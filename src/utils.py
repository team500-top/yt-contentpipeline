#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Вспомогательные функции для YouTube Competitor Analysis Tool
"""

import os
import sys
import json
import logging
import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import requests
from diskcache import Cache

from config import config, validate_config

def setup_logging(level: str = None, log_file: str = None) -> logging.Logger:
    """Настройка системы логирования"""
    
    # Определение уровня логирования
    if level is None:
        level = config.log_level
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Определение файла логов
    if log_file is None:
        log_file = config.log_file
    
    # Создание папки для логов
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Очистка существующих обработчиков
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Файловый обработчик
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено. Уровень: {level}, Файл: {log_file}")
    
    return logger

def load_config() -> Dict:
    """Загрузка и валидация конфигурации"""
    
    logger = logging.getLogger(__name__)
    
    # Валидация конфигурации
    warnings = validate_config()
    
    if warnings:
        logger.warning("Найдены предупреждения в конфигурации:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    logger.info("Конфигурация загружена успешно")
    
    # Возвращаем словарь с основными настройками
    return {
        'youtube_api_key': config.youtube_api_key,
        'max_videos': config.max_total_videos,
        'max_channels': config.max_channels_to_analyze,
        'enable_transcripts': config.enable_transcript_extraction,
        'enable_analysis': config.enable_content_analysis,
        'max_workers': config.max_workers,
        'request_delay': config.request_delay,
        'proxies': config.proxies
    }

def validate_environment() -> bool:
    """Валидация окружения и зависимостей"""
    
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'requests', 'beautifulsoup4', 'pandas', 'yt_dlp', 
        'youtube_transcript_api', 'nltk', 'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Отсутствуют необходимые пакеты: {', '.join(missing_packages)}")
        logger.error("Установите их командой: pip install -r requirements.txt")
        return False
    
    # Проверка NLTK данных
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logger.warning("NLTK данные не найдены. Попытка загрузки...")
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            logger.info("NLTK данные загружены успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки NLTK данных: {e}")
            return False
    
    # Проверка spaCy модели
    try:
        import spacy
        spacy.load("ru_core_news_sm")
    except OSError:
        logger.warning("spaCy модель для русского языка не найдена")
        logger.warning("Установите командой: python -m spacy download ru_core_news_sm")
    
    logger.info("Валидация окружения завершена успешно")
    return True

# === КЭШИРОВАНИЕ ===

class CacheManager:
    """Менеджер кэширования результатов"""
    
    def __init__(self, cache_dir: str = None, duration_hours: int = None):
        if cache_dir is None:
            cache_dir = str(config.cache_dir)
        
        if duration_hours is None:
            duration_hours = config.cache_duration_hours
        
        self.cache = Cache(cache_dir)
        self.duration = timedelta(hours=duration_hours)
        self.logger = logging.getLogger(__name__)
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """Генерация ключа кэша"""
        data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        if not config.enable_caching:
            return None
        
        try:
            cached_data = self.cache.get(key)
            if cached_data:
                timestamp, data = cached_data
                if datetime.now() - timestamp < self.duration:
                    self.logger.debug(f"Данные получены из кэша: {key[:16]}...")
                    return data
                else:
                    self.cache.delete(key)
                    self.logger.debug(f"Кэш устарел, удален: {key[:16]}...")
        except Exception as e:
            self.logger.warning(f"Ошибка чтения кэша: {e}")
        
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Сохранение данных в кэш"""
        if not config.enable_caching:
            return
        
        try:
            self.cache.set(key, (datetime.now(), data))
            self.logger.debug(f"Данные сохранены в кэш: {key[:16]}...")
        except Exception as e:
            self.logger.warning(f"Ошибка записи в кэш: {e}")
    
    def clear(self) -> None:
        """Очистка кэша"""
        try:
            self.cache.clear()
            self.logger.info("Кэш очищен")
        except Exception as e:
            self.logger.warning(f"Ошибка очистки кэша: {e}")

# Глобальный менеджер кэша
cache_manager = CacheManager()

