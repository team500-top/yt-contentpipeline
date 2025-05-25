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
        """И