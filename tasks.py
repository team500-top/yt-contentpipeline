import eventlet
eventlet.monkey_patch()

import os
import asyncio
from celery import Celery, Task
from celery.result import AsyncResult
from datetime import datetime
from typing import Dict, Any, List
import json

from database import SyncSessionLocal, get_sync_session
from models import Video, Task as TaskModel, Channel
from youtube_api import YouTubeClient
from analyzer import VideoAnalyzer

# Настройка Celery
celery_app = Celery(
    "youtube_analyzer",
    broker=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 час максимум на задачу
    task_soft_time_limit=3300,  # Мягкий лимит
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Класс для задач с сохранением состояния
class PausableTask(Task):
    """Базовый класс для задач с возможностью паузы"""
    
    def __init__(self):
        self._is_paused = False
        self._should_stop = False
    
    def pause(self):
        self._is_paused = True
    
    def resume(self):
        self._is_paused = False
    
    def stop(self):
        self._should_stop = True
    
    def check_pause(self):
        """Проверка паузы и ожидание возобновления"""
        while self._is_paused and not self._should_stop:
            import time
            time.sleep(1)
        
        if self._should_stop:
            raise Exception("Task was stopped")

# Вспомогательные функции
def update_task_progress(task_id: int, progress: float, processed: int, total: int, status: str = "running"):
    """Обновление прогресса задачи"""
    with next(get_sync_session()) as session:
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.progress = progress
            task.processed_items = processed
            task.total_items = total
            task.status = status
            session.commit()

def save_task_checkpoint(task_id: int, checkpoint_data: Dict[str, Any]):
    """Сохранение контрольной точки для возобновления"""
    with next(get_sync_session()) as session:
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.checkpoint = checkpoint_data
            session.commit()

# Основные задачи
@celery_app.task(bind=True, base=PausableTask, name="parse_youtube_search")
def parse_youtube_search(self, task_id: int, search_params: Dict[str, Any]):
    """Парсинг YouTube по поисковому запросу"""
    youtube = YouTubeClient()
    
    try:
        # Обновление статуса задачи
        update_task_progress(task_id, 0, 0, 0, "running")
        
        # Выполнение поиска
        query = search_params.get("query", "")
        max_results = search_params.get("maxResults", 50)
        video_type = search_params.get("videoType", "all")
        sort = search_params.get("sort", "relevance")
        
        # Асинхронный вызов в синхронном контексте
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        videos = loop.run_until_complete(
            youtube.search_videos(query, max_results, video_type, sort)
        )
        
        total_videos = len(videos)
        update_task_progress(task_id, 0, 0, total_videos, "running")
        
        # Обработка каждого видео
        processed = 0
        for i, video_data in enumerate(videos):
            # Проверка паузы
            self.check_pause()
            
            # Получение детальной информации о видео
            try:
                video_details = loop.run_until_complete(
                    youtube.get_video_details(video_data["video_id"])
                )
                
                # Сохранение в базу данных
                with next(get_sync_session()) as session:
                    # Проверка, существует ли видео
                    existing = session.query(Video).filter_by(
                        video_url=video_details["video_url"]
                    ).first()
                    
                    if not existing:
                        video = Video(
                            video_url=video_details["video_url"],
                            channel_url=video_details["channel_url"],
                            is_short=video_details["is_short"],
                            views=video_details["views"],
                            likes=video_details["likes"],
                            comments=video_details["comments"],
                            like_ratio=video_details["like_ratio"],
                            comment_ratio=video_details["comment_ratio"],
                            engagement_rate=video_details["engagement_rate"],
                            title=video_details["title"],
                            description=video_details["description"],
                            duration=video_details["duration"],
                            publish_date=datetime.fromisoformat(
                                video_details["publish_date"].replace("Z", "+00:00")
                            ),
                            thumbnail_url=video_details["thumbnail_url"],
                            video_category=video_details.get("video_category"),
                            video_quality=video_details.get("video_quality", "hd"),
                            has_cc=video_details.get("has_captions", False),
                            parse_status="completed"
                        )
                        session.add(video)
                        session.commit()
                
                processed += 1
                progress = (processed / total_videos) * 100
                update_task_progress(task_id, progress, processed, total_videos)
                
                # Сохранение контрольной точки
                save_task_checkpoint(task_id, {
                    "last_processed_index": i,
                    "video_ids": [v["video_id"] for v in videos],
                    "search_params": search_params
                })
                
            except Exception as e:
                print(f"Error processing video {video_data['video_id']}: {e}")
                continue
        
        # Завершение задачи
        update_task_progress(task_id, 100, processed, total_videos, "completed")
        
        return {
            "status": "success",
            "processed": processed,
            "total": total_videos
        }
        
    except Exception as e:
        update_task_progress(task_id, 0, 0, 0, "failed")
        raise

@celery_app.task(bind=True, base=PausableTask, name="parse_youtube_channel")
def parse_youtube_channel(self, task_id: int, channel_params: Dict[str, Any]):
    """Парсинг видео с YouTube канала"""
    youtube = YouTubeClient()
    
    try:
        update_task_progress(task_id, 0, 0, 0, "running")
        
        channel_url = channel_params.get("query", "")
        max_results = channel_params.get("maxResults", 50)
        video_type = channel_params.get("videoType", "all")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Получение информации о канале
        channel_id = youtube.extract_channel_id(channel_url)
        if channel_id:
            channel_info = loop.run_until_complete(
                youtube.get_channel_info(channel_id)
            )
            
            # Сохранение информации о канале
            with next(get_sync_session()) as session:
                channel, created = session.query(Channel).filter_by(
                    channel_id=channel_id
                ).first(), False
                
                if not channel:
                    channel = Channel(
                        channel_id=channel_id,
                        channel_url=channel_info["channel_url"],
                        title=channel_info["title"],
                        description=channel_info["description"],
                        subscriber_count=channel_info["subscriber_count"],
                        video_count=channel_info["video_count"],
                        view_count=channel_info["view_count"],
                        created_date=datetime.fromisoformat(
                            channel_info["created_date"].replace("Z", "+00:00")
                        ),
                        country=channel_info.get("country"),
                        thumbnail_url=channel_info["thumbnail_url"]
                    )
                    session.add(channel)
                    session.commit()
        
        # Получение видео с канала
        videos = loop.run_until_complete(
            youtube.get_channel_videos(channel_url, max_results, video_type)
        )
        
        total_videos = len(videos)
        update_task_progress(task_id, 0, 0, total_videos, "running")
        
        processed = 0
        for i, video_data in enumerate(videos):
            self.check_pause()
            
            try:
                video_details = loop.run_until_complete(
                    youtube.get_video_details(video_data["video_id"])
                )
                
                with next(get_sync_session()) as session:
                    existing = session.query(Video).filter_by(
                        video_url=video_details["video_url"]
                    ).first()
                    
                    if not existing:
                        video = Video(
                            video_url=video_details["video_url"],
                            channel_url=video_details["channel_url"],
                            is_short=video_details["is_short"],
                            views=video_details["views"],
                            likes=video_details["likes"],
                            comments=video_details["comments"],
                            like_ratio=video_details["like_ratio"],
                            comment_ratio=video_details["comment_ratio"],
                            engagement_rate=video_details["engagement_rate"],
                            title=video_details["title"],
                            description=video_details["description"],
                            duration=video_details["duration"],
                            publish_date=datetime.fromisoformat(
                                video_details["publish_date"].replace("Z", "+00:00")
                            ),
                            thumbnail_url=video_details["thumbnail_url"],
                            video_category=video_details.get("video_category"),
                            video_quality=video_details.get("video_quality", "hd"),
                            has_cc=video_details.get("has_captions", False),
                            channel_avg_views=channel_info.get("view_count", 0) / max(channel_info.get("video_count", 1), 1),
                            parse_status="completed"
                        )
                        session.add(video)
                        session.commit()
                
                processed += 1
                progress = (processed / total_videos) * 100
                update_task_progress(task_id, progress, processed, total_videos)
                
                save_task_checkpoint(task_id, {
                    "last_processed_index": i,
                    "video_ids": [v["video_id"] for v in videos],
                    "channel_params": channel_params
                })
                
            except Exception as e:
                print(f"Error processing video: {e}")
                continue
        
        update_task_progress(task_id, 100, processed, total_videos, "completed")
        
        return {
            "status": "success",
            "processed": processed,
            "total": total_videos,
            "channel_id": channel_id
        }
        
    except Exception as e:
        update_task_progress(task_id, 0, 0, 0, "failed")
        raise

@celery_app.task(bind=True, name="analyze_video_content")
def analyze_video_content(self, task_id: int, video_id: int):
    """Глубокий анализ контента видео"""
    try:
        update_task_progress(task_id, 0, 0, 1, "running")
        
        analyzer = VideoAnalyzer()
        
        with next(get_sync_session()) as session:
            video = session.query(Video).filter_by(id=video_id).first()
            if not video:
                raise ValueError("Video not found")
            
            # Анализ видео
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            analysis = loop.run_until_complete(
                analyzer.analyze_video(video)
            )
            
            # Сохранение результатов анализа
            video.top_5_keywords = analysis.get("keywords", [])[:5]
            video.improvement_recommendations = analysis.get("recommendations", "")
            video.success_analysis = analysis.get("success_analysis", "")
            video.content_strategy = analysis.get("strategy", "")
            video.has_branding = analysis.get("has_branding", False)
            video.has_intro = analysis.get("has_intro", False)
            video.has_outro = analysis.get("has_outro", False)
            video.speech_speed = analysis.get("speech_speed", 0)
            
            session.commit()
            
            update_task_progress(task_id, 100, 1, 1, "completed")
            
            return {
                "status": "success",
                "video_id": video_id,
                "analysis": analysis
            }
            
    except Exception as e:
        update_task_progress(task_id, 0, 0, 0, "failed")
        raise

# Управление задачами
def pause_task(celery_task_id: str):
    """Приостановка задачи"""
    task_result = AsyncResult(celery_task_id, app=celery_app)
    if hasattr(task_result, "pause"):
        task_result.pause()

def resume_task(celery_task_id: str):
    """Возобновление задачи"""
    task_result = AsyncResult(celery_task_id, app=celery_app)
    if hasattr(task_result, "resume"):
        task_result.resume()

def cancel_task(celery_task_id: str):
    """Отмена задачи"""
    celery_app.control.revoke(celery_task_id, terminate=True)

# Запуск Celery worker
def start_celery_worker():
    """Запуск Celery worker для Windows"""
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--pool=solo"  # Для Windows
    ])