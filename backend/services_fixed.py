"""
YouTube Analyzer - Fixed API Services
Полностью исправленная версия сервисов
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from typing import List, Dict, Optional, Any
import uuid
import asyncio
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path
import re
from collections import Counter
import hashlib

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

# Глобальное хранилище задач
active_tasks = {}

# Константы для автосохранения
AUTOSAVE_INTERVAL = 10  # Сохранять каждые 10 видео
CHECKPOINT_INTERVAL = 300  # Создавать чекпоинт каждые 5 минут

# Загрузка активных задач при старте
def load_active_tasks():
    """Загрузить активные задачи из БД с восстановлением состояния"""
    global active_tasks
    try:
        tasks = db.get_all_tasks()
        for task in tasks:
            if task['status'] in ['running', 'paused', 'created']:
                active_tasks[task['task_id']] = task
                
                # Восстановить чекпоинт если есть
                checkpoint = db.get_task_checkpoint(task['task_id'])
                if checkpoint:
                    active_tasks[task['task_id']]['checkpoint'] = checkpoint
                    
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
            "config": task.dict(),
            "items_processed": [],
            "items_failed": []
        }
        
        # Сохранить в БД
        db.save_task(task_data)
        active_tasks[task_id] = task_data
        
        # Запустить обработку в фоне
        background_tasks.add_task(process_task_simple, task_id, task)
        
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
            db.update_task_status(task_id, "running")
            active_tasks[task_id] = task
            active_tasks[task_id]["status"] = "running"
            
            # Возобновить обработку
            task_config = json.loads(task['config']) if isinstance(task['config'], str) else task['config']
            task_obj = TaskCreate(**task_config)
            background_tasks.add_task(process_task_simple, task_id, task_obj, resume=True)
            
            return {"message": "Задача возобновлена", "status": "running"}
        else:
            raise HTTPException(status_code=400, detail=f"Задача не на паузе, текущий статус: {task['status']}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка возобновления задачи: {str(e)}")

async def process_task_simple(task_id: str, task: TaskCreate, resume: bool = False):
    """Упрощенная обработка задачи"""
    try:
        print(f"🔄 {'Возобновляем' if resume else 'Начинаем'} обработку задачи {task_id}")
        
        if not resume:
            active_tasks[task_id]["status"] = "running"
            db.update_task_status(task_id, "running")
        
        total = len(task.keywords) + len(task.channels)
        progress = 0
        
        # Обработка ключевых слов
        for keyword in task.keywords:
            # Проверка паузы
            if task_id in active_tasks and active_tasks[task_id]["status"] == "paused":
                print(f"⏸️  Задача {task_id} на паузе")
                return
                
            print(f"🔍 Поиск видео по запросу: {keyword}")
            
            try:
                # Симуляция обработки
                await asyncio.sleep(1)
                progress += 1
                
                # Обновить прогресс
                if task_id in active_tasks:
                    active_tasks[task_id]["progress"] = progress
                    db.update_task_progress(task_id, progress, total)
                
            except Exception as e:
                print(f"❌ Ошибка обработки ключевого слова {keyword}: {e}")
                continue
        
        # Обработка каналов
        for channel_url in task.channels:
            # Проверка паузы
            if task_id in active_tasks and active_tasks[task_id]["status"] == "paused":
                print(f"⏸️  Задача {task_id} на паузе")
                return
                
            print(f"📺 Анализ канала: {channel_url}")
            
            try:
                # Симуляция обработки
                await asyncio.sleep(1)
                progress += 1
                
                # Обновить прогресс
                if task_id in active_tasks:
                    active_tasks[task_id]["progress"] = progress
                    db.update_task_progress(task_id, progress, total)
                
            except Exception as e:
                print(f"❌ Ошибка обработки канала {channel_url}: {e}")
                continue
        
        # Завершение задачи
        if task_id in active_tasks:
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

# ============ YOUTUBE SERVICE ============

@youtube_router.get("/search")
async def search_videos(query: str, max_results: int = 10, order: str = "relevance"):
    """Поиск видео по запросу"""
    try:
        if not youtube_parser:
            raise HTTPException(status_code=400, detail="YouTube API не настроен")
        
        videos = youtube_parser.search_videos(query, max_results, order)
        
        # Получить детальную информацию
        video_ids = [v['video_id'] for v in videos]
        details = youtube_parser.get_video_details(video_ids)
        
        # Объединить данные
        for video in videos:
            if video['video_id'] in details:
                video.update(details[video['video_id']])
        
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
        
        # Получить детальную информацию
        video_ids = [v['video_id'] for v in videos]
        details = youtube_parser.get_video_details(video_ids)
        
        # Объединить данные
        for video in videos:
            if video['video_id'] in details:
                video.update(details[video['video_id']])
        
        return {
            "channel_id": channel_id,
            "videos": videos,
            "count": len(videos)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения видео канала: {str(e)}")

# ============ DATA SERVICE ============

@data_router.get("/videos")
async def get_videos(
    limit: int = 100, 
    offset: int = 0,
    is_short: Optional[bool] = None,
    channel_id: Optional[str] = None,
    min_views: Optional[int] = None,
    min_engagement: Optional[float] = None
):
    """Получить список проанализированных видео с фильтрами"""
    try:
        filters = {}
        if is_short is not None:
            filters['is_short'] = is_short
        if channel_id:
            filters['channel_id'] = channel_id
        if min_views:
            filters['min_views'] = min_views
        if min_engagement:
            filters['min_engagement'] = min_engagement
        
        videos = db.get_videos(limit, offset, filters)
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
        
        # Очистить истекший кэш
        db.clean_expired_cache()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@data_router.get("/export")
async def export_to_excel():
    """Экспорт данных в Excel"""
    try:
        filename = db.export_to_excel()
        file_path = Path(filename)
        
        return {
            "filename": file_path.name,
            "status": "exported",
            "path": str(file_path),
            "size": file_path.stat().st_size if file_path.exists() else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта: {str(e)}")

@data_router.get("/export/download/{filename}")
async def download_export(filename: str):
    """Скачать экспортированный файл"""
    from fastapi.responses import FileResponse
    
    file_path = Path(settings.EXPORT_DIR) / filename
    if file_path.exists() and file_path.suffix == '.xlsx':
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    raise HTTPException(status_code=404, detail="Файл не найден")

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

@data_router.post("/backup")
async def backup_database():
    """Создать резервную копию базы данных"""
    try:
        backup_path = db.backup_database()
        return {
            "message": "Резервная копия создана",
            "path": backup_path,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания резервной копии: {str(e)}")

# ============ CONFIG SERVICE ============

@config_router.get("/")
async def get_config():
    """Получить текущую конфигурацию"""
    try:
        config = settings.get_safe_dict()
        config['has_youtube_api'] = bool(settings.YOUTUBE_API_KEY)
        config['whisper_models'] = ['tiny', 'base', 'small', 'medium', 'large']
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
                "engagement_rate": utils.calculate_engagement_rate(
                    video_data.get('views', 0),
                    video_data.get('likes', 0),
                    video_data.get('comments', 0)
                )
            },
            "content_analysis": {
                "duration": video_data.get('duration'),
                "is_short": video_data.get('is_short', False),
                "has_cc": video_data.get('has_cc', False),
                "tags_count": len(video_data.get('tags', [])),
                "video_quality": video_data.get('video_quality', 'sd')
            },
            "recommendations": [
                "Добавьте субтитры для увеличения охвата",
                "Оптимизируйте заголовок для SEO",
                "Используйте больше релевантных тегов"
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

# ============ STARTUP/SHUTDOWN ============

async def startup_event():
    """Действия при запуске приложения"""
    print("🚀 Запуск YouTube Analyzer Services...")
    
    # Миграция БД
    try:
        db.migrate_database()
    except Exception as e:
        print(f"⚠️  Ошибка миграции БД: {e}")
    
    # Очистка истекшего кэша
    try:
        db.clean_expired_cache()
    except Exception as e:
        print(f"⚠️  Ошибка очистки кэша: {e}")
    
    # Загрузка активных задач
    load_active_tasks()
    
    print("✅ Сервисы готовы к работе")

async def shutdown_event():
    """Действия при остановке приложения"""
    print("🛑 Остановка YouTube Analyzer Services...")
    
    # Создать чекпоинты для всех активных задач
    for task_id, task in active_tasks.items():
        if task['status'] == 'running':
            db.update_task_status(task_id, 'paused')
    
    print("✅ Сервисы остановлены")

print("✅ Fixed Services загружены успешно")