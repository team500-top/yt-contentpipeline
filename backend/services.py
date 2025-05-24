"""
YouTube Analyzer - Enhanced API Services
Расширенные сервисы с автосохранением и улучшенным анализом
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

# ============ ENHANCED ANALYSIS FUNCTIONS ============

async def analyze_video_extended(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """Расширенный анализ видео с дополнительными метриками"""
    
    # Базовые вычисления
    video_data['title_length'] = len(video_data.get('title', ''))
    video_data['description_length'] = len(video_data.get('description', ''))
    
    # Анализ заголовка
    title = video_data.get('title', '')
    video_data['emoji_in_title'] = utils.has_emoji(title)
    
    # Подсчет хэштегов
    description = video_data.get('description', '')
    video_data['hashtags_count'] = len(re.findall(r'#\w+', description))
    
    # Поиск упомянутых каналов
    mentioned = re.findall(r'@[\w-]+', description)
    video_data['mentioned_channels'] = mentioned[:10]  # Максимум 10
    
    # Анализ ссылок
    video_data['links_in_description'] = utils.count_links(description)
    
    # Поиск контактов
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, description)
    video_data['contacts_in_video'] = emails[:5]  # Максимум 5
    
    # SEO оценка (0-100)
    seo_score = 0
    if video_data.get('tags') and len(video_data['tags']) > 5:
        seo_score += 20
    if video_data['description_length'] > 200:
        seo_score += 20
    if video_data.get('has_cc'):
        seo_score += 20
    if video_data['hashtags_count'] > 0:
        seo_score += 10
    if video_data['title_length'] > 40 and video_data['title_length'] < 70:
        seo_score += 15
    if video_data['emoji_in_title']:
        seo_score += 5
    if video_data.get('thumbnail_url'):
        seo_score += 10
    
    video_data['seo_score'] = min(seo_score, 100)
    
    # Оценка кликабельности превью (0-100)
    thumbnail_score = 50  # Базовая оценка
    if video_data['emoji_in_title']:
        thumbnail_score += 10
    if '!' in title or '?' in title:
        thumbnail_score += 10
    if any(word in title.lower() for word in ['топ', 'лучший', 'секрет', 'быстро', 'просто']):
        thumbnail_score += 15
    if video_data.get('is_short'):
        thumbnail_score += 15
    
    video_data['thumbnail_click_score'] = min(thumbnail_score, 100)
    
    # Определение категории контента
    categories = {
        'education': ['урок', 'tutorial', 'обучение', 'гайд', 'guide', 'как сделать'],
        'entertainment': ['влог', 'vlog', 'пранк', 'челлендж', 'challenge', 'реакция'],
        'gaming': ['игра', 'game', 'прохождение', 'стрим', 'stream', 'геймплей'],
        'tech': ['обзор', 'review', 'технологии', 'гаджет', 'новинка', 'тест'],
        'music': ['клип', 'песня', 'music', 'song', 'кавер', 'cover'],
        'news': ['новости', 'news', 'события', 'breaking', 'срочно']
    }
    
    detected_category = 'other'
    title_lower = title.lower()
    for category, keywords in categories.items():
        if any(keyword in title_lower for keyword in keywords):
            detected_category = category
            break
    
    video_data['video_category'] = detected_category
    
    # Генерация рекомендаций по улучшению
    improvements = []
    
    if not video_data.get('has_cc'):
        improvements.append("Добавьте субтитры для увеличения охвата")
    
    if video_data['engagement_rate'] < 2:
        improvements.append("Низкая вовлеченность - улучшите заголовок и превью")
    
    if video_data['description_length'] < 100:
        improvements.append("Слишком короткое описание - добавьте больше деталей и ключевых слов")
    
    if not video_data.get('tags') or len(video_data['tags']) < 5:
        improvements.append("Добавьте больше тегов (минимум 10)")
    
    if not video_data['emoji_in_title'] and detected_category in ['entertainment', 'gaming']:
        improvements.append("Добавьте эмодзи в заголовок для привлечения внимания")
    
    if video_data['title_length'] > 70:
        improvements.append("Сократите заголовок до 60-70 символов")
    
    if video_data['hashtags_count'] == 0:
        improvements.append("Добавьте 3-5 релевантных хэштегов")
    
    video_data['improvement_suggestions'] = improvements[:5]
    
    # Стратегия контента
    strategy_parts = []
    
    if video_data.get('is_short'):
        strategy_parts.append("Shorts формат работает хорошо - продолжайте")
    else:
        if video_data.get('duration_seconds', 0) > 600:
            strategy_parts.append("Рассмотрите создание коротких версий для Shorts")
    
    if video_data['engagement_rate'] > 5:
        strategy_parts.append("Высокая вовлеченность - изучите и повторите успешные элементы")
    
    if detected_category == 'education':
        strategy_parts.append("Образовательный контент - создайте серию уроков")
    
    video_data['content_strategy'] = '. '.join(strategy_parts)
    
    # Примерная оценка дохода (очень приблизительно)
    if video_data.get('views', 0) > 0:
        # $1-3 за 1000 просмотров в среднем
        cpm = 2.0  # Средний CPM
        if detected_category in ['education', 'tech']:
            cpm = 3.0
        elif detected_category in ['gaming', 'entertainment']:
            cpm = 1.5
        
        estimated_revenue = (video_data['views'] / 1000) * cpm
        video_data['estimated_revenue'] = round(estimated_revenue, 2)
    
    return video_data

async def analyze_channel_extended(channel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Расширенный анализ канала"""
    
    channel_id = channel_data['channel_id']
    
    # Вычислить частоту загрузок
    upload_frequency = db.get_channel_upload_frequency(channel_id)
    channel_data['upload_frequency'] = round(upload_frequency, 2)
    
    # Определить тип канала
    if channel_data.get('video_count', 0) > 100:
        channel_data['channel_type'] = 'media'
    elif channel_data.get('subscriber_count', 0) > 100000:
        channel_data['channel_type'] = 'brand'
    else:
        channel_data['channel_type'] = 'personal'
    
    # Оценка роста (приблизительно)
    if upload_frequency > 0:
        # Предполагаем рост на основе частоты загрузок и вовлеченности
        growth_factor = upload_frequency * 0.1
        if channel_data.get('avg_engagement_rate', 0) > 5:
            growth_factor *= 1.5
        channel_data['growth_rate'] = round(growth_factor, 2)
    
    # Примерная оценка месячного дохода
    if channel_data.get('avg_views', 0) > 0 and upload_frequency > 0:
        monthly_views = channel_data['avg_views'] * upload_frequency
        cpm = 2.0  # Средний CPM
        channel_data['estimated_monthly_revenue'] = round((monthly_views / 1000) * cpm, 2)
    
    return channel_data

