"""
YouTube Analyzer - Configuration Management
Управление конфигурацией системы
"""
import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # YouTube API
    YOUTUBE_API_KEY: str = Field(default="", env="YOUTUBE_API_KEY")
    
    # Database
    DATABASE_PATH: str = Field(default="youtube_data.db", env="DATABASE_PATH")
    
    # Limits
    MAX_LONG_VIDEOS_CHANNEL: int = Field(default=5, ge=1, le=500)
    MAX_LONG_VIDEOS_SEARCH: int = Field(default=5, ge=1, le=500)
    MAX_SHORTS_CHANNEL: int = Field(default=5, ge=1, le=500)
    MAX_SHORTS_SEARCH: int = Field(default=5, ge=1, le=500)
    
    # Processing
    ORDER_BY: str = Field(default="relevance", pattern=r"^(relevance|date|viewCount|both)$")
    MAX_TRANSCRIPT_LENGTH: int = Field(default=50000, ge=1000, le=100000)
    WHISPER_MODEL: str = Field(default="tiny", pattern=r"^(tiny|base|small|medium|large)$")
    
    # Server
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Paths
    TEMP_DIR: str = Field(default="temp", env="TEMP_DIR")
    EXPORT_DIR: str = Field(default="exports", env="EXPORT_DIR")
    
    # Processing settings
    REQUEST_DELAY: float = Field(default=1.0, description="Задержка между API запросами (секунды)")
    MAX_CONCURRENT_TASKS: int = Field(default=3, description="Максимум одновременных задач")
    TASK_TIMEOUT: int = Field(default=3600, description="Таймаут задачи в секундах")
    
    # Cache settings
    ENABLE_CACHE: bool = Field(default=True, description="Включить кэширование")
    CACHE_TTL: int = Field(default=3600, description="Время жизни кэша в секундах")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Игнорировать дополнительные поля из .env
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
        self._load_from_json()
    
    def _ensure_directories(self):
        """Создать необходимые директории"""
        Path(self.TEMP_DIR).mkdir(exist_ok=True)
        Path(self.EXPORT_DIR).mkdir(exist_ok=True)
    
    def _load_from_json(self):
        """Загрузить настройки из JSON файла"""
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Обновить настройки из JSON
                for key, value in config_data.items():
                    if hasattr(self, key.upper()):
                        setattr(self, key.upper(), value)
                    elif hasattr(self, key):
                        setattr(self, key, value)
                        
            except Exception as e:
                print(f"⚠️  Ошибка загрузки config.json: {e}")
    
    def save_to_json(self):
        """Сохранить настройки в JSON файл"""
        config_data = {}
        
        # Получить все настройки
        for field_name, field_info in self.__fields__.items():
            value = getattr(self, field_name)
            # Конвертировать имена полей в snake_case для совместимости
            json_key = field_name.lower()
            config_data[json_key] = value
        
        # Не сохранять чувствительные данные в открытом виде
        if config_data.get('youtube_api_key'):
            config_data['youtube_api_key'] = '***'
        
        try:
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print("✅ Конфигурация сохранена в config.json")
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def update_from_dict(self, data: dict):
        """Обновить настройки из словаря"""
        for key, value in data.items():
            # Попробовать найти поле по разным вариантам имени
            field_variants = [
                key.upper(),
                key.lower(), 
                key
            ]
            
            for variant in field_variants:
                if hasattr(self, variant):
                    setattr(self, variant, value)
                    break
        
        # Сохранить обновленные настройки
        self.save_to_json()
    
    def get_youtube_settings(self) -> dict:
        """Получить настройки для YouTube API"""
        return {
            "api_key": self.YOUTUBE_API_KEY,
            "max_long_videos_channel": self.MAX_LONG_VIDEOS_CHANNEL,
            "max_long_videos_search": self.MAX_LONG_VIDEOS_SEARCH,
            "max_shorts_channel": self.MAX_SHORTS_CHANNEL,
            "max_shorts_search": self.MAX_SHORTS_SEARCH,
            "order_by": self.ORDER_BY
        }
    
    def get_processing_settings(self) -> dict:
        """Получить настройки обработки"""
        return {
            "whisper_model": self.WHISPER_MODEL,
            "max_transcript_length": self.MAX_TRANSCRIPT_LENGTH,
            "request_delay": self.REQUEST_DELAY,
            "max_concurrent_tasks": self.MAX_CONCURRENT_TASKS,
            "task_timeout": self.TASK_TIMEOUT
        }
    
    def get_database_settings(self) -> dict:
        """Получить настройки базы данных"""
        return {
            "database_path": self.DATABASE_PATH,
            "temp_dir": self.TEMP_DIR,
            "export_dir": self.EXPORT_DIR
        }
    
    def validate_youtube_api(self) -> bool:
        """Проверить валидность YouTube API ключа"""
        if not self.YOUTUBE_API_KEY or self.YOUTUBE_API_KEY == "YOUR_API_KEY_HERE":
            return False
        
        # Простая проверка формата (YouTube API ключи обычно длиной 39 символов)
        if len(self.YOUTUBE_API_KEY) < 30:
            return False
            
        return True
    
    def get_safe_dict(self) -> dict:
        """Получить словарь настроек без чувствительных данных"""
        safe_dict = {}
        
        for field_name in self.__fields__:
            value = getattr(self, field_name)
            
            # Скрыть чувствительные данные
            if 'api_key' in field_name.lower() or 'password' in field_name.lower():
                safe_dict[field_name.lower()] = '***' if value else ''
            else:
                safe_dict[field_name.lower()] = value
        
        return safe_dict
    
    def dict(self, **kwargs):
        """Переопределение метода dict для совместимости"""
        return self.model_dump(**kwargs)

