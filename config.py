#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация для YouTube Competitor Analysis Tool
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

@dataclass
class Config:
    """Класс конфигурации приложения"""
    
    # === API НАСТРОЙКИ ===
    youtube_api_key: Optional[str] = os.getenv('YOUTUBE_API_KEY')
    youtube_cookies_file: str = os.getenv('YOUTUBE_COOKIES_FILE', 'cookies.txt')
    
    # === ПРОКСИ НАСТРОЙКИ ===
    http_proxy: Optional[str] = os.getenv('HTTP_PROXY')
    https_proxy: Optional[str] = os.getenv('HTTPS_PROXY')
    
    # === ОГРАНИЧЕНИЯ ПАРСИНГА ===
    max_videos_per_keyword: int = int(os.getenv('MAX_VIDEOS_PER_KEYWORD', '10'))
    max_total_videos: int = int(os.getenv('MAX_TOTAL_VIDEOS', '50'))
    max_channels_to_analyze: int = int(os.getenv('MAX_CHANNELS_TO_ANALYZE', '20'))
    
    # === ЗАДЕРЖКИ ===
    request_delay: float = float(os.getenv('REQUEST_DELAY', '2.0'))
    api_request_delay: float = float(os.getenv('API_REQUEST_DELAY', '1.0'))
    error_retry_delay: float = float(os.getenv('ERROR_RETRY_DELAY', '5.0'))
    
    # === ОБРАБОТКА КОНТЕНТА ===
    enable_transcript_extraction: bool = os.getenv('ENABLE_TRANSCRIPT_EXTRACTION', 'true').lower() == 'true'
    enable_content_analysis: bool = os.getenv('ENABLE_CONTENT_ANALYSIS', 'true').lower() == 'true'
    enable_sentiment_analysis: bool = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'false').lower() == 'true'
    
    # === ФОРМАТЫ ВЫВОДА ===
    excel_output_enabled: bool = os.getenv('EXCEL_OUTPUT_ENABLED', 'true').lower() == 'true'
    json_output_enabled: bool = os.getenv('JSON_OUTPUT_ENABLED', 'true').lower() == 'true'
    charts_enabled: bool = os.getenv('CHARTS_ENABLED', 'true').lower() == 'true'
    
    # === ЛОГИРОВАНИЕ ===
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', 'logs/youtube_analysis.log')
    
    # === ПАРАЛЛЕЛЬНАЯ ОБРАБОТКА ===
    max_workers: int = int(os.getenv('MAX_WORKERS', '4'))
    enable_parallel_processing: bool = os.getenv('ENABLE_PARALLEL_PROCESSING', 'true').lower() == 'true'
    
    # === КЭШИРОВАНИЕ ===
    enable_caching: bool = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    cache_duration_hours: int = int(os.getenv('CACHE_DURATION_HOURS', '24'))
    
    # === ПУТИ К ПАПКАМ ===
    project_root: Path = Path(r'C:\youtube-analyzer')
    data_dir: Path = Path(r'C:\youtube-analyzer\data')
    reports_dir: Path = Path(r'C:\youtube-analyzer\reports')
    logs_dir: Path = Path(r'C:\youtube-analyzer\logs')
    cache_dir: Path = Path(r'C:\youtube-analyzer\.cache')
    
    def __post_init__(self):
        """Создание необходимых папок"""
        for directory in [self.data_dir, self.reports_dir, self.logs_dir, self.cache_dir]:
            directory.mkdir(exist_ok=True)
    
    @property
    def proxies(self) -> Dict[str, str]:
        """Возвращает словарь прокси для requests"""
        proxies = {}
        if self.http_proxy:
            proxies['http'] = self.http_proxy
        if self.https_proxy:
            proxies['https'] = self.https_proxy
        return proxies
    
    @property
    def has_youtube_api(self) -> bool:
        """Проверяет наличие YouTube API ключа"""
        return bool(self.youtube_api_key and self.youtube_api_key.strip())
    
    @property
    def has_cookies(self) -> bool:
        """Проверяет наличие файла cookies"""
        return Path(self.youtube_cookies_file).exists()
    
    @property
    def has_proxy(self) -> bool:
        """Проверяет настройку прокси"""
        return bool(self.http_proxy or self.https_proxy)

