from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, List

Base = declarative_base()

class Video(Base):
    """Модель для хранения данных о видео"""
    __tablename__ = "videos"
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    video_url = Column(String(255), unique=True, nullable=False, index=True)
    channel_url = Column(String(255), nullable=False, index=True)
    is_short = Column(Boolean, default=False, index=True)
    
    # Метрики
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    
    # Вычисляемые метрики
    like_ratio = Column(Float, default=0.0)
    comment_ratio = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    
    # Информация о видео
    title = Column(String(500), nullable=False)
    description = Column(Text)
    duration = Column(String(50))  # ISO 8601 format
    subtitles = Column(Text)  # Полный текст субтитров
    publish_date = Column(DateTime, nullable=False, index=True)
    thumbnail_url = Column(String(500))
    video_category = Column(String(100))
    video_quality = Column(String(20))  # 1080p, 4K, etc.
    
    # Анализ контента
    keywords = Column(JSON)  # Список ключевых слов
    top_5_keywords = Column(JSON)  # Топ-5 ключевых слов из транскрипта
    has_branding = Column(Boolean, default=False)
    has_cc = Column(Boolean, default=False)
    has_intro = Column(Boolean, default=False)
    has_outro = Column(Boolean, default=False)
    has_chapters = Column(Boolean, default=False)
    emoji_in_title = Column(Boolean, default=False)
    
    # Дополнительные метрики
    average_view_duration = Column(Float)  # В секундах
    click_through_rate = Column(Float)
    speech_speed = Column(Float)  # Символов в минуту
    links_in_description = Column(Integer, default=0)
    links_in_channel_description = Column(Integer, default=0)
    
    # Контакты
    has_pinned_comment = Column(Boolean, default=False)
    contacts_in_video = Column(JSON)  # Список найденных контактов
    contacts_in_channel = Column(JSON)
    
    # Аналитика канала
    channel_avg_views = Column(Float)
    channel_avg_likes = Column(Float)
    channel_frequency = Column(Float)  # Дней между публикациями
    channel_age = Column(Integer)  # Дней с момента создания
    
    # AI анализ
    improvement_recommendations = Column(Text)  # Рекомендации по улучшению
    success_analysis = Column(Text)  # Почему видео залетело
    content_strategy = Column(Text)  # Стратегия создания похожего контента
    
    # Служебные поля
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_checked = Column(DateTime, default=func.now())
    parse_status = Column(String(50), default="pending")  # pending, parsing, completed, error
    parse_error = Column(Text)

    def to_dict(self) -> Dict:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "video_url": self.video_url,
            "channel_url": self.channel_url,
            "is_short": self.is_short,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "like_ratio": self.like_ratio,
            "comment_ratio": self.comment_ratio,
            "engagement_rate": self.engagement_rate,
            "title": self.title,
            "description": self.description[:200] + "..." if self.description and len(self.description) > 200 else self.description,
            "duration": self.duration,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "thumbnail_url": self.thumbnail_url,
            "video_category": self.video_category,
            "has_branding": self.has_branding,
            "top_5_keywords": self.top_5_keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "parse_status": self.parse_status
        }

class Task(Base):
    """Модель для управления задачами"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    task_type = Column(String(50), nullable=False)  # search, channel_parse, video_parse, analysis
    
    # Параметры задачи
    parameters = Column(JSON)  # Входные параметры задачи
    
    # Статус и прогресс
    status = Column(String(50), default="pending")  # pending, running, paused, completed, failed
    progress = Column(Float, default=0.0)  # 0-100
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    
    # Результаты
    results = Column(JSON)  # Результаты выполнения
    error_message = Column(Text)
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    paused_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Сохранение состояния для возобновления
    checkpoint = Column(JSON)  # Данные для возобновления задачи
    
    def to_dict(self) -> Dict:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "parameters": self.parameters,
            "status": self.status,
            "progress": self.progress,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }

class Channel(Base):
    """Модель для хранения данных о каналах"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_url = Column(String(255), unique=True, nullable=False, index=True)
    channel_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Основная информация
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    # Метрики
    avg_views = Column(Float, default=0.0)
    avg_likes = Column(Float, default=0.0)
    avg_comments = Column(Float, default=0.0)
    upload_frequency = Column(Float)  # Видео в неделю
    
    # Дополнительная информация
    country = Column(String(50))
    created_date = Column(DateTime)
    thumbnail_url = Column(String(500))
    keywords = Column(JSON)
    
    # Анализ
    content_categories = Column(JSON)  # Категории контента канала
    target_audience = Column(JSON)  # Целевая аудитория
    
    # Служебные поля
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_parsed = Column(DateTime)

class SearchQuery(Base):
    """Модель для сохранения поисковых запросов"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), nullable=False, index=True)
    search_type = Column(String(50))  # keyword, channel
    filters = Column(JSON)  # Фильтры поиска
    
    # Результаты
    total_results = Column(Integer, default=0)
    parsed_results = Column(Integer, default=0)
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    last_searched = Column(DateTime)

class Analytics(Base):
    """Модель для хранения аналитических данных"""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), nullable=False)  # niche, competitor, trend
    
    # Параметры отчета
    parameters = Column(JSON)
    
    # Данные отчета
    data = Column(JSON)
    insights = Column(Text)
    recommendations = Column(Text)
    
    # Временные метки
    created_at = Column(DateTime, default=func.now())
    valid_until = Column(DateTime)  # Когда данные устареют