# ============ TASKS SERVICE WITH CHECKPOINTS ============

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
        background_tasks.add_task(process_task_with_checkpoints, task_id, task)
        
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
    """Поставить задачу на паузу с сохранением состояния"""
    try:
        if task_id in active_tasks:
            # Создать чекпоинт перед паузой
            checkpoint_data = {
                'status': 'paused',
                'progress': active_tasks[task_id].get('progress', 0),
                'timestamp': datetime.now().isoformat(),
                'active_items': active_tasks[task_id].get('active_items', [])
            }
            
            db.save_task_checkpoint(task_id, checkpoint_data)
            
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
    """Возобновить задачу с последнего чекпоинта"""
    try:
        task = db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        if task['status'] == 'paused':
            # Получить чекпоинт
            checkpoint = db.get_task_checkpoint(task_id)
            
            # Обновить статус
            db.update_task_status(task_id, "running")
            active_tasks[task_id] = task
            active_tasks[task_id]["status"] = "running"
            
            if checkpoint:
                active_tasks[task_id]["checkpoint"] = checkpoint
            
            # Возобновить обработку
            task_config = json.loads(task['config']) if isinstance(task['config'], str) else task['config']
            task_obj = TaskCreate(**task_config)
            background_tasks.add_task(process_task_with_checkpoints, task_id, task_obj, resume=True)
            
            return {"message": "Задача возобновлена", "status": "running"}
        else:
            raise HTTPException(status_code=400, detail=f"Задача не на паузе, текущий статус: {task['status']}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка возобновления задачи: {str(e)}")