# === КОНСТАНТЫ ===

class YouTubeConstants:
    """Константы для работы с YouTube"""
    
    # Лимиты API
    API_QUOTA_LIMIT_PER_DAY = 10000
    API_SEARCH_COST = 100
    API_VIDEO_DETAILS_COST = 1
    API_CHANNEL_DETAILS_COST = 1
    
    # Форматы видео
    VIDEO_DURATION_SHORT = 60  # Shorts <= 60 секунд
    VIDEO_DURATION_MEDIUM = 600  # Средние видео <= 10 минут
    VIDEO_DURATION_LONG = 3600  # Длинные видео <= 1 час
    
    # User Agents для web scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    # Языки для субтитров
    SUBTITLE_LANGUAGES = ['ru', 'en', 'auto']
    
    # Домены продуктов для анализа
    PRODUCT_DOMAINS = [
        'gumroad.com', 'getcourse.ru', 'teachable.com', 'udemy.com',
        'boosty.to', 'patreon.com', 'youtube.com/channel/UC', 'tinkoff.ru',
        'sberbank.ru', 'alfabank.ru', 'tg.me', 'telegram.me'
    ]

class ContentAnalysisConstants:
    """Константы для анализа контента"""
    
    # Форматы контента
    CONTENT_FORMATS = {
        'обзор': ['обзор', 'ревью', 'review', 'тест', 'сравнение'],
        'туториал': ['как', 'урок', 'tutorial', 'гайд', 'guide', 'пошагово'],
        'интервью': ['интервью', 'беседа', 'разговор', 'интерв'],
        'новости': ['новости', 'news', 'обновление', 'релиз'],
        'мнение': ['мнение', 'opinion', 'думаю', 'считаю', 'взгляд'],
        'кейс': ['кейс', 'case', 'опыт', 'результат', 'история'],
        'развлечение': ['приколы', 'funny', 'юмор', 'смешно', 'угар'],
        'стрим': ['стрим', 'live', 'прямой эфир', 'онлайн']
    }
    
    # Индикаторы проблем
    PROBLEM_INDICATORS = [
        'проблема', 'ошибка', 'сложность', 'трудность', 'препятствие',
        'как решить', 'как избежать', 'что делать', 'помочь', 'решение',
        'не получается', 'не работает', 'баг', 'глюк', 'исправить'
    ]
    
    # Паттерны CTA
    CTA_PATTERNS = {
        'subscription': [
            'подписывайтесь', 'subscribe', 'подписка', 'подпишись',
            'жми на колокольчик', 'включи уведомления'
        ],
        'engagement': [
            'лайк', 'like', 'комментарий', 'comment', 'ставьте лайк',
            'пишите в комментариях', 'делитесь', 'share'
        ],
        'traffic': [
            'ссылка в описании', 'переходите по ссылке', 'link in bio',
            'ссылка ниже', 'подробности в описании', 'больше информации'
        ],
        'sales': [
            'купить', 'buy', 'заказать', 'order', 'скидка', 'акция',
            'предложение', 'цена', 'стоимость', 'покупайте'
        ]
    }
    
    # Трендовые слова
    TRENDING_KEYWORDS = [
        'ai', 'искусственный интеллект', 'нейросети', 'chatgpt', 'gpt',
        'криптовалюта', 'блокчейн', 'nft', 'метавселенная', 'web3',
        'удаленная работа', 'фриланс', 'онлайн бизнес', 'самозанятый',
        'тренд', 'хайп', '2025', 'новый', 'инновации', 'технологии'
    ]
    
    # Аудитория
    AUDIENCE_INDICATORS = {
        'начинающие': ['для начинающих', 'с нуля', 'базовый', 'основы', 'новичок'],
        'профессионалы': ['про', 'профессиональный', 'продвинутый', 'эксперт', 'специалист'],
        'бизнес': ['бизнес', 'предприниматель', 'стартап', 'доход', 'заработок'],
        'молодежь': ['тренды', 'хайп', 'новое поколение', 'студент', 'школьник'],
        'женщины': ['для женщин', 'мама', 'красота', 'мода', 'девушки'],
        'мужчины': ['для мужчин', 'технологии', 'гаджеты', 'спорт', 'авто'],
        'геймеры': ['игра', 'game', 'геймер', 'стрим', 'летсплей'],
        'дети': ['детям', 'детский', 'малыши', 'развивающий', 'обучающий']
    }