# Создать глобальный экземпляр настроек
settings = Settings()

# Функции для работы с конфигурацией
def get_settings() -> Settings:
    """Получить текущие настройки"""
    return settings

def update_settings(**kwargs) -> Settings:
    """Обновить настройки"""
    settings.update_from_dict(kwargs)
    return settings

def reload_settings() -> Settings:
    """Перезагрузить настройки"""
    global settings
    settings = Settings()
    return settings

def create_example_files():
    """Создать примеры файлов конфигурации"""
    
    # Создать .env.example
    env_example = """# YouTube Analyzer - Environment Variables
# Скопируйте этот файл в .env и заполните своими значениями

# YouTube API Key (обязательно)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Database
DATABASE_PATH=youtube_data.db

# Server settings
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Directories
TEMP_DIR=temp
EXPORT_DIR=exports
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_example)
    
    # Создать config.json.example
    config_example = {
        "youtube_api_key": "YOUR_API_KEY_HERE",
        "max_long_videos_channel": 5,
        "max_long_videos_search": 5,
        "max_shorts_channel": 5,
        "max_shorts_search": 5,
        "order_by": "relevance",
        "max_transcript_length": 50000,
        "whisper_model": "tiny",
        "request_delay": 1.0,
        "max_concurrent_tasks": 3,
        "enable_cache": True,
        "cache_ttl": 3600
    }
    
    with open('config.json.example', 'w', encoding='utf-8') as f:
        json.dump(config_example, f, indent=2, ensure_ascii=False)
    
    print("✅ Созданы примеры конфигурационных файлов:")
    print("   - .env.example")
    print("   - config.json.example")

# Проверить настройки при импорте
if __name__ == "__main__":
    print("🔧 YouTube Analyzer - Configuration")
    print(f"📁 Database: {settings.DATABASE_PATH}")
    print(f"🔑 YouTube API: {'✅ Настроен' if settings.validate_youtube_api() else '❌ Не настроен'}")
    print(f"🏠 Host: {settings.HOST}:{settings.PORT}")
    print(f"🔧 Debug: {settings.DEBUG}")
    
    # Создать примеры если их нет
    if not Path('.env.example').exists():
        create_example_files()

print("✅ Configuration manager загружен успешно")