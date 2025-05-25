# БЕЗ EVENTLET для Windows!
import os
import asyncio
import time
from celery import Celery, Task, current_task
from celery.result import AsyncResult
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

from database import get_sync_session
from models import Video, Task as TaskModel, Channel, SearchQuery
from youtube_api import YouTubeClient
from analyzer import VideoAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Celery
celery_app = Celery(
    "youtube_analyzer",
    broker=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
)

# Конфигурация Celery для Windows
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    # Важно для Windows!
    worker_pool="solo",
    broker_connection_retry_on_startup=True,
)

# Глобальный словарь для управления паузой задач
PAUSED_TASKS = {}

class PausableTask(Task):
    """Базовый класс для задач с возможностью паузы"""
    
    def __call__(self, *args, **kwargs):
        """Обертка для отслеживания состояния задачи"""
        task_id = self.request.id
        PAUSED_TASKS[task_id] = {"paused": False, "stopped": False}
        try:
            return self.run(*args, **kwargs)
        finally:
            # Очистка после завершения
            PAUSED_TASKS.pop(task_id, None)
    
    def check_pause(self):
        """Проверка паузы и ожидание возобновления"""
        task_id = self.request.id
        if task_id not in PAUSED_TASKS:
            return
            
        while PAUSED_TASKS[task_id]["paused"]:
            if PAUSED_TASKS[task_id]["stopped"]:
                raise Exception("Task was stopped")
            time.sleep(1)
        
        if PAUSED_TASKS[task_id]["stopped"]:
            raise Exception("Task was stopped")

# Вспомогательные функции
def update_task_progress(task_id: int, progress: float, processed: int, total: int, status: str = "running"):
    """Обновление прогресса задачи в БД"""
    session = next(get_sync_session())
    try:
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.progress = progress
            task.processed_items = processed
            task.total_items = total
            task.status = status
            if status == "running" and not task.started_at:
                task.started_at = datetime.now()
            elif status == "completed":
                task.completed_at = datetime.now()
            session.commit()
            logger.info(f"Task {task_id} progress: {progress:.1f}% ({processed}/{total})")
    finally:
        session.close()

def save_task_checkpoint(task_id: int, checkpoint_data: Dict[str, Any]):
    """Сохранение контрольной точки для возобновления"""
    session = next(get_sync_session())
    try:
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.checkpoint = checkpoint_data
            session.commit()
    finally:
        session.close()

def get_or_create_video(session, video_data: Dict[str, Any]) -> Optional[Video]:
    """Получение или создание видео в БД"""
    existing = session.query(Video).filter_by(
        video_url=video_data["video_url"]
    ).first()
    
    if existing:
        logger.info(f"Video already exists: {video_data['title']}")
        return None
    
    video = Video(
        video_url=video_data["video_url"],
        channel_url=video_data["channel_url"],
        is_short=video_data.get("is_short", False),
        views=video_data.get("views", 0),
        likes=video_data.get("likes", 0),
        comments=video_data.get("comments", 0),
        like_ratio=video_data.get("like_ratio", 0),
        comment_ratio=video_data.get("comment_ratio", 0),
        engagement_rate=video_data.get("engagement_rate", 0),
        title=video_data["title"],
        description=video_data.get("description", ""),
        duration=video_data.get("duration", ""),
        publish_date=datetime.fromisoformat(
            video_data["publish_date"].replace("Z", "+00:00")
        ) if video_data.get("publish_date") else datetime.now(),
        thumbnail_url=video_data.get("thumbnail_url", ""),
        video_category=video_data.get("video_category"),
        video_quality=video_data.get("video_quality", "hd"),
        has_cc=video_data.get("has_captions", False),
        parse_status="completed"
    )
    
    session.add(video)
    session.commit()
    logger.info(f"New video added: {video.title}")
    return video

