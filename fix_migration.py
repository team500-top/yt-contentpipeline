"""
Скрипт для исправления миграции базы данных
Запустите этот файл для обновления схемы БД
"""
import sqlite3
from pathlib import Path

def fix_database_migration():
    """Исправить проблемы с миграцией БД"""
    db_path = "youtube_data.db"
    
    if not Path(db_path).exists():
        print("❌ База данных не найдена!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем существующие колонки в таблице tasks
        cursor.execute("PRAGMA table_info(tasks)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        print(f"Существующие колонки в tasks: {existing_columns}")
        
        # Добавляем недостающие колонки
        new_columns = {
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
        
        for column, definition in new_columns.items():
            if column not in existing_columns:
                try:
                    query = f'ALTER TABLE tasks ADD COLUMN {column} {definition}'
                    cursor.execute(query)
                    print(f"✅ Добавлена колонка: {column}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Колонка {column} уже существует или ошибка: {e}")
        
        # Проверяем и создаем новые таблицы если их нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcript_cache (
                video_id TEXT PRIMARY KEY,
                transcript TEXT,
                language TEXT,
                source TEXT,
                confidence_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT
            )
        """)
        print("✅ Таблица transcript_cache проверена/создана")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                date TEXT,
                video_count INTEGER,
                avg_views INTEGER,
                avg_engagement REAL,
                top_channels TEXT,
                trending_topics TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица trend_analysis проверена/создана")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitor_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                competitor_channel_id TEXT,
                comparison_date TEXT,
                metrics_comparison TEXT,
                strengths TEXT,
                weaknesses TEXT,
                opportunities TEXT,
                recommendations TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица competitor_analysis проверена/создана")
        
        conn.commit()
        print("\n✅ Миграция базы данных завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Запуск исправления миграции БД...")
    fix_database_migration()
    print("\nТеперь перезапустите сервер командой: run.bat")
    input("Нажмите Enter для завершения...")