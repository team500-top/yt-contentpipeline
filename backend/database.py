"""
YouTube Analyzer - Database Manager
Управление SQLite базой данных
"""
import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys

# Добавить пути для импорта
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from shared.config import settings

class DatabaseManager:
    """Менеджер базы данных SQLite"""
    
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
            
            # Таблица видео
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
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            ''')
            
            # Таблица каналов
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
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица задач
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
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица истории парсинга
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parsing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT,
                    action TEXT,
                    status TEXT,
                    error_message TEXT,
                    task_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создание индексов для оптимизации
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_channel_id ON videos(channel_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_task_id ON videos(task_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_analyzed_at ON videos(analyzed_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_is_short ON videos(is_short)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_engagement ON videos(engagement_rate)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)')
            
            conn.commit()
            conn.close()
            print("✅ База данных инициализирована успешно")
            
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
            if 'tags' in video_data and isinstance(video_data['tags'], list):
                video_data['tags'] = json.dumps(video_data['tags'])
            if 'keywords' in video_data and isinstance(video_data['keywords'], list):
                video_data['keywords'] = json.dumps(video_data['keywords'])
            
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
    
    def get_videos(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получить список видео"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM videos 
            ORDER BY analyzed_at DESC, created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        videos = []
        for row in cursor.fetchall():
            video = dict(row)
            # Преобразование JSON полей
            if video.get('tags'):
                try:
                    video['tags'] = json.loads(video['tags'])
                except:
                    video['tags'] = []
            if video.get('keywords'):
                try:
                    video['keywords'] = json.loads(video['keywords'])
                except:
                    video['keywords'] = []
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
            if video.get('tags'):
                try:
                    video['tags'] = json.loads(video['tags'])
                except:
                    video['tags'] = []
            if video.get('keywords'):
                try:
                    video['keywords'] = json.loads(video['keywords'])
                except:
                    video['keywords'] = []
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
            # Вычислить средние значения из видео канала
            cursor.execute('''
                SELECT AVG(views) as avg_views, AVG(likes) as avg_likes
                FROM videos WHERE channel_id = ?
            ''', (channel_data['channel_id'],))
            
            avgs = cursor.fetchone()
            if avgs and avgs[0]:
                channel_data['avg_views'] = avgs[0]
                channel_data['avg_likes'] = avgs[1]
            
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
            ORDER BY c.last_updated DESC
        ''')
        
        channels = [dict(row) for row in cursor.fetchall()]
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
            
            # Статистика по видео канала
            cursor.execute('''
                SELECT 
                    AVG(views) as avg_views,
                    AVG(likes) as avg_likes,
                    AVG(comments) as avg_comments,
                    AVG(engagement_rate) as avg_engagement,
                    COUNT(*) as video_count
                FROM videos 
                WHERE channel_id = ?
            ''', (channel_id,))
            
            stats = cursor.fetchone()
            if stats:
                channel_info.update({
                    'avg_views': stats[0] or 0,
                    'avg_likes': stats[1] or 0,
                    'avg_comments': stats[2] or 0,
                    'avg_engagement': stats[3] or 0,
                    'analyzed_videos': stats[4] or 0
                })
            
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
            if 'config' in task_data and isinstance(task_data['config'], dict):
                task_data['config'] = json.dumps(task_data['config'])
            
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
            if task.get('config'):
                try:
                    task['config'] = json.loads(task['config'])
                except:
                    task['config'] = {}
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
            if task.get('config'):
                try:
                    task['config'] = json.loads(task['config'])
                except:
                    task['config'] = {}
            conn.close()
            return task
        
        conn.close()
        return None
    
    def update_task_status(self, task_id: str, status: str, error_message: str = None):
        """Обновить статус задачи"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, error_message = ?, updated_at = ?
            WHERE task_id = ?
        ''', (status, error_message, datetime.now().isoformat(), task_id))
        
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
        
        # Топ каналы
        cursor.execute('''
            SELECT 
                c.channel_title,
                c.subscriber_count,
                COUNT(v.video_id) as video_count,
                AVG(v.engagement_rate) as avg_engagement
            FROM channels c
            LEFT JOIN videos v ON c.channel_id = v.channel_id
            GROUP BY c.channel_id
            ORDER BY video_count DESC, avg_engagement DESC
            LIMIT 10
        ''')
        
        top_channels = []
        for row in cursor.fetchall():
            top_channels.append({
                'channel_title': row[0],
                'subscriber_count': row[1] or 0,
                'video_count': row[2],
                'avg_engagement': round(row[3], 2) if row[3] else 0
            })
        stats['top_channels'] = top_channels
        
        conn.close()
        return stats
    
    # ============ EXPORT ============
    
    def export_to_excel(self, filename: str = None) -> str:
        """Экспорт данных в Excel"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"youtube_analysis_{timestamp}.xlsx"
        
        conn = self.get_connection()
        
        try:
            # Получить данные видео
            videos_df = pd.read_sql_query('''
                SELECT 
                    'https://youtube.com/watch?v=' || video_id as video_url,
                    'https://youtube.com/channel/' || channel_id as channel_url,
                    channel_title,
                    title,
                    description,
                    duration,
                    CASE 
                        WHEN is_short THEN 'SHORT'
                        ELSE 'LONG'
                    END as video_type,
                    views,
                    likes,
                    comments,
                    like_ratio,
                    comment_ratio,
                    engagement_rate,
                    has_branding,
                    publish_date,
                    keywords as top_5_keywords,
                    thumbnail_url,
                    has_cc,
                    video_quality,
                    has_intro,
                    has_outro,
                    speech_speed,
                    recommendations,
                    success_analysis as analysis,
                    analyzed_at
                FROM videos
                ORDER BY analyzed_at DESC
            ''', conn)
            
            # Получить данные каналов
            channels_df = pd.read_sql_query('''
                SELECT 
                    channel_id,
                    channel_title,
                    channel_url,
                    subscriber_count,
                    video_count,
                    view_count,
                    avg_views as channel_avg_views,
                    avg_likes as channel_avg_likes,
                    last_updated
                FROM channels
                ORDER BY channel_title
            ''', conn)
            
            # Обработка данных
            if not videos_df.empty:
                # Обработка ключевых слов
                videos_df['top_5_keywords'] = videos_df['top_5_keywords'].apply(
                    lambda x: ', '.join(json.loads(x)[:5]) if x and x != 'null' and x != '[]' else ''
                )
                
                # Добавление дополнительных полей
                videos_df['emoji_in_title'] = videos_df['title'].apply(
                    lambda x: any(ord(char) > 127 for char in str(x)) if x else False
                )
                
                videos_df['links_in_description'] = videos_df['description'].apply(
                    lambda x: len([word for word in str(x).split() if 'http' in word]) if x else 0
                )
            
            # Сохранение в Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                if not videos_df.empty:
                    videos_df.to_excel(writer, sheet_name='Videos', index=False)
                
                if not channels_df.empty:
                    channels_df.to_excel(writer, sheet_name='Channels', index=False)
                
                # Лист статистики
                stats = self.get_statistics()
                stats_data = []
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        stats_data.append({'Metric': key, 'Value': value})
                
                if stats_data:
                    stats_df = pd.DataFrame(stats_data)
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            conn.close()
            print(f"✅ Данные экспортированы в {filename}")
            return filename
            
        except Exception as e:
            conn.close()
            raise Exception(f"Ошибка экспорта: {e}")
    
    # ============ MAINTENANCE ============
    
    def clear_database(self):
        """Очистить все данные"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM parsing_history")
            cursor.execute("DELETE FROM videos")
            cursor.execute("DELETE FROM channels")
            cursor.execute("DELETE FROM tasks")
            
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
    
    def backup_database(self, backup_path: str):
        """Создать резервную копию БД"""
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Резервная копия создана: {backup_path}")

print("✅ Database Manager загружен успешно")