async def process_task_with_checkpoints(task_id: str, task: TaskCreate, resume: bool = False):
    """Обработка задачи с автосохранением и чекпоинтами"""
    try:
        print(f"🔄 {'Возобновляем' if resume else 'Начинаем'} обработку задачи {task_id}")
        
        if not resume:
            active_tasks[task_id]["status"] = "running"
            db.update_task_status(task_id, "running")
        
        # Получить текущий прогресс
        current_task = db.get_task(task_id)
        checkpoint = db.get_task_checkpoint(task_id) if resume else None
        

    except Exception as e:
        print(f'Ошибка: {e}')
        pass
items_processed_data = current_task.get('items_processed', '[]')
items_failed_data = current_task.get('items_failed', '[]')

# Проверяем тип данных перед парсингом
if isinstance(items_processed_data, str):
    processed_items = set(json.loads(items_processed_data))
elif isinstance(items_processed_data, list):
    processed_items = set(items_processed_data)
else:
    processed_items = set()

if isinstance(items_failed_data, str):
    failed_items = set(json.loads(items_failed_data))
elif isinstance(items_failed_data, list):
    failed_items = set(items_failed_data)
else:
    failed_items = set()

      
        # Восстановить прогресс из чекпоинта
        if checkpoint and 'processed_items' in checkpoint:
            processed_items.update(checkpoint['processed_items'])
        
        total = len(task.keywords) + len(task.channels)
        last_checkpoint_time = datetime.now()
        
        # Обработка ключевых слов
        for idx, keyword in enumerate(task.keywords):
            # Проверка на уже обработанные
            item_id = f"keyword:{keyword}"
            if item_id in processed_items:
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
                
                await process_videos_extended(videos, task_id)
                
                # Отметить как обработанный
                processed_items.add(item_id)
                
                # Обновить прогресс
                progress = len(processed_items)
                active_tasks[task_id]["progress"] = progress
                
                # Автосохранение
                if len(processed_items) % AUTOSAVE_INTERVAL == 0:
                    db.update_task_progress_extended(
                        task_id, progress, total,
                        list(processed_items), list(failed_items)
                    )
                
                # Чекпоинт каждые N минут
                if (datetime.now() - last_checkpoint_time).seconds > CHECKPOINT_INTERVAL:
                    checkpoint_data = {
                        'processed_items': list(processed_items),
                        'failed_items': list(failed_items),
                        'current_keyword': keyword,
                        'progress': progress
                    }
                    db.save_task_checkpoint(task_id, checkpoint_data)
                    last_checkpoint_time = datetime.now()
                
                await asyncio.sleep(settings.REQUEST_DELAY)
                
            except Exception as e:
                print(f"❌ Ошибка обработки ключевого слова {keyword}: {e}")
                failed_items.add(item_id)
                continue
        
        # Обработка каналов
        for idx, channel_url in enumerate(task.channels):
            # Проверка на уже обработанные
            item_id = f"channel:{channel_url}"
            if item_id in processed_items:
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
                        # Расширенный анализ канала
                        channel_info = await analyze_channel_extended(channel_info)
                        db.save_channel(channel_info)
                    
                    # Получить видео канала
                    videos = youtube_parser.get_channel_videos(
                        channel_id, 
                        settings.MAX_LONG_VIDEOS_CHANNEL + settings.MAX_SHORTS_CHANNEL
                    )
                    await process_videos_extended(videos, task_id)
                
                # Отметить как обработанный
                processed_items.add(item_id)
                
                # Обновить прогресс
                progress = len(processed_items)
                active_tasks[task_id]["progress"] = progress
                
                # Автосохранение
                if len(processed_items) % AUTOSAVE_INTERVAL == 0:
                    db.update_task_progress_extended(
                        task_id, progress, total,
                        list(processed_items), list(failed_items)
                    )
                
                await asyncio.sleep(settings.REQUEST_DELAY)
                
            except Exception as e:
                print(f"❌ Ошибка обработки канала {channel_url}: {e}")
                failed_items.add(item_id)
                continue
        
        # Финальное сохранение
        db.update_task_progress_extended(
            task_id, len(processed_items), total,
            list(processed_items), list(failed_items)
        )
        
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

