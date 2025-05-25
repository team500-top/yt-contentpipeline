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
        
        # Настройки yt-dlp
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ru', 'en'],
            'subtitlesformat': 'vtt',
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
        published_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Поиск видео по ключевым словам"""
        videos = []
        next_page_token = None
        
        # Определение типа видео
        video_duration = None
        if video_type == "shorts":
            video_duration = "short"  # < 4 минут
        elif video_type == "long":
            video_duration = "long"   # > 20 минут
        
        while len(videos) < max_results:
            try:
                request_params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "maxResults": min(50, max_results - len(videos)),
                    "order": order,
                    "pageToken": next_page_token
                }
                
                if video_duration:
                    request_params["videoDuration"] = video_duration
                
                if published_after:
                    request_params["publishedAfter"] = published_after.isoformat() + "Z"
                
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
                part="snippet,statistics,contentDetails,status",
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
        """Получение дополнительных данных через yt-dlp"""
        loop = asyncio.get_event_loop()
        
        def extract_info():
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
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
        
        # Субтитры
        if info.get("subtitles") or info.get("automatic_captions"):
            ydl_data["has_subtitles"] = True
            # Здесь можно добавить код для загрузки и обработки субтитров
        
        # Главы видео
        if info.get("chapters"):
            ydl_data["has_chapters"] = True
            ydl_data["chapters_count"] = len(info["chapters"])
        
        # Информация о спонсорских сегментах (если доступно)
        if info.get("sponsorblock_chapters"):
            ydl_data["has_sponsorblock"] = True
        
        return ydl_data
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Получение информации о канале"""
        try:
            response = self.youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            ).execute()
            
            if not response["items"]:
                raise ValueError("Channel not found")
            
            channel = response["items"][0]
            
            return {
                "channel_id": channel_id,
                "channel_url": f"https://youtube.com/channel/{channel_id}",
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
                "video_count": int(channel["statistics"].get("videoCount", 0)),
                "view_count": int(channel["statistics"].get("viewCount", 0)),
                "created_date": channel["snippet"]["publishedAt"],
                "country": channel["snippet"].get("country"),
                "thumbnail_url": channel["snippet"]["thumbnails"]["high"]["url"],
                "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"]
            }
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            raise
    
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