# Основные задачи
@celery_app.task(bind=True, base=PausableTask, name="parse_youtube_search")
def parse_youtube_search(self, task_id: int, search_params: Dict[str, Any]):
    """Парсинг YouTube по поисковому запросу"""
    logger.info(f"Starting search task {task_id}: {search_params}")
    
    youtube = YouTubeClient()
    session = next(get_sync_session())
    
    try:
        # Обновление статуса задачи
        update_task_progress(task_id, 0, 0, 0, "running")
        
        # Параметры поиска
        query = search_params.get("query", "")
        max_results = search_params.get("maxResults", 50)
        video_type = search_params.get("videoType", "all")
        sort = search_params.get("sort", "relevance")
        
        # Создание нового event loop для async кода
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Выполнение поиска
            videos = loop.run_until_complete(
                youtube.search_videos(query, max_results, video_type, sort)
            )
            
            total_videos = len(videos)
            logger.info(f"Found {total_videos} videos for query: {query}")
            
            # Обновление общего количества
            update_task_progress(task_id, 0, 0, total_videos, "running")
            
            # Сохранение поискового запроса
            search_query = session.query(SearchQuery).filter_by(
                query=query,
                search_type="keyword"
            ).first()
            
            if not search_query:
                search_query = SearchQuery(
                    query=query,
                    search_type="keyword",
                    filters=search_params,
                    total_results=total_videos
                )
                session.add(search_query)
            else:
                search_query.total_results = total_videos
                search_query.last_searched = datetime.now()
            
            session.commit()
            
            # Обработка каждого видео
            processed = 0
            failed = 0
            
            for i, video_data in enumerate(videos):
                try:
                    # Проверка паузы
                    self.check_pause()
                    
                    # Получение детальной информации
                    logger.info(f"Processing video {i+1}/{total_videos}: {video_data['title']}")
                    
                    video_details = loop.run_until_complete(
                        youtube.get_video_details(video_data["video_id"])
                    )
                    
                    # Сохранение в БД
                    video = get_or_create_video(session, video_details)
                    if video:
                        processed += 1
                    
                    # Обновление прогресса
                    progress = ((i + 1) / total_videos) * 100
                    update_task_progress(task_id, progress, i + 1, total_videos)
                    
                    # Сохранение контрольной точки
                    save_task_checkpoint(task_id, {
                        "last_processed_index": i,
                        "processed": processed,
                        "failed": failed,
                        "video_ids": [v["video_id"] for v in videos],
                        "search_params": search_params
                    })
                    
                    # Небольшая задержка для избежания лимитов API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing video {video_data.get('video_id')}: {str(e)}")
                    failed += 1
                    continue
            
            # Обновление количества обработанных результатов
            search_query.parsed_results = processed
            session.commit()
            
            # Завершение задачи
            update_task_progress(task_id, 100, processed, total_videos, "completed")
            
            result = {
                "status": "success",
                "processed": processed,
                "failed": failed,
                "total": total_videos,
                "query": query
            }
            
            logger.info(f"Search task {task_id} completed: {result}")
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Search task {task_id} failed: {str(e)}")
        update_task_progress(task_id, 0, 0, 0, "failed")
        
        # Сохранение ошибки
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.error_message = str(e)
            session.commit()
        
        raise
    finally:
        session.close()

@celery_app.task(bind=True, base=PausableTask, name="parse_youtube_channel")
def parse_youtube_channel(self, task_id: int, channel_params: Dict[str, Any]):
    """Парсинг видео с YouTube канала"""
    logger.info(f"Starting channel parse task {task_id}: {channel_params}")
    
    youtube = YouTubeClient()
    session = next(get_sync_session())
    
    try:
        update_task_progress(task_id, 0, 0, 0, "running")
        
        channel_url = channel_params.get("query", "")
        max_results = channel_params.get("maxResults", 50)
        video_type = channel_params.get("videoType", "all")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Получение информации о канале
            channel_id = youtube.extract_channel_id(channel_url)
            if not channel_id:
                raise ValueError(f"Invalid channel URL: {channel_url}")
            
            logger.info(f"Extracted channel ID: {channel_id}")
            
            # Получение и сохранение информации о канале
            channel_info = loop.run_until_complete(
                youtube.get_channel_info(channel_id)
            )
            
            # Сохранение канала в БД
            channel = session.query(Channel).filter_by(
                channel_id=channel_id
            ).first()
            
            if not channel:
                channel = Channel(
                    channel_id=channel_id,
                    channel_url=channel_info["channel_url"],
                    title=channel_info["title"],
                    description=channel_info.get("description", ""),
                    subscriber_count=channel_info.get("subscriber_count", 0),
                    video_count=channel_info.get("video_count", 0),
                    view_count=channel_info.get("view_count", 0),
                    created_date=datetime.fromisoformat(
                        channel_info["created_date"].replace("Z", "+00:00")
                    ) if channel_info.get("created_date") else None,
                    country=channel_info.get("country"),
                    thumbnail_url=channel_info.get("thumbnail_url", ""),
                    last_parsed=datetime.now()
                )
                session.add(channel)
            else:
                # Обновление существующего канала
                channel.subscriber_count = channel_info.get("subscriber_count", 0)
                channel.video_count = channel_info.get("video_count", 0)
                channel.view_count = channel_info.get("view_count", 0)
                channel.last_parsed = datetime.now()
            
            session.commit()
            logger.info(f"Channel saved: {channel.title}")
            
            # Получение видео с канала
            videos = loop.run_until_complete(
                youtube.get_channel_videos(channel_url, max_results, video_type)
            )
            
            total_videos = len(videos)
            logger.info(f"Found {total_videos} videos on channel: {channel.title}")
            
            update_task_progress(task_id, 0, 0, total_videos, "running")
            
            # Обработка видео
            processed = 0
            failed = 0
            
            for i, video_data in enumerate(videos):
                try:
                    # Проверка паузы
                    self.check_pause()
                    
                    logger.info(f"Processing video {i+1}/{total_videos}: {video_data['title']}")
                    
                    # Получение детальной информации
                    video_details = loop.run_until_complete(
                        youtube.get_video_details(video_data["video_id"])
                    )
                    
                    # Дополнительные данные о канале
                    if channel_info.get("video_count", 0) > 0:
                        video_details["channel_avg_views"] = channel_info.get("view_count", 0) / channel_info.get("video_count", 1)
                    
                    # Сохранение видео
                    video = get_or_create_video(session, video_details)
                    if video:
                        processed += 1
                    
                    # Обновление прогресса
                    progress = ((i + 1) / total_videos) * 100
                    update_task_progress(task_id, progress, i + 1, total_videos)
                    
                    # Сохранение контрольной точки
                    save_task_checkpoint(task_id, {
                        "last_processed_index": i,
                        "processed": processed,
                        "failed": failed,
                        "video_ids": [v["video_id"] for v in videos],
                        "channel_params": channel_params,
                        "channel_id": channel_id
                    })
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing video: {str(e)}")
                    failed += 1
                    continue
            
            # Обновление статистики канала
            if channel and processed > 0:
                # Вычисление средних значений
                channel_videos = session.query(Video).filter_by(
                    channel_url=channel.channel_url
                ).all()
                
                if channel_videos:
                    channel.avg_views = sum(v.views for v in channel_videos) / len(channel_videos)
                    channel.avg_likes = sum(v.likes for v in channel_videos) / len(channel_videos)
                    channel.avg_comments = sum(v.comments for v in channel_videos) / len(channel_videos)
                    session.commit()
            
            # Завершение задачи
            update_task_progress(task_id, 100, processed, total_videos, "completed")
            
            result = {
                "status": "success",
                "processed": processed,
                "failed": failed,
                "total": total_videos,
                "channel_id": channel_id,
                "channel_name": channel.title if channel else "Unknown"
            }
            
            logger.info(f"Channel task {task_id} completed: {result}")
            return result
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Channel task {task_id} failed: {str(e)}")
        update_task_progress(task_id, 0, 0, 0, "failed")
        
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.error_message = str(e)
            session.commit()
        
        raise
    finally:
        session.close()

