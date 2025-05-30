"""
Модуль для парсинга YouTube видео и каналов
"""
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import json
from typing import List, Dict, Optional, Tuple
import time

class YouTubeParser:
    """Парсер YouTube API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.request_count = 0
        
    def extract_channel_id(self, channel_url: str) -> Optional[str]:
        """Извлечь ID канала из URL"""
        # Паттерны для различных форматов URL каналов
        patterns = [
            r'youtube\.com/channel/([\w-]+)',
            r'youtube\.com/@([\w-]+)',
            r'youtube\.com/c/([\w-]+)',
            r'youtube\.com/user/([\w-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, channel_url)
            if match:
                identifier = match.group(1)
                
                # Если это @username или /c/ или /user/, нужно получить channel ID
                if '@' in channel_url or '/c/' in channel_url or '/user/' in channel_url:
                    try:
                        response = self.youtube.search().list(
                            part='snippet',
                            q=identifier,
                            type='channel',
                            maxResults=1
                        ).execute()
                        
                        if response['items']:
                            return response['items'][0]['snippet']['channelId']
                    except Exception as e:
                        print(f"Ошибка при получении ID канала: {e}")
                        return None
                else:
                    return identifier
        
        return None
    
    def search_videos(self, query: str, max_results: int, order: str = 'relevance') -> List[Dict]:
        """Поиск видео по ключевому запросу"""
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            try:
                request = self.youtube.search().list(
                    part='id,snippet',
                    q=query,
                    type='video',
                    maxResults=min(50, max_results - len(videos)),
                    order=order,
                    pageToken=next_page_token
                )
                response = request.execute()
                self.request_count += 1
                
                for item in response['items']:
                    video_data = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'channel_id': item['snippet']['channelId'],
                        'channel_title': item['snippet']['channelTitle'],
                        'publish_date': item['snippet']['publishedAt'],
                        'description': item['snippet'].get('description', ''),  # Полное описание из snippet
                        'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                    }
                    videos.append(video_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"Ошибка HTTP при поиске: {e}")
                break
            except Exception as e:
                print(f"Ошибка при поиске видео: {e}")
                break
        
        return videos[:max_results]
    
    def get_channel_videos(self, channel_id: str, max_results: int, order: str = 'date') -> List[Dict]:
        """Получить видео с канала"""
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            try:
                request = self.youtube.search().list(
                    part='id,snippet',
                    channelId=channel_id,
                    type='video',
                    maxResults=min(50, max_results - len(videos)),
                    order=order,
                    pageToken=next_page_token
                )
                response = request.execute()
                self.request_count += 1
                
                for item in response['items']:
                    video_data = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'channel_id': item['snippet']['channelId'],
                        'channel_title': item['snippet']['channelTitle'],
                        'publish_date': item['snippet']['publishedAt'],
                        'description': item['snippet']['description'],
                        'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                    }
                    videos.append(video_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except HttpError as e:
                print(f"Ошибка HTTP при получении видео канала: {e}")
                break
            except Exception as e:
                print(f"Ошибка при получении видео канала: {e}")
                break
        
        return videos[:max_results]
    
    def get_video_details(self, video_ids: List[str]) -> Dict[str, Dict]:
        """Получить детальную информацию о видео"""
        video_details = {}
        
        # API позволяет запрашивать до 50 видео за раз
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            try:
                request = self.youtube.videos().list(
                    part='statistics,contentDetails,snippet',
                    id=','.join(batch_ids)
                )
                response = request.execute()
                self.request_count += 1
                
                for item in response['items']:
                    video_id = item['id']
                    
                    # Определить тип видео (short или обычное)
                    duration = item['contentDetails']['duration']
                    duration_seconds = self._parse_duration(duration)
                    is_short = duration_seconds <= 60
                    
                    # Проверка наличия субтитров через локализацию
                    localizations = item.get('localizations', {})
                    has_captions = False
                    
                    # Проверяем caption в contentDetails
                    if item['contentDetails'].get('caption') == 'true':
                        has_captions = True
                    # Проверяем hasCustomThumbnail как индикатор профессионального контента
                    elif item['contentDetails'].get('hasCustomThumbnail', False):
                        has_captions = True  # Часто имеют субтитры
                    # Проверяем локализации - если есть, значит есть субтитры
                    elif len(localizations) > 0:
                        has_captions = True
                    
                    video_details[video_id] = {
                        'views': int(item['statistics'].get('viewCount', 0)),
                        'likes': int(item['statistics'].get('likeCount', 0)),
                        'comments': int(item['statistics'].get('commentCount', 0)),
                        'duration': duration,
                        'duration_seconds': duration_seconds,
                        'is_short': is_short,
                        'has_cc': has_captions,
                        'video_quality': item['contentDetails'].get('definition', 'sd'),
                        'tags': item['snippet'].get('tags', []),
                        'category_id': item['snippet'].get('categoryId', ''),
                        'full_description': item['snippet'].get('description', '')  # Полное описание
                    }
                    
            except HttpError as e:
                print(f"Ошибка HTTP при получении деталей видео: {e}")
            except Exception as e:
                print(f"Ошибка при получении деталей видео: {e}")
        
        return video_details
    
    def _parse_duration(self, duration: str) -> int:
        """Парсинг длительности видео из ISO 8601 в секунды"""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        return 0
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Получить информацию о канале"""
        try:
            request = self.youtube.channels().list(
                part='statistics,snippet,contentDetails',
                id=channel_id
            )
            response = request.execute()
            self.request_count += 1
            
            if response['items']:
                item = response['items'][0]
                return {
                    'channel_id': channel_id,
                    'channel_title': item['snippet']['title'],
                    'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                    'video_count': int(item['statistics'].get('videoCount', 0)),
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'created_at': item['snippet']['publishedAt'],
                    'channel_url': f"https://youtube.com/channel/{channel_id}"
                }
                
        except Exception as e:
            print(f"Ошибка при получении информации о канале: {e}")
        
        return None