import re
import asyncio
from typing import Dict, Any, List, Optional
from collections import Counter
from datetime import datetime
import nltk
from textblob import TextBlob
import string

# Загрузка необходимых NLTK данных
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

from models import Video

class VideoAnalyzer:
    """Класс для анализа видео контента"""
    
    def __init__(self):
        # Стоп-слова для различных языков
        self.stop_words = set()
        try:
            from nltk.corpus import stopwords
            self.stop_words.update(stopwords.words('english'))
            self.stop_words.update(stopwords.words('russian'))
        except:
            # Базовые стоп-слова если NLTK недоступен
            self.stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'и', 'в', 'на', 'с', 'по', 'за', 'к', 'от', 'до', 'из', 'о', 'об',
                'это', 'как', 'что', 'все', 'она', 'так', 'его', 'но', 'да', 'ты'
            }
    
    async def analyze_video(self, video: Video) -> Dict[str, Any]:
        """Комплексный анализ видео"""
        analysis = {}
        
        # Извлечение ключевых слов
        keywords = self.extract_keywords(video.title, video.description)
        analysis['keywords'] = keywords
        
        # Анализ заголовка
        title_analysis = self.analyze_title(video.title)
        analysis.update(title_analysis)
        
        # Анализ описания
        description_analysis = self.analyze_description(video.description)
        analysis.update(description_analysis)
        
        # Анализ метрик
        metrics_analysis = self.analyze_metrics(video)
        analysis.update(metrics_analysis)
        
        # Генерация рекомендаций
        recommendations = self.generate_recommendations(video, analysis)
        analysis['recommendations'] = recommendations
        
        # Анализ успеха
        success_analysis = self.analyze_success(video, analysis)
        analysis['success_analysis'] = success_analysis
        
        # Стратегия контента
        strategy = self.generate_content_strategy(video, analysis)
        analysis['strategy'] = strategy
        
        return analysis
    
    def extract_keywords(self, title: str, description: str, top_n: int = 10) -> List[str]:
        """Извлечение ключевых слов из заголовка и описания"""
        # Объединение текста
        text = f"{title} {description}".lower()
        
        # Удаление URL и email
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Удаление специальных символов
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Токенизация
        words = text.split()
        
        # Фильтрация
        words = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words and not word.isdigit()
        ]
        
        # Подсчет частоты
        word_freq = Counter(words)
        
        # Возврат топ ключевых слов
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def analyze_title(self, title: str) -> Dict[str, Any]:
        """Анализ заголовка видео"""
        analysis = {
            'title_length': len(title),
            'title_word_count': len(title.split()),
            'has_emoji': bool(re.search(r'[^\w\s,]', title)),
            'has_numbers': bool(re.search(r'\d', title)),
            'has_caps': title.isupper() or bool(re.search(r'[A-Z]{2,}', title)),
            'has_question': '?' in title,
            'has_exclamation': '!' in title
        }
        
        # Проверка на clickbait паттерны
        clickbait_patterns = [
            r'you won\'t believe',
            r'shocking',
            r'amazing',
            r'secret',
            r'никогда не поверишь',
            r'шок',
            r'срочно',
            r'жесть'
        ]
        
        analysis['has_clickbait'] = any(
            re.search(pattern, title.lower()) for pattern in clickbait_patterns
        )
        
        return analysis
    
    def analyze_description(self, description: str) -> Dict[str, Any]:
        """Анализ описания видео"""
        if not description:
            return {
                'description_length': 0,
                'description_word_count': 0,
                'links_count': 0,
                'hashtags_count': 0,
                'has_timestamps': False
            }
        
        analysis = {
            'description_length': len(description),
            'description_word_count': len(description.split()),
            'links_count': len(re.findall(r'http\S+|www\.\S+', description)),
            'hashtags_count': len(re.findall(r'#\w+', description)),
            'has_timestamps': bool(re.search(r'\d{1,2}:\d{2}', description)),
            'has_chapters': bool(re.search(r'0:00|00:00', description))
        }
        
        # Проверка на призывы к действию
        cta_patterns = [
            r'subscribe',
            r'like',
            r'comment',
            r'подпис',
            r'лайк',
            r'коммент',
            r'нажми',
            r'перейди'
        ]
        
        analysis['has_cta'] = any(
            re.search(pattern, description.lower()) for pattern in cta_patterns
        )
        
        return analysis
    
    def analyze_metrics(self, video: Video) -> Dict[str, Any]:
        """Анализ метрик видео"""
        analysis = {}
        
        # Определение уровня вовлеченности
        if video.engagement_rate > 10:
            engagement_level = 'exceptional'
        elif video.engagement_rate > 5:
            engagement_level = 'excellent'
        elif video.engagement_rate > 2:
            engagement_level = 'good'
        elif video.engagement_rate > 1:
            engagement_level = 'average'
        else:
            engagement_level = 'low'
        
        analysis['engagement_level'] = engagement_level
        
        # Анализ соотношения лайков/дизлайков
        if video.likes > 0:
            like_sentiment = 'positive' if video.like_ratio > 3 else 'mixed'
        else:
            like_sentiment = 'neutral'
        
        analysis['like_sentiment'] = like_sentiment
        
        # Виральный потенциал
        viral_score = 0
        if video.views > 100000:
            viral_score += 3
        elif video.views > 10000:
            viral_score += 2
        elif video.views > 1000:
            viral_score += 1
        
        if video.engagement_rate > 5:
            viral_score += 2
        elif video.engagement_rate > 2:
            viral_score += 1
        
        if video.comment_ratio > 1:
            viral_score += 1
        
        analysis['viral_potential'] = min(viral_score, 5)
        
        return analysis
    
    def generate_recommendations(self, video: Video, analysis: Dict[str, Any]) -> str:
        """Генерация рекомендаций по улучшению видео"""
        recommendations = []
        
        # Рекомендации по заголовку
        if analysis.get('title_length', 0) < 30:
            recommendations.append("Увеличьте длину заголовка до 50-60 символов для лучшей видимости в поиске")
        elif analysis.get('title_length', 0) > 100:
            recommendations.append("Сократите заголовок - слишком длинные заголовки обрезаются в результатах поиска")
        
        if not analysis.get('has_numbers'):
            recommendations.append("Добавьте числа в заголовок (например, 'ТОП-5', '10 способов') - это повышает CTR")
        
        if not analysis.get('has_emoji'):
            recommendations.append("Используйте эмодзи в заголовке для привлечения внимания")
        
        # Рекомендации по описанию
        if analysis.get('description_length', 0) < 100:
            recommendations.append("Расширьте описание - добавьте больше информации о видео, ключевые слова")
        
        if not analysis.get('has_timestamps'):
            recommendations.append("Добавьте временные метки в описание для удобства навигации")
        
        if analysis.get('links_count', 0) == 0:
            recommendations.append("Добавьте полезные ссылки в описание (соцсети, связанные видео)")
        
        if analysis.get('hashtags_count', 0) < 3:
            recommendations.append("Используйте 3-5 релевантных хэштегов для улучшения поиска")
        
        # Рекомендации по метрикам
        if video.engagement_rate < 2:
            recommendations.append("Работайте над повышением вовлеченности - задавайте вопросы, призывайте к обсуждению")
        
        if video.comment_ratio < 0.5:
            recommendations.append("Стимулируйте комментарии - задайте вопрос в конце видео")
        
        # Рекомендации для Shorts
        if video.is_short:
            if video.duration and int(video.duration.replace('PT', '').replace('S', '')) > 45:
                recommendations.append("Для Shorts оптимальная длительность 15-30 секунд")
            recommendations.append("Используйте вертикальный формат и динамичный монтаж")
        
        return "\n".join(recommendations) if recommendations else "Видео хорошо оптимизировано!"
    
    def analyze_success(self, video: Video, analysis: Dict[str, Any]) -> str:
        """Анализ причин успеха видео"""
        factors = []
        
        # Анализ заголовка
        if analysis.get('has_clickbait'):
            factors.append("Интригующий заголовок привлекает внимание")
        
        if analysis.get('has_numbers'):
            factors.append("Числа в заголовке повышают CTR")
        
        # Анализ времени публикации
        if video.publish_date:
            weekday = video.publish_date.weekday()
            if weekday in [4, 5, 6]:  # Пятница, суббота, воскресенье
                factors.append("Публикация в выходные дни увеличивает охват")
        
        # Анализ вовлеченности
        if analysis.get('engagement_level') in ['excellent', 'exceptional']:
            factors.append("Высокая вовлеченность указывает на качественный контент")
        
        # Анализ формата
        if video.is_short:
            factors.append("Формат Shorts способствует быстрому росту просмотров")
        
        # Анализ тематики
        if any(keyword in ['tutorial', 'how to', 'как', 'обучение'] for keyword in analysis.get('keywords', [])):
            factors.append("Обучающий контент имеет высокую ценность для аудитории")
        
        if video.views > 10000:
            factors.append("Видео попало в рекомендации YouTube")
        
        return " ".join(factors) if factors else "Стандартное видео без явных факторов успеха"
    
    def generate_content_strategy(self, video: Video, analysis: Dict[str, Any]) -> str:
        """Генерация стратегии создания похожего контента"""
        strategies = []
        
        # Базовая стратегия
        strategies.append(f"Создайте серию видео на тему '{' '.join(analysis.get('keywords', [])[:3])}'")
        
        # Формат
        if video.is_short:
            strategies.append("Сфокусируйтесь на коротком формате - публикуйте Shorts ежедневно")
        else:
            strategies.append(f"Оптимальная длительность для этой ниши: {video.duration}")
        
        # Время публикации
        if video.publish_date:
            hour = video.publish_date.hour
            strategies.append(f"Публикуйте в {hour}:00 по времени вашей целевой аудитории")
        
        # Оптимизация
        if analysis.get('has_clickbait'):
            strategies.append("Используйте интригующие заголовки, но избегайте обмана ожиданий")
        
        strategies.append("Создайте привлекательную обложку с крупным текстом и ярким фоном")
        
        # Контент
        if video.engagement_rate > 5:
            strategies.append("Этот формат вызывает эмоции - создавайте эмоциональный контент")
        
        strategies.append("Анализируйте комментарии для понимания запросов аудитории")
        
        # Продвижение
        strategies.append("Создайте плейлист из похожих видео для увеличения времени просмотра")
        strategies.append("Используйте карточки и конечные заставки для перенаправления на другие видео")
        
        return "\n".join(strategies)