@celery_app.task(bind=True, name="analyze_video_content")
def analyze_video_content(self, task_id: int, video_id: int):
    """Глубокий анализ контента видео"""
    logger.info(f"Starting video analysis task {task_id} for video {video_id}")
    
    session = next(get_sync_session())
    
    try:
        update_task_progress(task_id, 0, 0, 1, "running")
        
        # Получение видео из БД
        video = session.query(Video).filter_by(id=video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        logger.info(f"Analyzing video: {video.title}")
        
        # Создание анализатора
        analyzer = VideoAnalyzer()
        
        # Запуск анализа
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            analysis = loop.run_until_complete(
                analyzer.analyze_video(video)
            )
            
            # Сохранение результатов анализа
            video.top_5_keywords = analysis.get("keywords", [])[:5]
            video.improvement_recommendations = analysis.get("recommendations", "")
            video.success_analysis = analysis.get("success_analysis", "")
            video.content_strategy = analysis.get("strategy", "")
            
            # Дополнительные параметры из анализа
            if "title_length" in analysis:
                video.emoji_in_title = analysis.get("has_emoji", False)
            
            if "has_clickbait" in analysis:
                video.has_branding = analysis.get("has_clickbait", False)
            
            if "has_timestamps" in analysis:
                video.has_chapters = analysis.get("has_timestamps", False)
            
            if "links_count" in analysis:
                video.links_in_description = analysis.get("links_count", 0)
            
            session.commit()
            logger.info(f"Analysis completed for video: {video.title}")
            
            update_task_progress(task_id, 100, 1, 1, "completed")
            
            return {
                "status": "success",
                "video_id": video_id,
                "title": video.title,
                "keywords": video.top_5_keywords,
                "recommendations": video.improvement_recommendations[:200] + "..." if len(video.improvement_recommendations) > 200 else video.improvement_recommendations
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Analysis task {task_id} failed: {str(e)}")
        update_task_progress(task_id, 0, 0, 0, "failed")
        
        task = session.query(TaskModel).filter_by(id=task_id).first()
        if task:
            task.error_message = str(e)
            session.commit()
        
        raise
    finally:
        session.close()

# Управление задачами
def pause_task(celery_task_id: str):
    """Приостановка задачи"""
    logger.info(f"Pausing task: {celery_task_id}")
    if celery_task_id in PAUSED_TASKS:
        PAUSED_TASKS[celery_task_id]["paused"] = True

def resume_task(celery_task_id: str):
    """Возобновление задачи"""
    logger.info(f"Resuming task: {celery_task_id}")
    if celery_task_id in PAUSED_TASKS:
        PAUSED_TASKS[celery_task_id]["paused"] = False

def cancel_task(celery_task_id: str):
    """Отмена задачи"""
    logger.info(f"Cancelling task: {celery_task_id}")
    if celery_task_id in PAUSED_TASKS:
        PAUSED_TASKS[celery_task_id]["stopped"] = True
    celery_app.control.revoke(celery_task_id, terminate=True)

# Для запуска воркера из командной строки
if __name__ == "__main__":
    import sys
    
    # Для Windows используем solo pool
    if sys.platform == "win32":
        celery_app.worker_main([
            "worker",
            "--loglevel=info",
            "--pool=solo",  # Важно для Windows!
            "--concurrency=1"
        ])
    else:
        celery_app.worker_main([
            "worker",
            "--loglevel=info",
            "--concurrency=2"
        ])