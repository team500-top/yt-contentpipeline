"""
YouTube Analyzer - Utility Functions
Общие утилиты и вспомогательные функции
"""
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import unicodedata
import urllib.parse

class Utils:
    """Класс с утилитарными функциями"""
    
    @staticmethod
    def format_number(num: Union[int, float, str]) -> str:
        """Форматирование чисел для отображения"""
        try:
            num = float(num) if num else 0
            if num >= 1000000000:
                return f"{num / 1000000000:.1f}B"
            elif num >= 1000000:
                return f"{num / 1000000:.1f}M"
            elif num >= 1000:
                return f"{num / 1000:.1f}K"
            else:
                return str(int(num))
        except (ValueError, TypeError):
            return "0"
    
    @staticmethod
    def format_duration(duration: str) -> str:
        """Форматирование длительности из ISO 8601 в читаемый вид"""
        if not duration:
            return "0:00"
        
        # Парсинг ISO 8601 (PT1H2M3S -> 1:02:03)
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return duration
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def parse_duration_to_seconds(duration: str) -> int:
        """Преобразование длительности в секунды"""
        if not duration:
            return 0
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    @staticmethod
    def format_date(date_str: str, short: bool = False) -> str:
        """Форматирование даты"""
        if not date_str:
            return "-"
        
        try:
            # Попробовать разные форматы даты
            date_formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                # Попробовать ISO format
                parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            if short:
                return parsed_date.strftime("%d.%m.%Y")
            else:
                return parsed_date.strftime("%d.%m.%Y %H:%M")
                
        except Exception:
            return date_str
    
    @staticmethod
    def calculate_engagement_rate(views: int, likes: int, comments: int) -> float:
        """Вычисление коэффициента вовлеченности"""
        if views == 0:
            return 0.0
        return round(((likes + comments) / views) * 100, 2)
    
    @staticmethod
    def calculate_like_ratio(views: int, likes: int) -> float:
        """Вычисление коэффициента лайков"""
        if views == 0:
            return 0.0
        return round((likes / views) * 100, 2)
    
    @staticmethod
    def calculate_comment_ratio(views: int, comments: int) -> float:
        """Вычисление коэффициента комментариев"""
        if views == 0:
            return 0.0
        return round((comments / views) * 100, 2)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Очистка текста от лишних символов"""
        if not text:
            return ""
        
        # Убрать лишние пробелы и переносы строк
        text = ' '.join(text.split())
        
        # Нормализация Unicode
        text = unicodedata.normalize('NFKC', text)
        
        return text.strip()
    
    @staticmethod
    def extract_video_id_from_url(url: str) -> Optional[str]:
        """Извлечение ID видео из YouTube URL"""
        if not url:
            return None
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Если это уже ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None
    
    @staticmethod
    def extract_channel_id_from_url(url: str) -> Optional[str]:
        """Извлечение ID канала из YouTube URL"""
        if not url:
            return None
        
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def has_emoji(text: str) -> bool:
        """Проверка наличия эмодзи в тексте"""
        if not text:
            return False
        
        # Простая проверка на наличие символов вне ASCII
        return any(ord(char) > 127 for char in text)
    
    @staticmethod
    def count_links(text: str) -> int:
        """Подсчет количества ссылок в тексте"""
        if not text:
            return 0
        
        # Поиск HTTP/HTTPS ссылок
        http_links = len(re.findall(r'https?://\S+', text))
        
        # Поиск www ссылок
        www_links = len(re.findall(r'www\.\S+', text))
        
        return http_links + www_links
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 5) -> List[str]:
        """Извлечение ключевых слов из текста"""
        if not text:
            return []
        
        # Простое извлечение слов (можно улучшить с помощью TF-IDF)
        words = re.findall(r'\b[а-яА-Яa-zA-Z]+\b', text.lower())
        
        # Стоп-слова
        stop_words = {
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так',
            'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было',
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг',
            'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж',
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'been', 'be', 'have', 'has', 'had',
            'i', 'it', 'its', 'of', 'that', 'to', 'was', 'will', 'with', 'what', 'when', 'where', 'who',
            'for', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below'
        }
        
        # Фильтрация и подсчет
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        from collections import Counter
        word_counts = Counter(filtered_words)
        
        return [word for word, _ in word_counts.most_common(top_n)]
    
    @staticmethod
    def generate_hash(text: str) -> str:
        """Генерация хеша для текста"""
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def validate_youtube_api_key(api_key: str) -> bool:
        """Валидация YouTube API ключа"""
        if not api_key or api_key in ['YOUR_API_KEY_HERE', '***', '']:
            return False
        
        # Проверка длины (обычно 39 символов)
        if len(api_key) < 30:
            return False
        
        # Проверка формата (только буквы, цифры, дефисы, подчеркивания)
        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
            return False
        
        return True
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Создание безопасного имени файла"""
        # Убрать опасные символы
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Ограничить длину
        if len(safe_name) > 100:
            name, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
            safe_name = name[:95] + ('.' + ext if ext else '')
        
        return safe_name
    
    @staticmethod
    def parse_json_safely(json_str: str, default=None) -> Any:
        """Безопасный парсинг JSON"""
        if not json_str:
            return default
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def create_video_url(video_id: str) -> str:
        """Создание URL видео"""
        return f"https://youtube.com/watch?v={video_id}"
    
    @staticmethod
    def create_channel_url(channel_id: str) -> str:
        """Создание URL канала"""
        return f"https://youtube.com/channel/{channel_id}"
    
    @staticmethod
    def time_ago(date_str: str) -> str:
        """Вычисление времени назад"""
        if not date_str:
            return "неизвестно"
        
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(date.tzinfo)
            diff = now - date
            
            if diff.days > 365:
                return f"{diff.days // 365} лет назад"
            elif diff.days > 30:
                return f"{diff.days // 30} месяцев назад"
            elif diff.days > 0:
                return f"{diff.days} дней назад"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600} часов назад"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60} минут назад"
            else:
                return "только что"
                
        except Exception:
            return "неизвестно"

