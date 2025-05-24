"""
YouTube Analyzer - API Services
Объединенные сервисы для работы с задачами, YouTube API, анализом и данными
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from typing import List, Dict, Optional
import uuid
import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

# Добавить пути для импорта
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from models import *
from database import DatabaseManager
from shared.config import settings
from shared.utils import Utils
from shared.youtube_parser import YouTubeParser

# Инициализация компонентов
db = DatabaseManager()
utils = Utils()
youtube_parser = YouTubeParser(settings.YOUTUBE_API_KEY) if settings.YOUTUBE_API_KEY else None

# Создание роутеров
tasks_router = APIRouter()
youtube_router = APIRouter()
analysis_router = APIRouter()
data_router = APIRouter()
config_router = APIRouter()

# Глобальное хранилище задач с персистентностью
active_tasks = {}

# Загрузка активных задач при старте
def load_active_tasks():
    """Загрузить активные задачи из БД"""
    global active_tasks
    try:
        tasks = db.get_all_tasks()
        for task in tasks:
            if task['status'] in ['running', 'paused', 'created']:
                active_tasks[task['task_id']] = task
        print(f"✅ Загружено {len(active_tasks)} активных задач")
    except Exception as e:
        print(f"❌ Ошибка загрузки задач: {e}")

# Загрузить при импорте
load_active_tasks()

# ============ TASKS SERVICE ============

@tasks_router.get("/", response_model=List[Dict])
async def get_tasks():
    """Получить список всех задач"""
    try:
        tasks = db.get_all_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения задач: {str(e)}")

@tasks_router.get("/active")
async def get_active_tasks():
    """Получить активные задачи в памяти"""
    return {
        "count": len(active_tasks),
        "tasks": list(active_tasks.values())
    }

@tasks_router.post("/", response_model=TaskCreateResponse)
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
    """Создать новую задачу анализа"""
    try:
        # Валидация
        if not task.keywords and not task.channels:
            raise HTTPException(status_code=400, detail="Укажите ключевые слова или каналы")
        
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API ключ не настроен")
        
        # Создание задачи
        task_id = str(uuid.uuid4())
        total_items = len(task.keywords) + len(task.channels)
        
        task_data = {
            "task_id": task_id,
            "status": "created",
            "progress": 0,
            "total_items": total_items,
            "created_at": datetime.now().isoformat(),
            "config": task.dict()
        }
        
        # Сохранить в БД
        db.save_task(task_data)
        active_tasks[task_id] = task_data
        
        # Запустить обработку в фоне
        background_tasks.add_task(process_task, task_id, task)
        
        return TaskCreateResponse(
            task_id=task_id,
            status=TaskStatus.CREATED,
            message="Задача создана и запущена"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания задачи: {str(e)}")

@tasks_router.get("/{task_id}")
async def get_task(task_id: str):
    """Получить статус конкретной задачи"""
    try:
        task = db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения задачи: {str(e)}")

@tasks_router.post("/{task_id}/pause")
async def pause_task(task_id: str):
    """Поставить задачу на паузу"""
    try:
        if task_id in active_tasks:
            active_tasks[task_id]["status"] = "paused"
            db.update_task_status(task_id, "paused")
            return {"message": "Задача поставлена на паузу", "status": "paused"}
        
        # Проверить в БД
        task = db.get_task(task_id)
        if task and task['status'] == 'running':
            db.update_task_status(task_id, "paused")
            return {"message": "Задача поставлена на паузу", "status": "paused"}
            
        raise HTTPException(status_code=404, detail="Активная задача не найдена")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка паузы задачи: {str(e)}")

@tasks_router.post("/{task_id}/resume")
async def resume_task(task_id: str, background_tasks: BackgroundTasks):
    """Возобновить задачу"""
    try:
        task = db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        if task['status'] == 'paused':
            # Обновить статус
            db.update_task_status(task_id, "running")
            active_tasks[task_id] = task
            active_tasks[task_id]["status"] = "running"
            
            # Возобновить обработку
            task_config = json.loads(task['config']) if isinstance(task['config'], str) else task['config']
            task_obj = TaskCreate(**task_config)
            background_tasks.add_task(process_task, task_id, task_obj, resume=True)
            
            return {"message": "Задача возобновлена", "status": "running"}
        else:
            raise HTTPException(status_code=400, detail=f"Задача не на паузе, текущий статус: {task['status']}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка возобновления задачи: {str(e)}")

async def process_task(task_id: str, task: TaskCreate, resume: bool = False):
    """Обработка задачи в фоновом режиме"""
    try:
        print(f"🔄 {'Возобновляем' if resume else 'Начинаем'} обработку задачи {task_id}")
        
        if not resume:
            active_tasks[task_id]["status"] = "running"
            db.update_task_status(task_id, "running")
        
        # Получить текущий прогресс
        current_task = db.get_task(task_id)
        processed = current_task['progress'] if current_task else 0
        total = len(task.keywords) + len(task.channels)
        
        # Обработка ключевых слов
        for idx, keyword in enumerate(task.keywords):
            # Пропустить уже обработанные
            if idx < processed and processed <= len(task.keywords):
                continue
                
            # Проверка паузы
            if task_id in active_tasks and active_tasks[task_id]["status"] == "paused":
                print(f"⏸️  Задача {task_id} на паузе")
                return
                
            print(f"🔍 Поиск видео по запросу: {keyword}")
            try:
                videos = youtube_parser.search_videos(
                    keyword, 
                    settings.MAX_LONG_VIDEOS_SEARCH + settings.MAX_SHORTS_SEARCH,
                    task.order_by.value
                )
                await process_videos(videos, task_id)
                
                # Обновить прогресс
                processed = idx + 1
                active_tasks[task_id]["progress"] = processed
                db.update_task_progress(task_id, processed, total)
                
                await asyncio.sleep(settings.REQUEST_DELAY)
                
            except Exception as e:
                print(f"❌ Ошибка обработки ключевого слова {keyword}: {e}")
                continue
        
        # Обработка каналов
        channel_start_idx = len(task.keywords)
        for idx, channel_url in enumerate(task.channels):
            # Пропустить уже обработанные
            if channel_start_idx + idx < processed:
                continue
                
            # Проверка паузы
            if task_id in active_tasks and active_tasks[task_id]["status"] == "paused":
                print(f"⏸️  Задача {task_id} на паузе")
                return
                
            print(f"📺 Анализ канала: {channel_url}")
            try:
                channel_id = youtube_parser.extract_channel_id(channel_url)
                if channel_id:
                    # Получить информацию о канале
                    channel_info = youtube_parser.get_channel_info(channel_id)
                    if channel_info:
                        db.save_channel(channel_info)
                    
                    # Получить видео канала
                    videos = youtube_parser.get_channel_videos(
                        channel_id, 
                        settings.MAX_LONG_VIDEOS_CHANNEL + settings.MAX_SHORTS_CHANNEL
                    )
                    await process_videos(videos, task_id)
                
                # Обновить прогресс
                processed = channel_start_idx + idx + 1
                active_tasks[task_id]["progress"] = processed
                db.update_task_progress(task_id, processed, total)
                
                await asyncio.sleep(settings.REQUEST_DELAY)
                
            except Exception as e:
                print(f"❌ Ошибка обработки канала {channel_url}: {e}")
                continue
        
        # Завершение задачи
        active_tasks[task_id]["status"] = "completed"
        db.update_task_status(task_id, "completed")
        
        # Удалить из активных
        if task_id in active_tasks:
            del active_tasks[task_id]
            
        print(f"✅ Задача {task_id} завершена")
        
    except Exception as e:
        print(f"❌ Критическая ошибка в задаче {task_id}: {e}")
        if task_id in active_tasks:
            active_tasks[task_id]["status"] = "error"
        db.update_task_status(task_id, "error", str(e))

async def process_videos(videos: List[Dict], task_id: str):
    """Обработка списка видео с транскрибацией"""
    for video in videos:
        try:
            video_id = video.get('video_id')
            if not video_id or db.video_exists(video_id):
                continue
            
            print(f"  📹 Обработка видео: {video.get('title', 'Unknown')[:50]}...")
            
            # Добавить метаданные
            video['analyzed_at'] = datetime.now().isoformat()
            video['task_id'] = task_id
            
            # Попытка получить транскрипт
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                
                # Попробовать получить субтитры
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Приоритет: русские -> английские -> любые
                transcript = None
                try:
                    transcript = transcript_list.find_transcript(['ru'])
                except:
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except:
                        # Берем первый доступный
                        for t in transcript_list:
                            transcript = t
                            break
                
                if transcript:
                    transcript_text = ' '.join([entry['text'] for entry in transcript.fetch()])
                    video['transcript'] = transcript_text[:50000]  # Ограничение длины
                    video['transcript_source'] = f"youtube_{transcript.language_code}"
                    print(f"    ✅ Транскрипт получен ({transcript.language_code})")
                    
                    # Анализ транскрипта
                    if transcript_text:
                        # Извлечение ключевых слов
                        video['keywords'] = utils.extract_keywords(transcript_text, top_n=10)
                        
                        # Анализ скорости речи (слов в минуту)
                        word_count = len(transcript_text.split())
                        duration_seconds = video.get('duration_seconds', 0)
                        if duration_seconds > 0:
                            video['speech_speed'] = round((word_count / duration_seconds) * 60, 1)
                        
                        # Проверка на рекламу
                        ad_keywords = ['спонсор', 'реклама', 'промокод', 'скидка', 'sponsor', 'promo', 'discount']
                        video['has_branding'] = any(keyword in transcript_text.lower() for keyword in ad_keywords)
                        
            except Exception as e:
                print(f"    ⚠️  Не удалось получить транскрипт: {e}")
                
                # Если нет субтитров и видео короткое, можно попробовать Whisper
                if video.get('duration_seconds', 0) < 600:  # Менее 10 минут
                    print(f"    🎤 Попытка транскрибации через Whisper...")
                    # TODO: Добавить Whisper транскрибацию
                    video['transcript_source'] = 'none'
            
            # Базовый анализ
            if 'engagement_rate' not in video and video.get('views', 0) > 0:
                video['engagement_rate'] = utils.calculate_engagement_rate(
                    video.get('views', 0),
                    video.get('likes', 0),
                    video.get('comments', 0)
                )
            
            # Анализ заголовка
            title = video.get('title', '')
            video['title_length'] = len(title)
            video['has_emoji'] = utils.has_emoji(title)
            
            # Анализ описания
            description = video.get('description', '')
            video['description_length'] = len(description)
            video['links_count'] = utils.count_links(description)
            
            # Рекомендации на основе анализа
            recommendations = []
            
            if video.get('engagement_rate', 0) < 1:
                recommendations.append("Низкая вовлеченность. Рекомендуется улучшить заголовок и превью.")
            elif video.get('engagement_rate', 0) > 5:
                recommendations.append("Отличная вовлеченность! Изучите факторы успеха этого видео.")
            
            if video.get('is_short') and video.get('views', 0) > 10000:
                recommendations.append("Успешный Short! Создайте больше контента в этом формате.")
            
            if not video.get('has_cc'):
                recommendations.append("Добавьте субтитры для увеличения охвата аудитории.")
            
            if video.get('speech_speed', 0) > 180:
                recommendations.append("Высокая скорость речи. Может быть сложно для восприятия.")
            
            video['recommendations'] = ' '.join(recommendations)
            
            # Анализ успеха
            success_factors = []
            if video.get('has_emoji'):
                success_factors.append("Использование эмодзи в заголовке")
            if video.get('duration_seconds', 0) < 60:
                success_factors.append("Формат Shorts")
            if video.get('engagement_rate', 0) > 3:
                success_factors.append("Высокая вовлеченность аудитории")
            
            video['success_analysis'] = ', '.join(success_factors) if success_factors else "Стандартное видео"
            
            # Сохранить в БД
            db.save_video(video)
            print(f"    ✅ Видео сохранено в БД")
            
        except Exception as e:
            print(f"  ❌ Ошибка обработки видео {video.get('video_id', 'unknown')}: {e}")
            continue

# ============ YOUTUBE SERVICE ============

@youtube_router.get("/search")
async def search_videos(query: str, max_results: int = 10, order: str = "relevance"):
    """Поиск видео по запросу"""
    try:
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API не настроен")
        
        videos = youtube_parser.search_videos(query, max_results, order)
        return {
            "videos": videos, 
            "count": len(videos),
            "query": query,
            "order": order
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")

@youtube_router.get("/channel/{channel_id}")
async def get_channel_info(channel_id: str):
    """Получить информацию о канале"""
    try:
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API не настроен")
        
        channel_info = youtube_parser.get_channel_info(channel_id)
        if not channel_info:
            raise HTTPException(status_code=404, detail="Канал не найден")
            
        return channel_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения канала: {str(e)}")

@youtube_router.get("/channel/{channel_id}/videos")
async def get_channel_videos(channel_id: str, max_results: int = 20):
    """Получить видео канала"""
    try:
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API не настроен")
        
        videos = youtube_parser.get_channel_videos(channel_id, max_results)
        return {
            "channel_id": channel_id,
            "videos": videos,
            "count": len(videos)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения видео канала: {str(e)}")

# ============ DATA SERVICE ============

@data_router.get("/videos")
async def get_videos(limit: int = 100, offset: int = 0):
    """Получить список проанализированных видео"""
    try:
        videos = db.get_videos(limit, offset)
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения видео: {str(e)}")

@data_router.get("/videos/{video_id}")
async def get_video_details(video_id: str):
    """Получить детальную информацию о видео"""
    try:
        video = db.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Видео не найдено")
        return video
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения видео: {str(e)}")

@data_router.get("/channels")
async def get_channels():
    """Получить список проанализированных каналов"""
    try:
        channels = db.get_channels()
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения каналов: {str(e)}")

@data_router.get("/channels/{channel_id}")
async def get_channel_details(channel_id: str):
    """Получить детальную информацию о канале"""
    try:
        channel = db.get_channel_stats(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Канал не найден")
        return channel
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения канала: {str(e)}")

@data_router.get("/stats")
async def get_statistics():
    """Получить общую статистику"""
    try:
        stats = db.get_statistics()
        stats['active_tasks'] = len(active_tasks)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@data_router.get("/export")
async def export_to_excel():
    """Экспорт данных в Excel"""
    try:
        filename = db.export_to_excel()
        file_path = Path(settings.EXPORT_DIR) / filename
        
        return {
            "filename": filename,
            "status": "exported",
            "path": str(file_path),
            "size": file_path.stat().st_size if file_path.exists() else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта: {str(e)}")

@data_router.delete("/clear")
async def clear_database():
    """Очистить базу данных"""
    try:
        # Очистить активные задачи
        active_tasks.clear()
        
        # Очистить БД
        db.clear_database()
        
        return {"message": "База данных очищена", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки БД: {str(e)}")

# ============ CONFIG SERVICE ============

@config_router.get("/")
async def get_config():
    """Получить текущую конфигурацию"""
    try:
        config = settings.get_safe_dict()
        config['has_youtube_api'] = bool(settings.YOUTUBE_API_KEY)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения конфигурации: {str(e)}")

@config_router.post("/")
async def update_config(config_data: dict):
    """Обновить конфигурацию"""
    try:
        # Обновить настройки
        settings.update_from_dict(config_data)
        
        # Пересоздать YouTube parser если изменился API ключ
        global youtube_parser
        if 'youtube_api_key' in config_data and config_data['youtube_api_key']:
            if config_data['youtube_api_key'] != '***':  # Не обновлять если скрыто
                settings.YOUTUBE_API_KEY = config_data['youtube_api_key']
                youtube_parser = YouTubeParser(config_data['youtube_api_key'])
        
        return {
            "message": "Конфигурация обновлена",
            "status": "success",
            "config": settings.get_safe_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления конфигурации: {str(e)}")

@config_router.post("/validate-api-key")
async def validate_api_key(api_key: str):
    """Проверить YouTube API ключ"""
    try:
        # Попробовать создать парсер и сделать тестовый запрос
        test_parser = YouTubeParser(api_key)
        test_videos = test_parser.search_videos("test", 1)
        
        return {
            "valid": True,
            "message": "API ключ валидный"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Ошибка API ключа: {str(e)}"
        }

# ============ ANALYSIS SERVICE ============

@analysis_router.post("/video/{video_id}")
async def analyze_video(video_id: str):
    """Провести анализ конкретного видео"""
    try:
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API не настроен")
        
        # Получить данные видео
        details = youtube_parser.get_video_details([video_id])
        if video_id not in details:
            raise HTTPException(status_code=404, detail="Видео не найдено")
        
        video_data = details[video_id]
        
        # Провести анализ
        analysis_result = {
            "video_id": video_id,
            "engagement_metrics": {
                "views": video_data.get('views', 0),
                "likes": video_data.get('likes', 0),
                "comments": video_data.get('comments', 0),
                "engagement_rate": video_data.get('engagement_rate', 0),
                "like_ratio": video_data.get('like_ratio', 0),
                "comment_ratio": video_data.get('comment_ratio', 0)
            },
            "content_analysis": {
                "duration": video_data.get('duration'),
                "is_short": video_data.get('is_short', False),
                "has_cc": video_data.get('has_cc', False),
                "tags_count": len(video_data.get('tags', [])),
                "video_quality": video_data.get('video_quality', 'sd')
            },
            "recommendations": [
                "Анализ завершен успешно",
                f"Вовлеченность: {'Высокая' if video_data.get('engagement_rate', 0) > 5 else 'Средняя' if video_data.get('engagement_rate', 0) > 2 else 'Низкая'}"
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
        # Сохранить в БД если не существует
        if not db.video_exists(video_id):
            video_data['analyzed_at'] = datetime.now().isoformat()
            db.save_video(video_data)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа видео: {str(e)}")

@analysis_router.post("/bulk")
async def analyze_bulk(video_urls: List[str], background_tasks: BackgroundTasks):
    """Массовый анализ видео"""
    try:
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API не настроен")
        
        # Извлечь video_ids
        video_ids = []
        for url in video_urls:
            video_id = utils.extract_video_id_from_url(url)
            if video_id:
                video_ids.append(video_id)
        
        if not video_ids:
            raise HTTPException(status_code=400, detail="Не найдено валидных video ID")
        
        # Создать задачу для анализа
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "task_type": "bulk_analysis",
            "status": "created",
            "progress": 0,
            "total_items": len(video_ids),
            "config": {"video_ids": video_ids}
        }
        
        db.save_task(task_data)
        active_tasks[task_id] = task_data
        
        # Запустить анализ в фоне
        background_tasks.add_task(process_bulk_analysis, task_id, video_ids)
        
        return {
            "task_id": task_id,
            "video_count": len(video_ids),
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка массового анализа: {str(e)}")

async def process_bulk_analysis(task_id: str, video_ids: List[str]):
    """Обработка массового анализа"""
    try:
        active_tasks[task_id]["status"] = "running"
        db.update_task_status(task_id, "running")
        
        for idx, video_id in enumerate(video_ids):
            if task_id in active_tasks and active_tasks[task_id]["status"] == "paused":
                return
            
            try:
                details = youtube_parser.get_video_details([video_id])
                if video_id in details:
                    video_data = details[video_id]
                    video_data['analyzed_at'] = datetime.now().isoformat()
                    video_data['task_id'] = task_id
                    db.save_video(video_data)
                
                # Обновить прогресс
                active_tasks[task_id]["progress"] = idx + 1
                db.update_task_progress(task_id, idx + 1, len(video_ids))
                
                await asyncio.sleep(settings.REQUEST_DELAY)
                
            except Exception as e:
                print(f"Ошибка анализа видео {video_id}: {e}")
                continue
        
        active_tasks[task_id]["status"] = "completed"
        db.update_task_status(task_id, "completed")
        
    except Exception as e:
        active_tasks[task_id]["status"] = "error"
        db.update_task_status(task_id, "error", str(e))

print("✅ Все сервисы загружены успешно")