class ExcelStylesConfig:
    """Конфигурация стилей для Excel отчетов"""
    
    # Цвета
    HEADER_COLOR = "366092"  # Синий
    SUB_HEADER_COLOR = "D9E2F3"  # Светло-синий
    ACCENT_COLOR = "70AD47"  # Зеленый
    WARNING_COLOR = "FFC000"  # Желтый
    ERROR_COLOR = "C55A5A"  # Красный
    
    # Шрифты
    HEADER_FONT_SIZE = 12
    CONTENT_FONT_SIZE = 10
    FONT_NAME = "Calibri"
    
    # Размеры столбцов (в символах)
    COLUMN_WIDTHS = {
        'URL': 50,
        'Название': 60,
        'Описание': 80,
        'Канал': 30,
        'Дата': 15,
        'Просмотры': 15,
        'Лайки': 12,
        'Комментарии': 12,
        'Длительность': 12,
        'Теги': 40,
        'CTA': 50,
        'Мнение': 60
    }

# Создание глобального объекта конфигурации
config = Config()

# === ВАЛИДАЦИЯ КОНФИГУРАЦИИ ===

def validate_config() -> List[str]:
    """Валидация конфигурации, возвращает список предупреждений"""
    warnings = []
    
    # Проверка API ключа
    if not config.has_youtube_api:
        warnings.append("YouTube API ключ не настроен. Будет использоваться только web scraping.")
    
    # Проверка cookies
    if not config.has_cookies:
        warnings.append("Файл cookies.txt не найден. Возможны ограничения при парсинге.")
    
    # Проверка лимитов
    if config.max_total_videos > 200:
        warnings.append("Большое количество видео для анализа может замедлить работу.")
    
    if config.max_workers > 8:
        warnings.append("Большое количество потоков может привести к блокировкам.")
    
    # Проверка папок
    for directory in [config.data_dir, config.reports_dir, config.logs_dir]:
        if not directory.exists():
            warnings.append(f"Папка {directory} не существует и будет создана.")
    
    return warnings

def get_effective_config() -> Dict:
    """Возвращает текущую конфигурацию в виде словаря"""
    return {
        'API настройки': {
            'YouTube API': 'Настроен' if config.has_youtube_api else 'Не настроен',
            'Cookies файл': 'Есть' if config.has_cookies else 'Отсутствует',
            'Прокси': 'Настроен' if config.has_proxy else 'Не настроен'
        },
        'Лимиты': {
            'Максимум видео': config.max_total_videos,
            'Максимум каналов': config.max_channels_to_analyze,
            'Видео на ключевое слово': config.max_videos_per_keyword
        },
        'Производительность': {
            'Параллельные потоки': config.max_workers,
            'Задержка запросов': f"{config.request_delay}с",
            'Кэширование': 'Включено' if config.enable_caching else 'Выключено'
        },
        'Функции': {
            'Извлечение субтитров': 'Включено' if config.enable_transcript_extraction else 'Выключено',
            'Анализ контента': 'Включено' if config.enable_content_analysis else 'Выключено',
            'Анализ тональности': 'Включено' if config.enable_sentiment_analysis else 'Выключено'
        },
        'Вывод': {
            'Excel отчеты': 'Включено' if config.excel_output_enabled else 'Выключено',
            'JSON отчеты': 'Включено' if config.json_output_enabled else 'Выключено',
            'Графики': 'Включено' if config.charts_enabled else 'Выключено'
        }
    }