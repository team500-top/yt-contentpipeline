"""
YouTube Analyzer - Database Manager
Управление SQLite базой данных с расширенной схемой
"""
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import sys

# Добавить пути для импорта
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from shared.config import settings

class DatabaseManager:
    """Менеджер базы данных SQLite с расширенными возможностями"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Включить WAL режим для лучшей производительности
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = 1000000")
            cursor.execute("PRAGMA temp_store = memory")
            
            # Расширенная таблица видео
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    channel_title TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    duration TEXT,
                    duration_seconds INTEGER,
                    is_short BOOLEAN DEFAULT FALSE,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    publish_date TEXT,
                    thumbnail_url TEXT,
                    has_cc BOOLEAN DEFAULT FALSE,
                    video_quality TEXT DEFAULT 'sd',
                    tags TEXT, -- JSON array
                    category_id TEXT,
                    transcript TEXT,
                    transcript_source TEXT,
                    keywords TEXT, -- JSON array
                    has_branding BOOLEAN DEFAULT FALSE,
                    speech_speed REAL,
                    has_intro BOOLEAN DEFAULT FALSE,
                    has_outro BOOLEAN DEFAULT FALSE,
                    like_ratio REAL,
                    comment_ratio REAL,
                    engagement_rate REAL,
                    recommendations TEXT,
                    success_analysis TEXT,
                    task_id TEXT,
                    analyzed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Новые поля для расширенного анализа
                    dislikes INTEGER DEFAULT 0,
                    average_view_duration REAL,
                    click_through_rate REAL,
                    has_pinned_comment BOOLEAN DEFAULT FALSE,
                    links_in_description INTEGER DEFAULT 0,
                    links_in_channel_description INTEGER DEFAULT 0,
                    contacts_in_video TEXT, -- JSON array
                    contacts_in_channel TEXT, -- JSON array
                    top_5_keywords TEXT, -- JSON array
                    video_category TEXT,
                    has_chapters BOOLEAN DEFAULT FALSE,
                    emoji_in_title BOOLEAN DEFAULT FALSE,
                    title_length INTEGER,
                    description_length INTEGER,
                    hashtags_count INTEGER DEFAULT 0,
                    mentioned_channels TEXT, -- JSON array
                    video_language TEXT,
                    is_live_stream BOOLEAN DEFAULT FALSE,
                    is_premiere BOOLEAN DEFAULT FALSE,
                    has_cards BOOLEAN DEFAULT FALSE,
                    has_end_screen BOOLEAN DEFAULT FALSE,
                    upload_schedule_consistency REAL,
                    competitor_comparison TEXT, -- JSON object
                    improvement_suggestions TEXT, -- JSON array
                    content_strategy TEXT,
                    estimated_revenue REAL,
                    audience_retention_score REAL,
                    seo_score INTEGER,
                    thumbnail_click_score INTEGER,
                    
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            ''')
            
            # Таблица каналов с расширенными полями
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_title TEXT NOT NULL,
                    channel_url TEXT,
                    subscriber_count INTEGER DEFAULT 0,
                    video_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    created_at TEXT,
                    avg_views REAL,
                    avg_likes REAL,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Новые поля для расширенного анализа
                    channel_description TEXT,
                    channel_keywords TEXT, -- JSON array
                    country TEXT,
                    custom_url TEXT,
                    default_language TEXT,
                    upload_frequency REAL, -- videos per month
                    avg_video_duration REAL,
                    avg_engagement_rate REAL,
                    total_engagement INTEGER,
                    channel_type TEXT, -- personal, brand, media
                    monetization_enabled BOOLEAN DEFAULT TRUE,
                    verified BOOLEAN DEFAULT FALSE,
                    family_safe BOOLEAN DEFAULT TRUE,
                    topics TEXT, -- JSON array
                    social_links TEXT, -- JSON object
                    email_in_description TEXT,
                    business_email TEXT,
                    has_channel_trailer BOOLEAN DEFAULT FALSE,
                    playlists_count INTEGER DEFAULT 0,
                    community_tab_enabled BOOLEAN DEFAULT FALSE,
                    merchandise_shelf_enabled BOOLEAN DEFAULT FALSE,
                    memberships_enabled BOOLEAN DEFAULT FALSE,
                    super_chat_enabled BOOLEAN DEFAULT FALSE,
                    competitor_channels TEXT, -- JSON array
                    growth_rate REAL,
                    estimated_monthly_revenue REAL,
                    brand_partnerships TEXT -- JSON array
                )
            ''')
            
            # Расширенная таблица задач с чекпоинтами
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT DEFAULT 'analysis',
                    status TEXT DEFAULT 'created',
                    progress INTEGER DEFAULT 0,
                    total_items INTEGER DEFAULT 0,
                    config TEXT, -- JSON
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Новые поля для восстановления состояния
                    checkpoint_data TEXT, -- JSON with recovery info
                    last_checkpoint_at TEXT,
                    processing_time INTEGER DEFAULT 0, -- seconds
                    items_processed TEXT, -- JSON array of processed IDs
                    items_failed TEXT, -- JSON array of failed IDs
                    retry_count INTEGER DEFAULT 0,
                    paused_at TEXT,
                    resumed_at TEXT,
                    completed_at TEXT,
                    estimated_completion TEXT,
                    resources_used TEXT -- JSON object with API calls, etc
                )
            ''')
            
            # Таблица истории парсинга с расширенной информацией
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parsing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT,
                    channel_id TEXT,
                    action TEXT,
                    status TEXT,
                    error_message TEXT,
                    task_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Новые поля
                    retry_count INTEGER DEFAULT 0,
                    processing_time REAL,
                    api_calls_used INTEGER DEFAULT 0,
                    data_source TEXT, -- api, cache, manual
                    metadata TEXT -- JSON with additional info
                )
            ''')
            
            # Новая таблица для кэширования транскриптов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transcript_cache (
                    video_id TEXT PRIMARY KEY,
                    transcript TEXT,
                    language TEXT,
                    source TEXT, -- youtube, whisper, manual
                    confidence_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                )
            ''')
            
            # Новая таблица для анализа трендов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trend_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT,
                    date TEXT,
                    video_count INTEGER,
                    avg_views INTEGER,
                    avg_engagement REAL,
                    top_channels TEXT, -- JSON array
                    trending_topics TEXT, -- JSON array
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Новая таблица для конкурентного анализа
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS competitor_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT,
                    competitor_channel_id TEXT,
                    comparison_date TEXT,
                    metrics_comparison TEXT, -- JSON object
                    strengths TEXT, -- JSON array
                    weaknesses TEXT, -- JSON array
                    opportunities TEXT, -- JSON array
                    recommendations TEXT, -- JSON array
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создание индексов для оптимизации
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_channel_id ON videos(channel_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_task_id ON videos(task_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_analyzed_at ON videos(analyzed_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_is_short ON videos(is_short)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_engagement ON videos(engagement_rate)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_views ON videos(views)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_publish_date ON videos(publish_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_channels_subscriber_count ON channels(subscriber_count)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transcript_cache_expires ON transcript_cache(expires_at)')
            
            conn.commit()
            conn.close()
            print("✅ База данных инициализирована успешно с расширенной схемой")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            raise
    
    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        return conn
    
    # ============ VIDEOS ============
    
    def video_exists(self, video_id: str) -> bool:
        """Проверить существование видео"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM videos WHERE video_id = ?", (video_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_video(self, video_data: Dict[str, Any]):
        """Сохранить видео в БД"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Преобразование списков в JSON
            json_fields = ['tags', 'keywords', 'top_5_keywords', 'contacts_in_video', 
                          'contacts_in_channel', 'mentioned_channels', 'improvement_suggestions']
            
            for field in json_fields:
                if field in video_data and isinstance(video_data[field], list):
                    video_data[field] = json.dumps(video_data[field], ensure_ascii=False)
            
            # Преобразование объектов в JSON
            object_fields = ['competitor_comparison']
            for field in object_fields:
                if field in video_data and isinstance(video_data[field], dict):
                    video_data[field] = json.dumps(video_data[field], ensure_ascii=False)
            
            # Добавить временные метки
            now = datetime.now().isoformat()
            video_data['updated_at'] = now
            if 'created_at' not in video_data:
                video_data['created_at'] = now
            
            # Подготовка данных для вставки
            columns = list(video_data.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [video_data[col] for col in columns]
            
            cursor.execute(f'''
                INSERT OR REPLACE INTO videos ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка сохранения видео: {e}")
        finally:
            conn.close()
    
    def get_videos(self, limit: int = 100, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """Получить список видео с фильтрами"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM videos 
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('is_short') is not None:
                query += ' AND is_short = ?'
                params.append(filters['is_short'])
            
            if filters.get('channel_id'):
                query += ' AND channel_id = ?'
                params.append(filters['channel_id'])
            
            if filters.get('min_views'):
                query += ' AND views >= ?'
                params.append(filters['min_views'])
            
            if filters.get('min_engagement'):
                query += ' AND engagement_rate >= ?'
                params.append(filters['min_engagement'])
        
        query += '''
            ORDER BY analyzed_at DESC, created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        videos = []
        for row in cursor.fetchall():
            video = dict(row)
            # Преобразование JSON полей
            for field in ['tags', 'keywords', 'top_5_keywords', 'contacts_in_video', 
                         'contacts_in_channel', 'mentioned_channels', 'improvement_suggestions']:
                if video.get(field):
                    try:
                        video[field] = json.loads(video[field])
                    except:
                        video[field] = []
            
            for field in ['competitor_comparison']:
                if video.get(field):
                    try:
                        video[field] = json.loads(video[field])
                    except:
                        video[field] = {}
            
            videos.append(video)
        
        conn.close()
        return videos
    
    def get_video_by_id(self, video_id: str) -> Optional[Dict]:
        """Получить видео по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
        row = cursor.fetchone()
        
        if row:
            video = dict(row)
            # Преобразование JSON полей
            for field in ['tags', 'keywords', 'top_5_keywords', 'contacts_in_video', 
                         'contacts_in_channel', 'mentioned_channels', 'improvement_suggestions']:
                if video.get(field):
                    try:
                        video[field] = json.loads(video[field])
                    except:
                        video[field] = []
            
            for field in ['competitor_comparison']:
                if video.get(field):
                    try:
                        video[field] = json.loads(video[field])
                    except:
                        video[field] = {}
            
            conn.close()
            return video
        
        conn.close()
        return None
    
    # ============ CHANNELS ============
    
    def save_channel(self, channel_data: Dict[str, Any]):
        """Сохранить канал в БД"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Преобразование JSON полей
            json_fields = ['channel_keywords', 'topics', 'competitor_channels', 'brand_partnerships']
            for field in json_fields:
                if field in channel_data and isinstance(channel_data[field], list):
                    channel_data[field] = json.dumps(channel_data[field], ensure_ascii=False)
            
            if 'social_links' in channel_data and isinstance(channel_data['social_links'], dict):
                channel_data['social_links'] = json.dumps(channel_data['social_links'], ensure_ascii=False)
            
            # Вычислить средние значения из видео канала
            cursor.execute('''
                SELECT 
                    AVG(views) as avg_views, 
                    AVG(likes) as avg_likes,
                    AVG(engagement_rate) as avg_engagement_rate,
                    AVG(duration_seconds) as avg_video_duration,
                    SUM(views + likes + comments) as total_engagement
                FROM videos WHERE channel_id = ?
            ''', (channel_data['channel_id'],))
            
            avgs = cursor.fetchone()
            if avgs and avgs[0]:
                channel_data['avg_views'] = avgs[0]
                channel_data['avg_likes'] = avgs[1]
                channel_data['avg_engagement_rate'] = avgs[2] or 0
                channel_data['avg_video_duration'] = avgs[3] or 0
                channel_data['total_engagement'] = avgs[4] or 0
            
            # Обновить временную метку
            channel_data['last_updated'] = datetime.now().isoformat()
            
            columns = list(channel_data.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [channel_data[col] for col in columns]
            
            cursor.execute(f'''
                INSERT OR REPLACE INTO channels ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка сохранения канала: {e}")
        finally:
            conn.close()
    
    def get_channels(self) -> List[Dict]:
        """Получить список каналов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.*,
                COUNT(v.video_id) as analyzed_videos
            FROM channels c
            LEFT JOIN videos v ON c.channel_id = v.channel_id
            GROUP BY c.channel_id
            ORDER BY c.subscriber_count DESC, c.last_updated DESC
        ''')
        
        channels = []
        for row in cursor.fetchall():
            channel = dict(row)
            # Преобразование JSON полей
            for field in ['channel_keywords', 'topics', 'competitor_channels', 'brand_partnerships']:
                if channel.get(field):
                    try:
                        channel[field] = json.loads(channel[field])
                    except:
                        channel[field] = []
            
            if channel.get('social_links'):
                try:
                    channel['social_links'] = json.loads(channel['social_links'])
                except:
                    channel['social_links'] = {}
            
            channels.append(channel)
        
        conn.close()
        return channels
    
    def get_channel_stats(self, channel_id: str) -> Dict:
        """Получить статистику канала"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Информация о канале
        cursor.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
        channel_row = cursor.fetchone()
        
        if channel_row:
            channel_info = dict(channel_row)
            
            # Преобразование JSON полей
            for field in ['channel_keywords', 'topics', 'competitor_channels', 'brand_partnerships']:
                if channel_info.get(field):
                    try:
                        channel_info[field] = json.loads(channel_info[field])
                    except:
                        channel_info[field] = []
            
            # Статистика по видео канала
            cursor.execute('''
                SELECT 
                    AVG(views) as avg_views,
                    AVG(likes) as avg_likes,
                    AVG(comments) as avg_comments,
                    AVG(engagement_rate) as avg_engagement,
                    COUNT(*) as video_count,
                    COUNT(CASE WHEN is_short = 1 THEN 1 END) as shorts_count,
                    COUNT(CASE WHEN is_short = 0 THEN 1 END) as videos_count,
                    MAX(views) as max_views,
                    MIN(views) as min_views,
                    AVG(CASE WHEN is_short = 1 THEN engagement_rate END) as shorts_engagement,
                    AVG(CASE WHEN is_short = 0 THEN engagement_rate END) as videos_engagement
                FROM videos 
                WHERE channel_id = ?
            ''', (channel_id,))
            
            stats = cursor.fetchone()
            if stats:
                channel_info.update(dict(stats))
            
            # Топ видео канала
            cursor.execute('''
                SELECT video_id, title, views, engagement_rate
                FROM videos
                WHERE channel_id = ?
                ORDER BY views DESC
                LIMIT 5
            ''', (channel_id,))
            
            channel_info['top_videos'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return channel_info
        
        conn.close()
        return {}
    
    # ============ TASKS ============
    
    def save_task(self, task_data: Dict[str, Any]):
        """Сохранить задачу"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Преобразование в JSON
            for field in ['config', 'checkpoint_data', 'items_processed', 'items_failed', 'resources_used']:
                if field in task_data and isinstance(task_data[field], (dict, list)):
                    task_data[field] = json.dumps(task_data[field], ensure_ascii=False)
            
            columns = list(task_data.keys())
            placeholders = ','.join(['?' for _ in columns])
            values = [task_data[col] for col in columns]
            
            cursor.execute(f'''
                INSERT OR REPLACE INTO tasks ({','.join(columns)})
                VALUES ({placeholders})
            ''', values)
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка сохранения задачи: {e}")
        finally:
            conn.close()
    
    def get_all_tasks(self) -> List[Dict]:
        """Получить все задачи"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        
        tasks = []
        for row in cursor.fetchall():
            task = dict(row)
            # Преобразование JSON полей
            for field in ['config', 'checkpoint_data', 'items_processed', 'items_failed', 'resources_used']:
                if task.get(field):
                    try:
                        task[field] = json.loads(task[field])
                    except:
                        task[field] = {} if field in ['config', 'checkpoint_data', 'resources_used'] else []
            tasks.append(task)
        
        conn.close()
        return tasks
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Получить задачу по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            task = dict(row)
            # Преобразование JSON полей
            for field in ['config', 'checkpoint_data', 'items_processed', 'items_failed', 'resources_used']:
                if task.get(field):
                    try:
                        task[field] = json.loads(task[field])
                    except:
                        task[field] = {} if field in ['config', 'checkpoint_data', 'resources_used'] else []
            conn.close()
            return task
        
        conn.close()
        return None
    
    def update_task_status(self, task_id: str, status: str, error_message: str = None):
        """Обновить статус задачи"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        update_fields = {
            'status': status,
            'updated_at': now
        }
        
        if error_message:
            update_fields['error_message'] = error_message
        
        if status == 'paused':
            update_fields['paused_at'] = now
        elif status == 'running' and cursor.execute("SELECT paused_at FROM tasks WHERE task_id = ?", (task_id,)).fetchone():
            update_fields['resumed_at'] = now
        elif status == 'completed':
            update_fields['completed_at'] = now
        
        # Построение запроса
        set_clause = ', '.join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [task_id]
        
        cursor.execute(f'''
            UPDATE tasks 
            SET {set_clause}
            WHERE task_id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def update_task_progress(self, task_id: str, progress: int, total: int):
        """Обновить прогресс задачи"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET progress = ?, total_items = ?, updated_at = ?
            WHERE task_id = ?
        ''', (progress, total, datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
    
    # ============ TASK CHECKPOINT METHODS ============
    
    def save_task_checkpoint(self, task_id: str, checkpoint_data: Dict[str, Any]):
        """Сохранить чекпоинт задачи для восстановления"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            checkpoint_json = json.dumps(checkpoint_data, ensure_ascii=False)
            now = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE tasks 
                SET checkpoint_data = ?, last_checkpoint_at = ?, updated_at = ?
                WHERE task_id = ?
            ''', (checkpoint_json, now, now, task_id))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка сохранения чекпоинта: {e}")
        finally:
            conn.close()
    
    def get_task_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить чекпоинт задачи"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT checkpoint_data, last_checkpoint_at 
            FROM tasks 
            WHERE task_id = ?
        ''', (task_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row['checkpoint_data']:
            try:
                checkpoint = json.loads(row['checkpoint_data'])
                checkpoint['last_checkpoint_at'] = row['last_checkpoint_at']
                return checkpoint
            except json.JSONDecodeError:
                return None
        return None
    
    def update_task_progress_extended(self, task_id: str, progress: int, total: int, 
                                    processed_items: List[str] = None, 
                                    failed_items: List[str] = None):
        """Обновить прогресс задачи с дополнительной информацией"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Получить текущие данные
            cursor.execute('''
                SELECT items_processed, items_failed, processing_time, created_at
                FROM tasks WHERE task_id = ?
            ''', (task_id,))
            
            current = cursor.fetchone()
            
            # Обновить списки обработанных элементов
            if current:
                current_processed = json.loads(current['items_processed'] or '[]')
                current_failed = json.loads(current['items_failed'] or '[]')
                
                if processed_items:
                    # Использовать set для уникальности
                    current_processed = list(set(current_processed + processed_items))
                if failed_items:
                    current_failed = list(set(current_failed + failed_items))
                
                # Вычислить время обработки
                start_time = datetime.fromisoformat(current['created_at'])
                processing_time = int((datetime.now() - start_time).total_seconds())
                
                # Оценить время завершения
                if progress > 0 and progress < total:
                    time_per_item = processing_time / progress
                    remaining_items = total - progress
                    estimated_seconds = remaining_items * time_per_item
                    estimated_completion = (datetime.now() + timedelta(seconds=estimated_seconds)).isoformat()
                else:
                    estimated_completion = None
                
                cursor.execute('''
                    UPDATE tasks 
                    SET progress = ?, total_items = ?, 
                        items_processed = ?, items_failed = ?,
                        processing_time = ?, estimated_completion = ?,
                        updated_at = ?
                    WHERE task_id = ?
                ''', (progress, total, 
                      json.dumps(current_processed, ensure_ascii=False),
                      json.dumps(current_failed, ensure_ascii=False),
                      processing_time, estimated_completion,
                      datetime.now().isoformat(), task_id))
                
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка обновления прогресса: {e}")
        finally:
            conn.close()
    
    # ============ TRANSCRIPT CACHE METHODS ============
    
    def cache_transcript(self, video_id: str, transcript: str, language: str, 
                        source: str, confidence_score: float = None):
        """Кэшировать транскрипт видео"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Установить срок истечения кэша (30 дней)
            expires_at = (datetime.now() + timedelta(days=30)).isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO transcript_cache 
                (video_id, transcript, language, source, confidence_score, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (video_id, transcript, language, source, confidence_score, expires_at))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка кэширования транскрипта: {e}")
        finally:
            conn.close()
    
    def get_cached_transcript(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Получить кэшированный транскрипт"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT transcript, language, source, confidence_score
            FROM transcript_cache
            WHERE video_id = ? AND expires_at > ?
        ''', (video_id, datetime.now().isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'transcript': row['transcript'],
                'language': row['language'],
                'source': row['source'],
                'confidence_score': row['confidence_score']
            }
        return None
    
    def clean_expired_cache(self):
        """Очистить истекший кэш"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM transcript_cache
            WHERE expires_at < ?
        ''', (datetime.now().isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            print(f"🗑️  Удалено {deleted} истекших транскриптов из кэша")
    
    # ============ ANALYTICS METHODS ============
    
    def get_channel_upload_frequency(self, channel_id: str) -> float:
        """Вычислить частоту загрузки видео канала"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT publish_date
            FROM videos
            WHERE channel_id = ?
            ORDER BY publish_date DESC
        ''', (channel_id,))
        
        dates = [row['publish_date'] for row in cursor.fetchall()]
        conn.close()
        
        if len(dates) < 2:
            return 0.0
        
        # Вычислить среднее время между загрузками
        date_objects = [datetime.fromisoformat(d.replace('Z', '+00:00')) for d in dates if d]
        differences = []
        
        for i in range(1, len(date_objects)):
            diff = (date_objects[i-1] - date_objects[i]).days
            if diff > 0:
                differences.append(diff)
        
        if differences:
            avg_days = sum(differences) / len(differences)
            return 30 / avg_days if avg_days > 0 else 0.0  # Videos per month
        return 0.0
    
    def analyze_competitor_channels(self, channel_id: str, competitor_ids: List[str]) -> Dict[str, Any]:
        """Анализ конкурентов канала"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        analysis = {
            'channel_id': channel_id,
            'competitors': {},
            'recommendations': []
        }
        
        # Получить метрики основного канала
        cursor.execute('''
            SELECT 
                AVG(views) as avg_views,
                AVG(engagement_rate) as avg_engagement,
                COUNT(*) as video_count,
                AVG(duration_seconds) as avg_duration
            FROM videos
            WHERE channel_id = ?
        ''', (channel_id,))
        
        main_metrics = dict(cursor.fetchone())
        
        # Анализ каждого конкурента
        for comp_id in competitor_ids:
            cursor.execute('''
                SELECT 
                    AVG(views) as avg_views,
                    AVG(engagement_rate) as avg_engagement,
                    COUNT(*) as video_count,
                    AVG(duration_seconds) as avg_duration
                FROM videos
                WHERE channel_id = ?
            ''', (comp_id,))
            
            comp_row = cursor.fetchone()
            if comp_row:
                comp_metrics = dict(comp_row)
                
                comparison = {
                    'avg_views_diff': (comp_metrics['avg_views'] - main_metrics['avg_views']) / main_metrics['avg_views'] * 100 if main_metrics['avg_views'] else 0,
                    'avg_engagement_diff': comp_metrics['avg_engagement'] - main_metrics['avg_engagement'],
                    'video_count': comp_metrics['video_count'],
                    'avg_duration': comp_metrics['avg_duration']
                }
                
                # Рекомендации на основе сравнения
                if comparison['avg_views_diff'] > 50:
                    analysis['recommendations'].append(f"Изучите стратегию канала {comp_id} - их видео получают на {comparison['avg_views_diff']:.0f}% больше просмотров")
                
                if comparison['avg_engagement_diff'] > 2:
                    analysis['recommendations'].append(f"Канал {comp_id} имеет лучшую вовлеченность (+{comparison['avg_engagement_diff']:.1f}%) - проанализируйте их подход")
                
                analysis['competitors'][comp_id] = comparison
        
        # Сохранить анализ
        self.save_competitor_analysis(channel_id, competitor_ids[0] if competitor_ids else None, analysis)
        
        conn.close()
        return analysis
    
    def save_competitor_analysis(self, channel_id: str, competitor_id: str, analysis: Dict[str, Any]):
        """Сохранить результаты конкурентного анализа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO competitor_analysis 
                (channel_id, competitor_channel_id, comparison_date, 
                 metrics_comparison, recommendations)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                channel_id,
                competitor_id,
                datetime.now().date().isoformat(),
                json.dumps(analysis.get('competitors', {}), ensure_ascii=False),
                json.dumps(analysis.get('recommendations', []), ensure_ascii=False)
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Ошибка сохранения конкурентного анализа: {e}")
        finally:
            conn.close()
    
    def save_trend_analysis(self, keyword: str, analysis_data: Dict[str, Any]):
        """Сохранить анализ трендов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO trend_analysis 
                (keyword, date, video_count, avg_views, avg_engagement, 
                 top_channels, trending_topics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                keyword,
                datetime.now().date().isoformat(),
                analysis_data.get('video_count', 0),
                analysis_data.get('avg_views', 0),
                analysis_data.get('avg_engagement', 0),
                json.dumps(analysis_data.get('top_channels', []), ensure_ascii=False),
                json.dumps(analysis_data.get('trending_topics', []), ensure_ascii=False)
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка сохранения анализа трендов: {e}")
        finally:
            conn.close()
    
    # ============ STATISTICS ============
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить общую статистику"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Общие счетчики
        cursor.execute("SELECT COUNT(*) FROM videos")
        stats['total_videos'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM channels")
        stats['total_channels'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        stats['total_tasks'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        stats['completed_tasks'] = cursor.fetchone()[0]
        
        # Средняя вовлеченность
        cursor.execute("SELECT AVG(engagement_rate) FROM videos WHERE engagement_rate IS NOT NULL")
        avg_engagement = cursor.fetchone()[0]
        stats['avg_engagement'] = round(avg_engagement, 2) if avg_engagement else 0
        
        # Видео по типам
        cursor.execute('''
            SELECT 
                CASE WHEN is_short THEN 'shorts' ELSE 'long' END as type,
                COUNT(*) as count
            FROM videos 
            GROUP BY is_short
        ''')
        
        videos_by_type = {}
        for row in cursor.fetchall():
            videos_by_type[row[0]] = row[1]
        stats['videos_by_type'] = videos_by_type
        
        # Топ каналы по вовлеченности
        cursor.execute('''
            SELECT 
                c.channel_title,
                c.subscriber_count,
                COUNT(v.video_id) as video_count,
                AVG(v.engagement_rate) as avg_engagement,
                SUM(v.views) as total_views
            FROM channels c
            LEFT JOIN videos v ON c.channel_id = v.channel_id
            GROUP BY c.channel_id
            HAVING video_count > 0
            ORDER BY avg_engagement DESC
            LIMIT 10
        ''')
        
        top_channels = []
        for row in cursor.fetchall():
            top_channels.append({
                'channel_title': row[0],
                'subscriber_count': row[1] or 0,
                'video_count': row[2],
                'avg_engagement': round(row[3], 2) if row[3] else 0,
                'total_views': row[4] or 0
            })
        stats['top_channels'] = top_channels
        
        # Топ видео по просмотрам
        cursor.execute('''
            SELECT 
                title,
                channel_title,
                views,
                engagement_rate,
                video_id
            FROM videos
            ORDER BY views DESC
            LIMIT 10
        ''')
        
        top_videos = []
        for row in cursor.fetchall():
            top_videos.append({
                'title': row[0],
                'channel_title': row[1],
                'views': row[2],
                'engagement_rate': round(row[3], 2) if row[3] else 0,
                'video_id': row[4]
            })
        stats['top_videos'] = top_videos
        
        # Статистика по задачам
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count,
                AVG(processing_time) / 60.0 as avg_minutes
            FROM tasks
            GROUP BY status
        ''')
        
        task_stats = {}
        for row in cursor.fetchall():
            task_stats[row[0]] = {
                'count': row[1],
                'avg_minutes': round(row[2], 1) if row[2] else 0
            }
        stats['task_stats'] = task_stats
        
        conn.close()
        return stats
    
    # ============ ENHANCED EXPORT ============
    
    def export_to_excel(self, filename: str = None) -> str:
        """Экспорт данных в Excel с множеством листов"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_analysis_{timestamp}.xlsx"
        
        export_path = Path(settings.EXPORT_DIR) / filename
        export_path.parent.mkdir(exist_ok=True)
        
        conn = self.get_connection()
        
        try:
            with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                # 1. Основные данные видео
                videos_query = '''
                    SELECT 
                        'https://youtube.com/watch?v=' || video_id as video_url,
                        title, channel_title, 
                        CASE WHEN is_short THEN 'SHORT' ELSE 'VIDEO' END as type,
                        views, likes, comments,
                        engagement_rate, like_ratio, comment_ratio,
                        duration, publish_date,
                        has_cc, video_quality, has_branding,
                        speech_speed, emoji_in_title,
                        links_in_description, hashtags_count,
                        analyzed_at
                    FROM videos
                    ORDER BY analyzed_at DESC
                '''
                videos_df = pd.read_sql_query(videos_query, conn)
                videos_df.to_excel(writer, sheet_name='Videos', index=False)
                
                # 2. Расширенная аналитика видео
                analytics_query = '''
                    SELECT 
                        video_id, title,
                        average_view_duration, click_through_rate,
                        has_chapters, has_intro, has_outro,
                        has_pinned_comment, has_cards, has_end_screen,
                        seo_score, thumbnail_click_score,
                        audience_retention_score, estimated_revenue,
                        top_5_keywords, recommendations,
                        success_analysis, content_strategy,
                        improvement_suggestions
                    FROM videos
                    WHERE analyzed_at IS NOT NULL
                    ORDER BY engagement_rate DESC
                '''
                analytics_df = pd.read_sql_query(analytics_query, conn)
                
                # Преобразовать JSON поля
                if not analytics_df.empty:
                    for json_field in ['top_5_keywords', 'improvement_suggestions']:
                        analytics_df[json_field] = analytics_df[json_field].apply(
                            lambda x: ', '.join(json.loads(x)) if x and x != 'null' and x != '[]' else ''
                        )
                
                analytics_df.to_excel(writer, sheet_name='Video Analytics', index=False)
                
                # 3. Данные каналов
                channels_query = '''
                    SELECT 
                        channel_title, channel_url,
                        subscriber_count, video_count, view_count,
                        avg_views, avg_engagement_rate,
                        upload_frequency, channel_type,
                        verified, monetization_enabled,
                        growth_rate, estimated_monthly_revenue
                    FROM channels
                    ORDER BY subscriber_count DESC
                '''
                channels_df = pd.read_sql_query(channels_query, conn)
                channels_df.to_excel(writer, sheet_name='Channels', index=False)
                
                # 4. Топ видео
                top_videos_query = '''
                    SELECT 
                        title, channel_title, views, engagement_rate,
                        'https://youtube.com/watch?v=' || video_id as url
                    FROM videos
                    ORDER BY views DESC
                    LIMIT 50
                '''
                top_videos_df = pd.read_sql_query(top_videos_query, conn)
                top_videos_df.to_excel(writer, sheet_name='Top 50 Videos', index=False)
                
                # 5. Анализ трендов
                trends_query = '''
                    SELECT 
                        keyword, date, video_count,
                        avg_views, avg_engagement,
                        trending_topics
                    FROM trend_analysis
                    ORDER BY date DESC, avg_views DESC
                '''
                trends_df = pd.read_sql_query(trends_query, conn)
                if not trends_df.empty:
                    trends_df['trending_topics'] = trends_df['trending_topics'].apply(
                        lambda x: ', '.join(json.loads(x)) if x and x != 'null' else ''
                    )
                    trends_df.to_excel(writer, sheet_name='Trends', index=False)
                
                # 6. Статистика по задачам
                tasks_query = '''
                    SELECT 
                        task_id, status, progress, total_items,
                        processing_time / 60.0 as processing_minutes,
                        created_at, completed_at
                    FROM tasks
                    ORDER BY created_at DESC
                '''
                tasks_df = pd.read_sql_query(tasks_query, conn)
                tasks_df.to_excel(writer, sheet_name='Tasks', index=False)
                
                # 7. Сводная статистика
                stats = self.get_statistics()
                summary_data = []
                
                summary_data.append({
                    'Метрика': 'Всего видео',
                    'Значение': stats['total_videos']
                })
                summary_data.append({
                    'Метрика': 'Всего каналов',
                    'Значение': stats['total_channels']
                })
                summary_data.append({
                    'Метрика': 'Средняя вовлеченность',
                    'Значение': f"{stats['avg_engagement']}%"
                })
                summary_data.append({
                    'Метрика': 'Shorts видео',
                    'Значение': stats['videos_by_type'].get('shorts', 0)
                })
                summary_data.append({
                    'Метрика': 'Обычных видео',
                    'Значение': stats['videos_by_type'].get('long', 0)
                })
                summary_data.append({
                    'Метрика': 'Выполнено задач',
                    'Значение': stats['completed_tasks']
                })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            conn.close()
            print(f"✅ Данные экспортированы в {filename}")
            return str(export_path)
            
        except Exception as e:
            conn.close()
            raise Exception(f"Ошибка экспорта: {e}")
    
    # ============ MAINTENANCE ============
    
    def clear_database(self):
        """Очистить все данные"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            tables = [
                'parsing_history', 'competitor_analysis', 'trend_analysis',
                'transcript_cache', 'videos', 'channels', 'tasks'
            ]
            
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            
            # Сбросить счетчики автоинкремента
            cursor.execute("DELETE FROM sqlite_sequence")
            
            conn.commit()
            print("✅ База данных очищена")
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка очистки БД: {e}")
        finally:
            conn.close()
    
    def vacuum_database(self):
        """Оптимизация базы данных"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()
        print("✅ База данных оптимизирована")
    
    def backup_database(self, backup_path: str = None):
        """Создать резервную копию БД"""
        import shutil
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/youtube_data_backup_{timestamp}.db"
        
        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(exist_ok=True)
        
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Резервная копия создана: {backup_path}")
        return backup_path
    
    # ============ MIGRATION METHODS ============
    
    def migrate_database(self):
        """Миграция базы данных к новой схеме"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверить существующие колонки в таблице videos
            cursor.execute("PRAGMA table_info(videos)")
            existing_columns = {col[1] for col in cursor.fetchall()}
            
            # Список новых колонок для добавления в videos
            new_columns = {
                'dislikes': 'INTEGER DEFAULT 0',
                'average_view_duration': 'REAL',
                'click_through_rate': 'REAL',
                'has_pinned_comment': 'BOOLEAN DEFAULT FALSE',
                'links_in_description': 'INTEGER DEFAULT 0',
                'links_in_channel_description': 'INTEGER DEFAULT 0',
                'contacts_in_video': 'TEXT',
                'contacts_in_channel': 'TEXT',
                'top_5_keywords': 'TEXT',
                'video_category': 'TEXT',
                'has_chapters': 'BOOLEAN DEFAULT FALSE',
                'emoji_in_title': 'BOOLEAN DEFAULT FALSE',
                'title_length': 'INTEGER',
                'description_length': 'INTEGER',
                'hashtags_count': 'INTEGER DEFAULT 0',
                'mentioned_channels': 'TEXT',
                'video_language': 'TEXT',
                'is_live_stream': 'BOOLEAN DEFAULT FALSE',
                'is_premiere': 'BOOLEAN DEFAULT FALSE',
                'has_cards': 'BOOLEAN DEFAULT FALSE',
                'has_end_screen': 'BOOLEAN DEFAULT FALSE',
                'upload_schedule_consistency': 'REAL',
                'competitor_comparison': 'TEXT',
                'improvement_suggestions': 'TEXT',
                'content_strategy': 'TEXT',
                'estimated_revenue': 'REAL',
                'audience_retention_score': 'REAL',
                'seo_score': 'INTEGER',
                'thumbnail_click_score': 'INTEGER'
            }
            
            # Добавить отсутствующие колонки
            for column, definition in new_columns.items():
                if column not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE videos ADD COLUMN {column} {definition}')
                        print(f"✅ Добавлена колонка: {column}")
                    except sqlite3.OperationalError:
                        pass
            
            # Проверить колонки в таблице channels
            cursor.execute("PRAGMA table_info(channels)")
            existing_channel_columns = {col[1] for col in cursor.fetchall()}
            
            new_channel_columns = {
                'channel_description': 'TEXT',
                'channel_keywords': 'TEXT',
                'country': 'TEXT',
                'custom_url': 'TEXT',
                'default_language': 'TEXT',
                'upload_frequency': 'REAL',
                'avg_video_duration': 'REAL',
                'avg_engagement_rate': 'REAL',
                'total_engagement': 'INTEGER',
                'channel_type': 'TEXT',
                'monetization_enabled': 'BOOLEAN DEFAULT TRUE',
                'verified': 'BOOLEAN DEFAULT FALSE',
                'family_safe': 'BOOLEAN DEFAULT TRUE',
                'topics': 'TEXT',
                'social_links': 'TEXT',
                'email_in_description': 'TEXT',
                'business_email': 'TEXT',
                'has_channel_trailer': 'BOOLEAN DEFAULT FALSE',
                'playlists_count': 'INTEGER DEFAULT 0',
                'community_tab_enabled': 'BOOLEAN DEFAULT FALSE',
                'merchandise_shelf_enabled': 'BOOLEAN DEFAULT FALSE',
                'memberships_enabled': 'BOOLEAN DEFAULT FALSE',
                'super_chat_enabled': 'BOOLEAN DEFAULT FALSE',
                'competitor_channels': 'TEXT',
                'growth_rate': 'REAL',
                'estimated_monthly_revenue': 'REAL',
                'brand_partnerships': 'TEXT'
            }
            
            for column, definition in new_channel_columns.items():
                if column not in existing_channel_columns:
                    try:
                        cursor.execute(f'ALTER TABLE channels ADD COLUMN {column} {definition}')
                        print(f"✅ Добавлена колонка в channels: {column}")
                    except sqlite3.OperationalError:
                        pass
            
            # Проверить колонки в таблице tasks
            cursor.execute("PRAGMA table_info(tasks)")
            existing_task_columns = {col[1] for col in cursor.fetchall()}
            
            new_task_columns = {
                'checkpoint_data': 'TEXT',
                'last_checkpoint_at': 'TEXT',
                'processing_time': 'INTEGER DEFAULT 0',
                'items_processed': 'TEXT',
                'items_failed': 'TEXT',
                'retry_count': 'INTEGER DEFAULT 0',
                'paused_at': 'TEXT',
                'resumed_at': 'TEXT',
                'completed_at': 'TEXT',
                'estimated_completion': 'TEXT',
                'resources_used': 'TEXT'
            }
            
            for column, definition in new_task_columns.items():
                if column not in existing_task_columns:
                    try:
                        cursor.execute(f'ALTER TABLE tasks ADD COLUMN {column} {definition}')
                        print(f"✅ Добавлена колонка в tasks: {column}")
                    except sqlite3.OperationalError:
                        pass
            
            conn.commit()
            print("✅ Миграция базы данных завершена")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Ошибка миграции: {e}")
            raise
        finally:
            conn.close()

# Автоматическая миграция при импорте
if __name__ == "__main__":
    db = DatabaseManager()
    db.migrate_database()

print("✅ Enhanced Database Manager загружен успешно")