async def process_videos_extended(videos: List[Dict], task_id: str):
    """Обработка видео с расширенным анализом и кэшированием"""
    for video in videos:
        try:
            video_id = video.get('video_id')
            if not video_id or db.video_exists(video_id):
                continue
            
            print(f"  📹 Обработка видео: {video.get('title', 'Unknown')[:50]}...")
            
            # Получить детальную информацию о видео
            details = youtube_parser.get_video_details([video_id])
            if video_id in details:
                video.update(details[video_id])
            
            # Добавить метаданные
            video['analyzed_at'] = datetime.now().isoformat()
            video['task_id'] = task_id
            
            # Проверить кэш транскриптов
            cached_transcript = db.get_cached_transcript(video_id)
            
            if cached_transcript:
                video['transcript'] = cached_transcript['transcript']
                video['transcript_source'] = f"cache_{cached_transcript['source']}"
                print(f"    ✅ Транскрипт загружен из кэша")
            else:
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
                        
                        # Кэшировать транскрипт
                        db.cache_transcript(
                            video_id, 
                            transcript_text, 
                            transcript.language_code,
                            'youtube'
                        )
                        
                except Exception as e:
                    print(f"    ⚠️  Не удалось получить транскрипт: {e}")
                    video['transcript_source'] = 'none'
            
            # Анализ транскрипта если есть
            if video.get('transcript'):
                transcript_text = video['transcript']
                
                # Извлечение ключевых слов
                video['keywords'] = utils.extract_keywords(transcript_text, top_n=10)
                video['top_5_keywords'] = video['keywords'][:5]
                
                # Анализ скорости речи (слов в минуту)
                word_count = len(transcript_text.split())
                duration_seconds = video.get('duration_seconds', 0)
                if duration_seconds > 0:
                    video['speech_speed'] = round((word_count / duration_seconds) * 60, 1)
                
                # Проверка на рекламу
                ad_keywords = ['спонсор', 'реклама', 'промокод', 'скидка', 'sponsor', 'promo', 'discount']
                video['has_branding'] = any(keyword in transcript_text.lower() for keyword in ad_keywords)
                
                # Анализ интро/аутро
                if duration_seconds > 30:
                    # Первые 10% текста
                    intro_text = transcript_text[:len(transcript_text)//10]
                    # Последние 10% текста
                    outro_text = transcript_text[-len(transcript_text)//10:]
                    
                    intro_patterns = ['привет', 'добро пожаловать', 'hello', 'welcome', 'всем привет']
                    outro_patterns = ['подписывайтесь', 'лайк', 'subscribe', 'like', 'пока', 'увидимся']
                    
                    video['has_intro'] = any(pattern in intro_text.lower() for pattern in intro_patterns)
                    video['has_outro'] = any(pattern in outro_text.lower() for pattern in outro_patterns)
            
            # Базовые метрики вовлеченности
            views = video.get('views', 0)
            likes = video.get('likes', 0)
            comments = video.get('comments', 0)
            
            if views > 0:
                video['like_ratio'] = utils.calculate_like_ratio(views, likes)
                video['comment_ratio'] = utils.calculate_comment_ratio(views, comments)
                video['engagement_rate'] = utils.calculate_engagement_rate(views, likes, comments)
            else:
                video['like_ratio'] = 0
                video['comment_ratio'] = 0
                video['engagement_rate'] = 0
            
            # Расширенный анализ
            video = await analyze_video_extended(video)
            
            # Сохранить в БД
            db.save_video(video)
            print(f"    ✅ Видео сохранено в БД")
            
            # Анализ трендов по ключевым словам
            if video.get('keywords'):
                for keyword in video['keywords'][:3]:  # Топ 3 ключевых слова
                    trend_data = {
                        'video_count': 1,
                        'avg_views': views,
                        'avg_engagement': video['engagement_rate'],
                        'top_channels': [video.get('channel_title', '')],
                        'trending_topics': video.get('tags', [])[:5]
                    }
                    db.save_trend_analysis(keyword, trend_data)
            
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
        
        # Расширенный анализ
        channel_info = await analyze_channel_extended(channel_info)
        
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
        
        # Расширенный анализ
        video_data = await analyze_video_extended(video_data)
        
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
                "video_quality": video_data.get('video_quality', 'sd'),
                "category": video_data.get('video_category', 'other'),
                "seo_score": video_data.get('seo_score', 0),
                "thumbnail_score": video_data.get('thumbnail_click_score', 0)
            },
            "recommendations": video_data.get('improvement_suggestions', []),
            "strategy": video_data.get('content_strategy', ''),
            "estimated_revenue": video_data.get('estimated_revenue', 0),
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

@analysis_router.get("/competitors/{channel_id}")
async def analyze_competitors(channel_id: str, competitor_ids: List[str] = None):
    """Анализ конкурентов канала"""
    try:
        if not competitor_ids:
            # Автоматически найти конкурентов (каналы с похожим контентом)
            # Это упрощенная версия - в реальности нужен более сложный алгоритм
            channel_videos = db.get_videos(limit=10, offset=0, filters={'channel_id': channel_id})
            
            if channel_videos:
                # Получить ключевые слова из видео канала
                all_keywords = []
                for video in channel_videos:
                    if video.get('keywords'):
                        all_keywords.extend(video['keywords'][:3])
                
                # Найти каналы с похожими ключевыми словами
                # Это заглушка - нужна реализация поиска похожих каналов
                competitor_ids = []
        
        if not competitor_ids:
            raise HTTPException(status_code=400, detail="Не найдены конкуренты для анализа")
        
        # Провести анализ
        analysis = db.analyze_competitor_channels(channel_id, competitor_ids)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа конкурентов: {str(e)}")

async def process_bulk_analysis(task_id: str, video_ids: List[str]):
    """Обработка массового анализа"""
    try:
        active_tasks[task_id]["status"] = "running"
        db.update_task_status(task_id, "running")
        
        processed = []
        failed = []
        
        for idx, video_id in enumerate(video_ids):
            if task_id in active_tasks and active_tasks[task_id]["status"] == "paused":
                return
            
            try:
                # Получить детали видео
                details = youtube_parser.get_video_details([video_id])
                if video_id in details:
                    video_data = details[video_id]
                    
                    # Расширенный анализ
                    video_data = await analyze_video_extended(video_data)
                    
                    video_data['analyzed_at'] = datetime.now().isoformat()
                    video_data['task_id'] = task_id
                    
                    # Попытка получить транскрипт
                    await process_videos_extended([video_data], task_id)
                    
                    processed.append(video_id)
                else:
                    failed.append(video_id)
                
                # Обновить прогресс
                progress = idx + 1
                active_tasks[task_id]["progress"] = progress
                db.update_task_progress_extended(task_id, progress, len(video_ids), processed, failed)
                
                await asyncio.sleep(settings.REQUEST_DELAY)
                
            except Exception as e:
                print(f"Ошибка анализа видео {video_id}: {e}")
                failed.append(video_id)
                continue
        
        # Завершение
        active_tasks[task_id]["status"] = "completed"
        db.update_task_status(task_id, "completed")
        
        if task_id in active_tasks:
            del active_tasks[task_id]
        
    except Exception as e:
        active_tasks[task_id]["status"] = "error"
        db.update_task_status(task_id, "error", str(e))

# ============ STARTUP/SHUTDOWN ============

async def startup_event():
    """Действия при запуске приложения"""
    print("🚀 Запуск YouTube Analyzer...")
    
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
    print("🛑 Остановка YouTube Analyzer...")
    
    # Создать чекпоинты для всех активных задач
    for task_id, task in active_tasks.items():
        if task['status'] == 'running':
            checkpoint_data = {
                'status': 'interrupted',
                'progress': task.get('progress', 0),
                'timestamp': datetime.now().isoformat()
            }
            db.save_task_checkpoint(task_id, checkpoint_data)
            db.update_task_status(task_id, 'paused')
    
    print("✅ Сервисы остановлены")

print("✅ Enhanced Services загружены успешно")