def cached(func):
    """Декоратор для кэширования результатов функций"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not config.enable_caching:
            return func(*args, **kwargs)
        
        cache_key = cache_manager.get_cache_key(func.__name__, *args, **kwargs)
        cached_result = cache_manager.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        result = func(*args, **kwargs)
        cache_manager.set(cache_key, result)
        
        return result
    
    return wrapper

# === ОБРАБОТКА ОШИБОК И ПОВТОРЫ ===

def retry_on_error(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Декоратор для автоматического повтора при ошибках"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Функция {func.__name__} не выполнена после {max_attempts} попыток: {e}")
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"Попытка {attempt + 1}/{max_attempts} неудачна: {e}. Повтор через {wait_time:.1f}с")
                    time.sleep(wait_time)
            
            return None
        
        return wrapper
    return decorator

def safe_request(url: str, **kwargs) -> Optional[requests.Response]:
    """Безопасный HTTP запрос с обработкой ошибок"""
    logger = logging.getLogger(__name__)
    
    # Настройки по умолчанию
    default_kwargs = {
        'timeout': 30,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    
    # Добавление прокси если настроен
    if config.proxies:
        default_kwargs['proxies'] = config.proxies
    
    # Объединение с пользовательскими параметрами
    request_kwargs = {**default_kwargs, **kwargs}
    
    try:
        response = requests.get(url, **request_kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.warning(f"Ошибка HTTP запроса к {url}: {e}")
        return None

# === РАБОТА С ФАЙЛАМИ ===

def save_json(data: Any, filepath: Union[str, Path], indent: int = 2) -> bool:
    """Безопасное сохранение данных в JSON"""
    logger = logging.getLogger(__name__)
    
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=str)
        
        logger.debug(f"JSON сохранен: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка сохранения JSON {filepath}: {e}")
        return False

def load_json(filepath: Union[str, Path]) -> Optional[Any]:
    """Безопасная загрузка данных из JSON"""
    logger = logging.getLogger(__name__)
    
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.debug(f"JSON загружен: {filepath}")
        return data
        
    except Exception as e:
        logger.error(f"Ошибка загрузки JSON {filepath}: {e}")
        return None

def save_pickle(data: Any, filepath: Union[str, Path]) -> bool:
    """Сохранение данных в pickle формате"""
    logger = logging.getLogger(__name__)
    
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        logger.debug(f"Pickle сохранен: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка сохранения pickle {filepath}: {e}")
        return False

def load_pickle(filepath: Union[str, Path]) -> Optional[Any]:
    """Загрузка данных из pickle формата"""
    logger = logging.getLogger(__name__)
    
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        logger.debug(f"Pickle загружен: {filepath}")
        return data
        
    except Exception as e:
        logger.error(f"Ошибка загрузки pickle {filepath}: {e}")
        return None

# === ВАЛИДАЦИЯ ДАННЫХ ===

def validate_youtube_url(url: str) -> bool:
    """Валидация YouTube URL"""
    youtube_patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/channel\/([^&\n?#\/]+)',
        r'youtube\.com\/@([^&\n?#\/]+)'
    ]
    
    import re
    return any(re.search(pattern, url) for pattern in youtube_patterns)

def extract_video_id(url: str) -> Optional[str]:
    """Извлечение ID видео из YouTube URL"""
    import re
    
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def extract_channel_id(url: str) -> Optional[str]:
    """Извлечение ID канала из YouTube URL"""
    import re
    
    patterns = [
        r'youtube\.com\/channel\/([^&\n?#\/]+)',
        r'youtube\.com\/@([^&\n?#\/]+)',
        r'youtube\.com\/c\/([^&\n?#\/]+)',
        r'youtube\.com\/user\/([^&\n?#\/]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

# === ФОРМАТИРОВАНИЕ И ОТОБРАЖЕНИЕ ===

def format_number(number: Union[int, float]) -> str:
    """Форматирование чисел для удобного отображения"""
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(int(number))

def format_duration(seconds: int) -> str:
    """Форматирование длительности в читаемый вид"""
    if seconds < 60:
        return f"{seconds}с"
    elif seconds < 3600:
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes}:{sec:02d}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        sec = seconds % 60
        return f"{hours}:{minutes:02d}:{sec:02d}"

def format_date(date_str: str) -> str:
    """Форматирование даты из различных форматов"""
    if not date_str:
        return "Не указано"
    
    # Попытка парсинга различных форматов
    formats = [
        '%Y%m%d',
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str[:len(fmt)], fmt)
            return dt.strftime('%d.%m.%Y')
        except ValueError:
            continue
    
    return date_str

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Сокращение текста до указанной длины"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

# === ПРОГРЕСС И СТАТИСТИКА ===

class ProgressTracker:
    """Отслеживание прогресса выполнения"""
    
    def __init__(self, total: int, description: str = "Обработка"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)
    
    def update(self, increment: int = 1) -> None:
        """Обновление прогресса"""
        self.current += increment
        
        if self.current % max(1, self.total // 10) == 0 or self.current == self.total:
            self._log_progress()
    
    def _log_progress(self) -> None:
        """Логирование прогресса"""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = datetime.now() - self.start_time
        
        if self.current > 0:
            estimated_total = elapsed * (self.total / self.current)
            remaining = estimated_total - elapsed
            
            self.logger.info(
                f"{self.description}: {self.current}/{self.total} "
                f"({percentage:.1f}%) - "
                f"Осталось: {str(remaining).split('.')[0]}"
            )
        else:
            self.logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")

def calculate_statistics(numbers: List[Union[int, float]]) -> Dict[str, float]:
    """Вычисление базовой статистики для числового массива"""
    if not numbers:
        return {}
    
    import statistics
    
    return {
        'count': len(numbers),
        'sum': sum(numbers),
        'mean': statistics.mean(numbers),
        'median': statistics.median(numbers),
        'min': min(numbers),
        'max': max(numbers),
        'std_dev': statistics.stdev(numbers) if len(numbers) > 1 else 0
    }

# === СИСТЕМНЫЕ УТИЛИТЫ ===

def get_system_info() -> Dict[str, str]:
    """Получение информации о системе"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': str(os.cpu_count()),
        'memory_gb': f"{psutil.virtual_memory().total / (1024**3):.1f}",
        'disk_free_gb': f"{psutil.disk_usage('.').free / (1024**3):.1f}"
    }

