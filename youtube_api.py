import os
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import isodate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp
from urllib.parse import urlparse, parse_qs
import asyncio
from concurrent.futures import ThreadPoolExecutor

class YouTubeClient:
    """Клиент для работы с YouTube API и yt-dlp"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is required")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Настройки yt-dlp для субтитров
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ru', 'en', 'auto'],
            'subtitlesformat': 'vtt/srt/best',
            'getcomments': False,
            'format': 'best'
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Извлечение ID видео из URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def extract_channel_id(self, url: str) -> Optional[str]:
        """Извлечение ID канала из URL"""
        # Обработка различных форматов URL каналов
        if '@' in url:
            # Handle @username format
            username = url.split('@')[-1].split('/')[0]
            return self._get_channel_id_by_username(username)
        
        patterns = [
            r'channel\/([UC][\w-]{22})',
            r'c\/([^\/]+)',
            r'user\/([^\/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                if pattern.startswith('channel'):
                    return match.group(1)
                else:
                    # Для c/ и user/ нужно получить ID через API
                    return self._get_channel_id_by_custom_url(match.group(1))
        
        return None
    
    def _get_channel_id_by_username(self, username: str) -> Optional[str]:
        """Получение ID канала по username"""
        try:
            response = self.youtube.search().list(
                part="snippet",
                q=f"@{username}",
                type="channel",
                maxResults=1
            ).execute()
            
            if response['items']:
                return response['items'][0]['snippet']['channelId']
        except HttpError:
            pass
        return None
    
    def _get_channel_id_by_custom_url(self, custom_url: str) -> Optional[str]:
        """Получение ID канала по custom URL"""
        try:
            response = self.youtube.search().list(
                part="snippet",
                q=custom_url,
                type="channel",
                maxResults=1
            ).execute()
            
            if response['items']:
                return response['items'][0]['snippet']['channelId']
        except HttpError:
            pass
        return None
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        video_type: str = "all",
        order: str = "relevance",
        published_after: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Поиск видео по ключевым словам с расширенными фильтрами"""
        videos = []
        next_page_token = None
        
        # Определение типа видео
        video_duration = None
        if video_type == "shorts":
            video_duration = "short"  # < 4 минут
        elif video_type == "long":
            video_duration = "long"   # > 20 минут
        elif kwargs.get('duration'):
            video_duration = kwargs['duration']
        
        while len(videos) < max_results:
            try:
                request_params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": min(50, max_results - len(videos)),
                    "order": order,
                    "pageToken": next_page_token,
                    "regionCode": kwargs.get('regionCode', 'RU'),
                    "relevanceLanguage": kwargs.get('relevanceLanguage', 'ru')
                }
                
                if video_duration:
                    request_params["videoDuration"] = video_duration
                
                if published_after:
                    request_params["publishedAfter"] = published_after.isoformat() + "Z"
                
                # Дополнительные фильтры
                if kwargs.get('videoDefinition'):
                    request_params["videoDefinition"] = kwargs['videoDefinition']
                
                if kwargs.get('videoDimension'):
                    request_params["videoDimension"] = kwargs['videoDimension']
                
                if kwargs.get('videoCaption'):
                    request_params["videoCaption"] = kwargs['videoCaption']
                
                response = self.youtube.search().list(**request_params).execute()
                
                for item in response.get("items", []):
                    video_data = {
                        "video_id": item["id"]["videoId"],
                        "video_url": f"https://youtube.com/watch?v={item['id']['videoId']}",
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "channel_id": item["snippet"]["channelId"],
                        "channel_title": item["snippet"]["channelTitle"],
                        "channel_url": f"https://youtube.com/channel/{item['snippet']['channelId']}",
                        "publish_date": item["snippet"]["publishedAt"],
                        "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"]
                    }
                    videos.append(video_data)
                
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"YouTube API error: {e}")
                break
            
            # Небольшая задержка между запросами
            await asyncio.sleep(0.5)
        
        return videos[:max_results]
    
    async def get_channel_videos(
        self,
        channel_url: str,
        max_results: int = 50,
        video_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """Получение видео с канала"""
        channel_id = self.extract_channel_id(channel_url)
        if not channel_id:
            raise ValueError("Invalid channel URL")
        
        # Получение uploads playlist ID
        try:
            channel_response = self.youtube.channels().list(
                part="contentDetails,snippet,statistics",
                id=channel_id
            ).execute()
            
            if not channel_response["items"]:
                raise ValueError("Channel not found")
            
            channel_info = channel_response["items"][0]
            uploads_playlist_id = channel_info["contentDetails"]["relatedPlaylists"]["uploads"]
            
        except HttpError as e:
            print(f"Error getting channel info: {e}")
            raise
        
        # Получение видео из плейлиста
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            try:
                playlist_response = self.youtube.playlistItems().list(
                    part="snippet",
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response.get("items", []):
                    video_data = {
                        "video_id": item["snippet"]["resourceId"]["videoId"],
                        "video_url": f"https://youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "channel_id": channel_id,
                        "channel_title": channel_info["snippet"]["title"],
                        "channel_url": channel_url,
                        "publish_date": item["snippet"]["publishedAt"],
                        "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"]
                    }
                    videos.append(video_data)
                
                next_page_token = playlist_response.get("nextPageToken")
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"Error getting playlist items: {e}")
                break
            
            await asyncio.sleep(0.5)
        
        return videos[:max_results]
    
    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Получение детальной информации о видео"""
        try:
            # Получение основной информации через API
            video_response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails,status,recordingDetails,topicDetails",
                id=video_id
            ).execute()
            
            if not video_response["items"]:
                raise ValueError("Video not found")
            
            video_info = video_response["items"][0]
            
            # Парсинг длительности
            duration = isodate.parse_duration(video_info["contentDetails"]["duration"])
            duration_seconds = int(duration.total_seconds())
            
            # Определение типа видео (short или обычное)
            is_short = duration_seconds <= 60
            
            # Базовые данные
            details = {
                "video_id": video_id,
                "video_url": f"https://youtube.com/watch?v={video_id}",
                "title": video_info["snippet"]["title"],
                "description": video_info["snippet"]["description"],
                "channel_id": video_info["snippet"]["channelId"],
                "channel_title": video_info["snippet"]["channelTitle"],
                "channel_url": f"https://youtube.com/channel/{video_info['snippet']['channelId']}",
                "publish_date": video_info["snippet"]["publishedAt"],
                "thumbnail_url": video_info["snippet"]["thumbnails"]["maxres"]["url"] if "maxres" in video_info["snippet"]["thumbnails"] else video_info["snippet"]["thumbnails"]["high"]["url"],
                "duration": video_info["contentDetails"]["duration"],
                "duration_seconds": duration_seconds,
                "is_short": is_short,
                "views": int(video_info["statistics"].get("viewCount", 0)),
                "likes": int(video_info["statistics"].get("likeCount", 0)),
                "comments": int(video_info["statistics"].get("commentCount", 0)),
                "video_category": video_info["snippet"].get("categoryId"),
                "tags": video_info["snippet"].get("tags", []),
                "has_captions": video_info["contentDetails"].get("caption") == "true",
                "video_quality": video_info["contentDetails"].get("definition", "sd"),
                "is_live": video_info["snippet"].get("liveBroadcastContent") == "live"
            }
            
            # Проверка на эмодзи в заголовке
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U00002702-\U000027B0"
                "\U000024C2-\U0001F251"
                "]+", flags=re.UNICODE)
            
            details["emoji_in_title"] = bool(emoji_pattern.search(details["title"]))
            
            # Вычисление метрик вовлеченности
            if details["views"] > 0:
                details["like_ratio"] = (details["likes"] / details["views"]) * 100
                details["comment_ratio"] = (details["comments"] / details["views"]) * 100
                details["engagement_rate"] = ((details["likes"] + details["comments"]) / details["views"]) * 100
            else:
                details["like_ratio"] = 0
                details["comment_ratio"] = 0
                details["engagement_rate"] = 0
            
            # Получение дополнительной информации через yt-dlp
            try:
                ydl_data = await self._get_ydl_data(video_id)
                if ydl_data:
                    details.update(ydl_data)
            except Exception as e:
                print(f"Error getting yt-dlp data: {e}")
            
            return details
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            raise
    
    async def _get_ydl_data(self, video_id: str) -> Dict[str, Any]:
        """Получение дополнительных данных через yt-dlp с улучшенной поддержкой субтитров"""
        loop = asyncio.get_event_loop()
        
        def extract_info():
            # Расширенные настройки для субтитров
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'allsubtitles': True,  # Получить все доступные субтитры
                'subtitleslangs': ['all'],  # Все языки
                'subtitlesformat': 'vtt/srt/best',
                'getcomments': False,
                'format': 'best',
                'ignoreerrors': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(
                        f"https://youtube.com/watch?v={video_id}",
                        download=False
                    )
                    return info
                except Exception as e:
                    print(f"yt-dlp error: {e}")
                    return None
        
        info = await loop.run_in_executor(self.executor, extract_info)
        
        if not info:
            return {}
        
        # Извлечение дополнительных данных
        ydl_data = {}
        
        # Субтитры - улучшенная проверка
        has_subtitles = False
        subtitle_text = ""
        subtitle_languages = []
        
        # Проверка автоматических субтитров
        if info.get("automatic_captions"):
            has_subtitles = True
            ydl_data["has_automatic_captions"] = True
            auto_langs = list(info["automatic_captions"].keys())
            subtitle_languages.extend(auto_langs)
            
            # Попытка получить текст субтитров
            for lang in ['ru', 'en']:
                if lang in info["automatic_captions"]:
                    # Здесь можно добавить код для загрузки текста субтитров
                    ydl_data["subtitle_language"] = lang
                    break
        
        # Проверка обычных субтитров
        if info.get("subtitles"):
            has_subtitles = True
            ydl_data["has_manual_subtitles"] = True
            manual_langs = list(info["subtitles"].keys())
            subtitle_languages.extend(manual_langs)
        
        ydl_data["has_subtitles"] = has_subtitles
        ydl_data["has_cc"] = has_subtitles  # Для совместимости
        ydl_data["subtitle_languages"] = list(set(subtitle_languages))
        
        # Главы видео
        if info.get("chapters"):
            ydl_data["has_chapters"] = True
            ydl_data["chapters_count"] = len(info["chapters"])
            ydl_data["chapter_titles"] = [ch.get("title", "") for ch in info["chapters"]]
        else:
            ydl_data["has_chapters"] = False
        
        # Теги
        if info.get("tags"):
            ydl_data["tags"] = info["tags"][:20]  # Первые 20 тегов
        
        # Описание канала
        if info.get("channel_description"):
            ydl_data["channel_description"] = info["channel_description"][:1000]
        
        # Возрастные ограничения
        if info.get("age_limit"):
            ydl_data["age_restricted"] = info["age_limit"] > 0
        
        # Категория
        if info.get("categories"):
            ydl_data["categories"] = info["categories"]
        
        # Является ли видео прямой трансляцией
        ydl_data["is_live"] = info.get("is_live", False)
        
        # Количество просмотров в прямом эфире
        if info.get("concurrent_view_count"):
            ydl_data["live_viewers"] = info["concurrent_view_count"]
        
        # Проверка на наличие спонсорских блоков
        if info.get("sponsorblock_chapters"):
            ydl_data["has_sponsorblock"] = True
            ydl_data["sponsorblock_count"] = len(info["sponsorblock_chapters"])
        
        # Информация о качестве видео
        formats = info.get("formats", [])
        if formats:
            # Найти максимальное качество
            max_height = 0
            for fmt in formats:
                if fmt.get("height"):
                    max_height = max(max_height, fmt["height"])
            
            if max_height >= 2160:
                ydl_data["max_quality"] = "4K"
            elif max_height >= 1440:
                ydl_data["max_quality"] = "2K"
            elif max_height >= 1080:
                ydl_data["max_quality"] = "1080p"
            elif max_height >= 720:
                ydl_data["max_quality"] = "720p"
            else:
                ydl_data["max_quality"] = "SD"
        
        # Проверка на наличие HDR
        for fmt in formats:
            if fmt.get("dynamic_range") == "HDR":
                ydl_data["has_hdr"] = True
                break
        
        return ydl_data
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Получение информации о канале"""
        try:
            response = self.youtube.channels().list(
                part="snippet,statistics,contentDetails,brandingSettings",
                id=channel_id
            ).execute()
            
            if not response["items"]:
                raise ValueError("Channel not found")
            
            channel = response["items"][0]
            
            # Извлечение контактов из описания канала
            description = channel["snippet"].get("description", "")
            contacts = self._extract_contacts(description)
            
            return {
                "channel_id": channel_id,
                "channel_url": f"https://youtube.com/channel/{channel_id}",
                "title": channel["snippet"]["title"],
                "description": description,
                "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
                "video_count": int(channel["statistics"].get("videoCount", 0)),
                "view_count": int(channel["statistics"].get("viewCount", 0)),
                "created_date": channel["snippet"]["publishedAt"],
                "country": channel["snippet"].get("country"),
                "thumbnail_url": channel["snippet"]["thumbnails"]["high"]["url"],
                "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"],
                "custom_url": channel["snippet"].get("customUrl"),
                "keywords": channel["brandingSettings"]["channel"].get("keywords", "").split() if "brandingSettings" in channel else [],
                "contacts": contacts
            }
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            raise
    
    def _extract_contacts(self, text: str) -> Dict[str, List[str]]:
        """Извлечение контактной информации из текста"""
        contacts = {
            "emails": [],
            "phones": [],
            "social_media": {}
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contacts["emails"] = re.findall(email_pattern, text)
        
        # Телефоны
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3,5}[-\s\.]?[0-9]{3,5}'
        contacts["phones"] = re.findall(phone_pattern, text)
        
        # Социальные сети
        social_patterns = {
            'instagram': r'instagram\.com/[\w.]+',
            'telegram': r't\.me/[\w]+|telegram\.me/[\w]+',
            'twitter': r'twitter\.com/[\w]+',
            'facebook': r'facebook\.com/[\w.]+',
            'tiktok': r'tiktok\.com/@[\w.]+',
            'vk': r'vk\.com/[\w]+'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, text.lower())
            if matches:
                contacts["social_media"][platform] = matches
        
        return contacts
    
    def get_video_category_name(self, category_id: str) -> str:
        """Получение названия категории видео"""
        try:
            response = self.youtube.videoCategories().list(
                part="snippet",
                id=category_id,
                hl="ru"
            ).execute()
            
            if response["items"]:
                return response["items"][0]["snippet"]["title"]
        except:
            pass
        
        return "Unknown"