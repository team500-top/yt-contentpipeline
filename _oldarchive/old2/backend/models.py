"""
YouTube Analyzer - Pydantic Models
Модели данных для API запросов и ответов
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ============ ENUMS ============

class TaskStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

class VideoType(str, Enum):
    SHORT = "short"
    LONG = "long"

class OrderBy(str, Enum):
    RELEVANCE = "relevance"
    DATE = "date"
    VIEW_COUNT = "viewCount"
    RATING = "rating"

# ============ REQUEST MODELS ============

class TaskCreate(BaseModel):
    """Модель для создания новой задачи"""
    keywords: List[str] = Field(default=[], description="Список ключевых запросов")
    channels: List[str] = Field(default=[], description="Список URL каналов")
    order_by: OrderBy = Field(default=OrderBy.RELEVANCE, description="Порядок сортировки")
    max_videos_per_source: int = Field(default=20, ge=1, le=100, description="Максимум видео с источника")
    
    @field_validator('keywords')
    def keywords_not_empty_strings(cls, v):
        return [keyword.strip() for keyword in v if keyword.strip()]
    
    @field_validator('channels')
    def channels_valid_urls(cls, v):
        valid_channels = []
        for channel in v:
            channel = channel.strip()
            if channel and ('youtube.com' in channel or 'youtu.be' in channel):
                valid_channels.append(channel)
        return valid_channels

class ConfigUpdate(BaseModel):
    """Модель для обновления конфигурации"""
    youtube_api_key: Optional[str] = None
    max_long_videos_channel: Optional[int] = Field(None, ge=1, le=500)
    max_long_videos_search: Optional[int] = Field(None, ge=1, le=500)
    max_shorts_channel: Optional[int] = Field(None, ge=1, le=500)
    max_shorts_search: Optional[int] = Field(None, ge=1, le=500)
    whisper_model: Optional[str] = Field(None, pattern=r'^(tiny|base|small|medium|large)$')
    max_transcript_length: Optional[int] = Field(None, ge=1000, le=100000)

class VideoSearch(BaseModel):
    """Модель для поиска видео"""
    query: str = Field(..., min_length=1, max_length=200)
    max_results: int = Field(default=10, ge=1, le=50)
    order: OrderBy = Field(default=OrderBy.RELEVANCE)
    video_type: Optional[VideoType] = None

# ============ RESPONSE MODELS ============

class TaskCreateResponse(BaseModel):
    """Ответ при создании задачи"""
    task_id: str
    status: TaskStatus
    message: str

class TaskStatusResponse(BaseModel):
    """Статус задачи"""
    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0)
    total_items: int = Field(ge=0)
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @property
    def progress_percentage(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.progress / self.total_items) * 100

class VideoResponse(BaseModel):
    """Модель видео для API ответов"""
    video_id: str
    title: str
    channel_id: str
    channel_title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_short: bool = False
    views: int = 0
    likes: int = 0
    comments: int = 0
    like_ratio: Optional[float] = None
    comment_ratio: Optional[float] = None
    engagement_rate: Optional[float] = None
    publish_date: Optional[str] = None
    thumbnail_url: Optional[str] = None
    has_cc: bool = False
    video_quality: Optional[str] = None
    category_id: Optional[str] = None
    tags: List[str] = []
    keywords: List[str] = []
    has_branding: bool = False
    speech_speed: Optional[float] = None
    has_intro: bool = False
    has_outro: bool = False
    recommendations: Optional[str] = None
    success_analysis: Optional[str] = None
    analyzed_at: Optional[datetime] = None
    task_id: Optional[str] = None

class ChannelResponse(BaseModel):
    """Модель канала для API ответов"""
    channel_id: str
    channel_title: str
    channel_url: Optional[str] = None
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
    created_at: Optional[str] = None
    avg_views: Optional[float] = None
    avg_likes: Optional[float] = None
    analyzed_videos: int = 0
    last_updated: Optional[datetime] = None

class StatisticsResponse(BaseModel):
    """Общая статистика системы"""
    total_videos: int = 0
    total_channels: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    avg_engagement: float = 0.0
    videos_by_type: Dict[str, int] = {}
    top_channels: List[Dict[str, Any]] = []
    recent_activity: List[Dict[str, Any]] = []

class SearchResponse(BaseModel):
    """Результат поиска видео"""
    videos: List[VideoResponse]
    total_count: int
    query: str
    search_params: Dict[str, Any]

class ExportResponse(BaseModel):
    """Ответ при экспорте данных"""
    filename: str
    status: str
    created_at: datetime
    file_size: Optional[int] = None
    records_count: Optional[int] = None

class AnalysisResponse(BaseModel):
    """Результат анализа видео"""
    video_id: str
    engagement_metrics: Dict[str, float]
    content_analysis: Dict[str, Any]
    recommendations: List[str]
    success_factors: List[str]
    analysis_date: datetime

# ============ DATABASE MODELS ============

class VideoDB(BaseModel):
    """Модель видео для базы данных"""
    video_id: str
    channel_id: str
    channel_title: Optional[str] = None
    title: str
    description: Optional[str] = None
    duration: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_short: bool = False
    views: int = 0
    likes: int = 0
    comments: int = 0
    publish_date: Optional[str] = None
    thumbnail_url: Optional[str] = None
    has_cc: bool = False
    video_quality: Optional[str] = "sd"
    tags: Optional[str] = None  # JSON string
    category_id: Optional[str] = None
    transcript: Optional[str] = None
    transcript_source: Optional[str] = None
    keywords: Optional[str] = None  # JSON string
    has_branding: bool = False
    speech_speed: Optional[float] = None
    has_intro: bool = False
    has_outro: bool = False
    like_ratio: Optional[float] = None
    comment_ratio: Optional[float] = None
    engagement_rate: Optional[float] = None
    recommendations: Optional[str] = None
    success_analysis: Optional[str] = None
    task_id: Optional[str] = None
    analyzed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ChannelDB(BaseModel):
    """Модель канала для базы данных"""
    channel_id: str
    channel_title: str
    channel_url: Optional[str] = None
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
    created_at: Optional[str] = None
    avg_views: Optional[float] = None
    avg_likes: Optional[float] = None
    last_updated: Optional[str] = None

class TaskDB(BaseModel):
    """Модель задачи для базы данных"""
    task_id: str
    task_type: str = "analysis"
    status: str = "created"
    progress: int = 0
    total_items: int = 0
    config: Optional[str] = None  # JSON string
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# ============ UTILITY MODELS ============

class APIResponse(BaseModel):
    """Стандартный формат API ответа"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class FilterParams(BaseModel):
    """Параметры фильтрации"""
    search: Optional[str] = None
    video_type: Optional[VideoType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_views: Optional[int] = Field(None, ge=0)
    max_views: Optional[int] = Field(None, ge=0)
    min_engagement: Optional[float] = Field(None, ge=0, le=100)
    channel_id: Optional[str] = None

# ============ VALIDATORS ============

def validate_video_id(video_id: str) -> str:
    """Валидация YouTube video ID"""
    if len(video_id) != 11:
        raise ValueError("Неверный формат video_id")
    return video_id

def validate_channel_id(channel_id: str) -> str:
    """Валидация YouTube channel ID"""
    if not (channel_id.startswith('UC') and len(channel_id) == 24):
        raise ValueError("Неверный формат channel_id")
    return channel_id

# Применение валидаторов к моделям
@field_validator('video_id')
def validate_video_field(cls, v):
    return validate_video_id(v)

@field_validator('channel_id')
def validate_channel_field(cls, v):
    return validate_channel_id(v)

print("✅ Модели данных загружены успешно")