def cleanup_temp_files(directory: Union[str, Path], older_than_days: int = 7) -> None:
    """Очистка временных файлов старше указанного количества дней"""
    logger = logging.getLogger(__name__)
    directory = Path(directory)
    
    if not directory.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    cleaned_count = 0
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_date:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Не удалось удалить файл {file_path}: {e}")
    
    if cleaned_count > 0:
        logger.info(f"Очищено временных файлов: {cleaned_count}")

# === ИНИЦИАЛИЗАЦИЯ ===

def initialize_project_structure() -> None:
    """Инициализация структуры проекта"""
    logger = logging.getLogger(__name__)
    
    # Убеждаемся что мы в правильной папке
    base_path = Path(r'C:\youtube-analyzer')
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Создана базовая папка: {base_path}")
    
    # Создание необходимых папок
    directories = [
        base_path / 'data',
        base_path / 'reports', 
        base_path / 'logs',
        base_path / '.cache',
        base_path / 'src',
        base_path / 'templates',
        base_path / 'tests'
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        
        # Создание __init__.py для Python пакетов
        if directory.name in ['src', 'templates', 'tests']:
            init_file = directory / '__init__.py'
            if not init_file.exists():
                init_file.touch()
    
    logger.info("Структура проекта инициализирована")

# === ЭКСПОРТ ===

__all__ = [
    'setup_logging',
    'load_config', 
    'validate_environment',
    'CacheManager',
    'cache_manager',
    'cached',
    'retry_on_error',
    'safe_request',
    'save_json',
    'load_json',
    'save_pickle',
    'load_pickle',
    'validate_youtube_url',
    'extract_video_id',
    'extract_channel_id',
    'format_number',
    'format_duration',
    'format_date',
    'truncate_text',
    'ProgressTracker',
    'calculate_statistics',
    'get_system_info',
    'cleanup_temp_files',
    'initialize_project_structure'
]