class FileUtils:
    """Утилиты для работы с файлами"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Создание директории если не существует"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Получение размера файла"""
        try:
            return Path(file_path).stat().st_size
        except OSError:
            return 0
    
    @staticmethod
    def clean_temp_files(temp_dir: Union[str, Path], max_age_hours: int = 24):
        """Очистка временных файлов старше указанного времени"""
        temp_dir = Path(temp_dir)
        if not temp_dir.exists():
            return
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for file_path in temp_dir.glob('*'):
            try:
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        print(f"🗑️  Удален временный файл: {file_path.name}")
            except OSError:
                continue

class ValidationUtils:
    """Утилиты для валидации данных"""
    
    @staticmethod
    def is_valid_video_id(video_id: str) -> bool:
        """Проверка валидности YouTube video ID"""
        if not video_id:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))
    
    @staticmethod
    def is_valid_channel_id(channel_id: str) -> bool:
        """Проверка валидности YouTube channel ID"""
        if not channel_id:
            return False
        return bool(re.match(r'^UC[a-zA-Z0-9_-]{22}$', channel_id))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        if not url:
            return False
        
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """Проверка валидности YouTube URL"""
        if not ValidationUtils.is_valid_url(url):
            return False
        
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc.lower() in youtube_domains

# Создать глобальные экземпляры утилит
file_utils = FileUtils()
validation_utils = ValidationUtils()

# Экспорт основных функций для удобства
format_number = Utils.format_number
format_duration = Utils.format_duration
format_date = Utils.format_date
calculate_engagement_rate = Utils.calculate_engagement_rate
clean_text = Utils.clean_text
extract_keywords = Utils.extract_keywords

print("✅ Utils загружены успешно")