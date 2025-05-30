import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from datetime import datetime
import nltk
from textblob import TextBlob
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import json

# Загрузка необходимых NLTK данных
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

from models import Video

class VideoAnalyzer:
    """Расширенный класс для глубокого анализа видео контента"""
    
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
        
        # Инициализация TF-IDF векторизатора
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words=list(self.stop_words),
            ngram_range=(1, 3),  # Униграммы, биграммы и триграммы
            min_df=1
        )
        
        # Паттерны успешных видео
        self.success_patterns = {
            'clickbait_words': ['shocking', 'amazing', 'secret', 'never', 'шок', 'срочно', 'жесть', 'секрет'],
            'power_words': ['best', 'top', 'ultimate', 'complete', 'лучший', 'топ', 'полный', 'гайд'],
            'question_words': ['how', 'why', 'what', 'when', 'как', 'почему', 'что', 'когда'],
            'number_patterns': [r'\d+', r'топ-?\d+', r'top\s?\d+'],
            'urgency_words': ['now', 'today', 'urgent', 'limited', 'сейчас', 'сегодня', 'срочно'],
            'emotional_triggers': ['happy', 'sad', 'angry', 'surprised', 'радость', 'грусть', 'злость']
        }
    
    async def analyze_video(self, video: Video) -> Dict[str, Any]:
        """Комплексный глубокий анализ видео"""
        analysis = {}
        
        # Анализ текстового контента
        all_text = f"{video.title} {video.description or ''} {video.subtitles or ''}"
        
        # 1. Извлечение ключевых слов через TF-IDF
        keywords_tfidf = await self.extract_keywords_tfidf(all_text)
        keywords_frequency = self.extract_keywords_frequency(all_text)
        
        # Объединение результатов двух методов
        all_keywords = list(set(keywords_tfidf + keywords_frequency))[:20]
        analysis['keywords'] = all_keywords
        analysis['top_5_keywords'] = all_keywords[:5]
        
        # 2. Анализ заголовка
        title_analysis = self.analyze_title_advanced(video.title)
        analysis.update(title_analysis)
        
        # 3. Анализ описания
        description_analysis = self.analyze_description_advanced(video.description)
        analysis.update(description_analysis)
        
        # 4. Анализ метрик
        metrics_analysis = self.analyze_metrics_advanced(video)
        analysis.update(metrics_analysis)
        
        # 5. Анализ трендов и паттернов
        trend_analysis = self.analyze_trends(video, all_text)
        analysis.update(trend_analysis)
        
        # 6. Анализ конкурентного преимущества
        competitive_analysis = self.analyze_competitive_advantage(video)
        analysis['competitive_advantage'] = competitive_analysis
        
        # 7. Генерация расширенных рекомендаций
        recommendations = self.generate_detailed_recommendations(video, analysis)
        analysis['improvement_recommendations'] = recommendations
        
        # 8. Анализ факторов успеха
        success_analysis = self.analyze_success_factors(video, analysis)
        analysis['success_analysis'] = success_analysis
        
        # 9. Стратегия контента
        strategy = self.generate_content_strategy_advanced(video, analysis)
        analysis['content_strategy'] = strategy
        
        # 10. Оценка потенциала
        potential_score = self.calculate_potential_score(video, analysis)
        analysis['potential_score'] = potential_score
        
        return analysis
    
    async def extract_keywords_tfidf(self, text: str) -> List[str]:
        """Извлечение ключевых слов через TF-IDF анализ"""
        if not text or len(text.strip()) < 10:
            return []
        
        try:
            # Очистка текста
            text = re.sub(r'http\S+|www\.\S+', '', text)
            text = re.sub(r'[^\w\s]', ' ', text)
            text = ' '.join(text.split())
            
            # Применение TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Получение топ ключевых слов
            scores = tfidf_matrix.toarray()[0]
            top_indices = scores.argsort()[-15:][::-1]
            
            keywords = []
            for idx in top_indices:
                if scores[idx] > 0:
                    keyword = feature_names[idx]
                    # Фильтрация коротких слов и стоп-слов
                    if len(keyword) > 2 and keyword.lower() not in self.stop_words:
                        keywords.append(keyword)
            
            return keywords[:10]
        
        except Exception as e:
            print(f"TF-IDF analysis error: {e}")
            return []
    
    def extract_keywords_frequency(self, text: str, top_n: int = 10) -> List[str]:
        """Извлечение ключевых слов по частоте"""
        if not text:
            return []
        
        # Очистка текста
        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+', '', text)
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
    
    def analyze_title_advanced(self, title: str) -> Dict[str, Any]:
        """Расширенный анализ заголовка"""
        analysis = {
            'title_length': len(title),
            'title_word_count': len(title.split()),
            'has_emoji': bool(re.search(r'[^\w\s,.-]', title)),
            'has_numbers': bool(re.search(r'\d', title)),
            'has_caps': title.isupper() or bool(re.search(r'[A-Z]{2,}', title)),
            'has_question': '?' in title,
            'has_exclamation': '!' in title,
            'has_brackets': bool(re.search(r'[\[\(\{]', title)),
            'has_quotes': bool(re.search(r'["\']', title))
        }
        
        # Анализ паттернов успеха
        analysis['has_power_words'] = any(
            word in title.lower() for word in self.success_patterns['power_words']
        )
        
        analysis['has_clickbait'] = any(
            word in title.lower() for word in self.success_patterns['clickbait_words']
        )
        
        analysis['has_urgency'] = any(
            word in title.lower() for word in self.success_patterns['urgency_words']
        )
        
        # Эмоциональный анализ
        try:
            blob = TextBlob(title)
            analysis['title_sentiment'] = blob.sentiment.polarity
            analysis['title_subjectivity'] = blob.sentiment.subjectivity
        except:
            analysis['title_sentiment'] = 0
            analysis['title_subjectivity'] = 0
        
        # Оценка заголовка
        title_score = 0
        if 40 <= analysis['title_length'] <= 60:
            title_score += 2
        if analysis['has_numbers']:
            title_score += 2
        if analysis['has_power_words']:
            title_score += 1
        if analysis['has_emoji']:
            title_score += 1
        if analysis['has_question']:
            title_score += 1
        
        analysis['title_score'] = min(title_score, 10)
        
        return analysis
    
    def analyze_description_advanced(self, description: str) -> Dict[str, Any]:
        """Расширенный анализ описания"""
        if not description:
            return {
                'description_length': 0,
                'description_word_count': 0,
                'description_score': 0
            }
        
        analysis = {
            'description_length': len(description),
            'description_word_count': len(description.split()),
            'description_line_count': len(description.split('\n')),
            'links_count': len(re.findall(r'http\S+|www\.\S+', description)),
            'email_count': len(re.findall(r'\S+@\S+', description)),
            'phone_count': len(re.findall(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3,5}[-\s\.]?[0-9]{3,5}', description)),
            'hashtags_count': len(re.findall(r'#\w+', description)),
            'mentions_count': len(re.findall(r'@\w+', description)),
            'has_timestamps': bool(re.search(r'\d{1,2}:\d{2}', description)),
            'has_chapters': bool(re.search(r'0:00|00:00', description)),
            'timestamp_count': len(re.findall(r'\d{1,2}:\d{2}', description))
        }
        
        # Поиск социальных сетей
        social_patterns = {
            'instagram': r'instagram\.com/\w+',
            'telegram': r't\.me/\w+|telegram\.me/\w+',
            'twitter': r'twitter\.com/\w+',
            'facebook': r'facebook\.com/\w+',
            'tiktok': r'tiktok\.com/@\w+',
            'vk': r'vk\.com/\w+'
        }
        
        analysis['social_links'] = {}
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, description.lower())
            if matches:
                analysis['social_links'][platform] = len(matches)
        
        # Проверка на призывы к действию
        cta_patterns = {
            'subscribe': ['subscribe', 'подпис'],
            'like': ['like', 'лайк', '👍'],
            'comment': ['comment', 'коммент', 'напиш'],
            'share': ['share', 'поделись', 'расскаж'],
            'bell': ['bell', 'колокол', '🔔'],
            'join': ['join', 'вступ', 'присоедин']
        }
        
        analysis['cta_types'] = []
        for cta_type, patterns in cta_patterns.items():
            if any(pattern in description.lower() for pattern in patterns):
                analysis['cta_types'].append(cta_type)
        
        analysis['has_cta'] = len(analysis['cta_types']) > 0
        analysis['cta_count'] = len(analysis['cta_types'])
        
        # Оценка описания
        desc_score = 0
        if analysis['description_length'] >= 150:
            desc_score += 2
        if analysis['has_timestamps']:
            desc_score += 2
        if analysis['links_count'] > 0:
            desc_score += 1
        if analysis['hashtags_count'] >= 3 and analysis['hashtags_count'] <= 10:
            desc_score += 1
        if analysis['has_cta']:
            desc_score += 1
        if len(analysis['social_links']) > 0:
            desc_score += 1
        
        analysis['description_score'] = min(desc_score, 10)
        
        return analysis
    
    def analyze_metrics_advanced(self, video: Video) -> Dict[str, Any]:
        """Расширенный анализ метрик видео"""
        analysis = {}
        
        # Базовые расчеты
        views = video.views or 0
        likes = video.likes or 0
        comments = video.comments or 0
        
        # Определение уровня успешности по просмотрам
        if views >= 1000000:
            view_level = 'mega_viral'
        elif views >= 100000:
            view_level = 'viral'
        elif views >= 10000:
            view_level = 'popular'
        elif views >= 1000:
            view_level = 'moderate'
        else:
            view_level = 'low'
        
        analysis['view_level'] = view_level
        
        # Детальный анализ вовлеченности
        if views > 0:
            like_rate = (likes / views) * 100
            comment_rate = (comments / views) * 100
            engagement_rate = ((likes + comments) / views) * 100
            
            # Оценка качества вовлеченности
            if like_rate >= 10:
                engagement_quality = 'exceptional'
            elif like_rate >= 5:
                engagement_quality = 'excellent'
            elif like_rate >= 3:
                engagement_quality = 'good'
            elif like_rate >= 1:
                engagement_quality = 'average'
            else:
                engagement_quality = 'poor'
            
            analysis['engagement_quality'] = engagement_quality
            
            # Соотношение комментариев к лайкам
            if likes > 0:
                comment_to_like_ratio = comments / likes
                if comment_to_like_ratio >= 0.1:
                    analysis['discussion_level'] = 'high'
                elif comment_to_like_ratio >= 0.05:
                    analysis['discussion_level'] = 'moderate'
                else:
                    analysis['discussion_level'] = 'low'
            else:
                analysis['discussion_level'] = 'none'
        else:
            analysis['engagement_quality'] = 'no_data'
            analysis['discussion_level'] = 'no_data'
        
        # Анализ времени с публикации
        if video.publish_date:
            days_since_publish = (datetime.now() - video.publish_date).days
            if days_since_publish > 0:
                views_per_day = views / days_since_publish
                analysis['views_per_day'] = round(views_per_day, 2)
                
                # Оценка темпа роста
                if views_per_day >= 10000:
                    analysis['growth_rate'] = 'explosive'
                elif views_per_day >= 1000:
                    analysis['growth_rate'] = 'rapid'
                elif views_per_day >= 100:
                    analysis['growth_rate'] = 'steady'
                else:
                    analysis['growth_rate'] = 'slow'
        
        # Виральный потенциал (0-100)
        viral_score = 0
        
        # Просмотры
        if views >= 1000000:
            viral_score += 30
        elif views >= 100000:
            viral_score += 20
        elif views >= 10000:
            viral_score += 10
        elif views >= 1000:
            viral_score += 5
        
        # Вовлеченность
        if video.engagement_rate >= 10:
            viral_score += 30
        elif video.engagement_rate >= 5:
            viral_score += 20
        elif video.engagement_rate >= 2:
            viral_score += 10
        
        # Комментарии
        if video.comment_ratio >= 1:
            viral_score += 20
        elif video.comment_ratio >= 0.5:
            viral_score += 10
        
        # Темп роста
        if analysis.get('growth_rate') == 'explosive':
            viral_score += 20
        elif analysis.get('growth_rate') == 'rapid':
            viral_score += 10
        
        analysis['viral_score'] = min(viral_score, 100)
        
        return analysis
    
    def analyze_trends(self, video: Video, text: str) -> Dict[str, Any]:
        """Анализ трендовых элементов"""
        analysis = {}
        
        # Список актуальных трендов (можно обновлять динамически)
        trends_2024 = {
            'ai': ['ai', 'artificial intelligence', 'chatgpt', 'midjourney', 'ии', 'искусственный интеллект'],
            'shorts': ['shorts', 'short', 'шортс', 'короткое видео'],
            'trends': ['trend', 'trending', 'viral', 'тренд', 'вирус'],
            'challenges': ['challenge', 'челлендж', 'вызов'],
            'reaction': ['reaction', 'reacts', 'реакция'],
            'tutorial': ['tutorial', 'how to', 'guide', 'обучение', 'как сделать', 'гайд'],
            'review': ['review', 'обзор', 'распаковка', 'unboxing'],
            'podcast': ['podcast', 'подкаст', 'интервью', 'interview']
        }
        
        found_trends = []
        text_lower = text.lower()
        
        for trend_category, keywords in trends_2024.items():
            if any(keyword in text_lower for keyword in keywords):
                found_trends.append(trend_category)
        
        analysis['trend_categories'] = found_trends
        analysis['trend_score'] = len(found_trends) * 10
        analysis['is_trendy'] = len(found_trends) >= 2
        
        return analysis
    
    def analyze_competitive_advantage(self, video: Video) -> str:
        """Анализ конкурентных преимуществ видео"""
        advantages = []
        
        # Анализ уникальности
        if video.views > 100000:
            advantages.append("Массовый охват аудитории")
        
        if video.engagement_rate > 5:
            advantages.append("Исключительно высокая вовлеченность")
        
        if video.is_short and video.views > 50000:
            advantages.append("Успешный формат Shorts")
        
        if video.comment_ratio > 1:
            advantages.append("Активное обсуждение в комментариях")
        
        if video.has_chapters:
            advantages.append("Удобная навигация по главам")
        
        if video.duration and video.duration.startswith("PT"):
            # Парсинг длительности
            duration_match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', video.duration)
            if duration_match:
                hours = int(duration_match.group(1) or 0)
                minutes = int(duration_match.group(2) or 0)
                total_minutes = hours * 60 + minutes
                
                if total_minutes > 10 and video.views > 10000:
                    advantages.append("Длинный формат с хорошим удержанием")
                elif total_minutes < 1 and video.views > 50000:
                    advantages.append("Вирусный короткий формат")
        
        return " | ".join(advantages) if advantages else "Стандартное видео без явных преимуществ"
    
    def generate_detailed_recommendations(self, video: Video, analysis: Dict[str, Any]) -> str:
        """Генерация детальных рекомендаций по улучшению"""
        recommendations = []
        priority_high = []
        priority_medium = []
        priority_low = []
        
        # ВЫСОКИЙ ПРИОРИТЕТ
        
        # Заголовок
        if analysis.get('title_length', 0) < 40:
            priority_high.append("🔴 Увеличьте длину заголовка до 50-60 символов для лучшего CTR")
        elif analysis.get('title_length', 0) > 70:
            priority_high.append("🔴 Сократите заголовок до 60-70 символов, чтобы он не обрезался")
        
        if not analysis.get('has_numbers') and not video.is_short:
            priority_high.append("🔴 Добавьте числа в заголовок (ТОП-5, 10 способов) - повышает CTR на 36%")
        
        if analysis.get('title_score', 0) < 5:
            priority_high.append("🔴 Усильте заголовок: добавьте эмоциональные слова или вопрос")
        
        # Описание
        if analysis.get('description_length', 0) < 150:
            priority_high.append("🔴 Расширьте описание минимум до 150 слов с ключевыми словами")
        
        if not analysis.get('has_timestamps') and video.duration and 'M' in video.duration:
            priority_high.append("🔴 Добавьте временные метки (таймкоды) для удобной навигации")
        
        # Вовлеченность
        if video.engagement_rate < 2:
            priority_high.append("🔴 Критически низкая вовлеченность! Добавьте вопрос в конце видео")
        
        # СРЕДНИЙ ПРИОРИТЕТ
        
        if not analysis.get('has_emoji') and video.is_short:
            priority_medium.append("🟡 Для Shorts добавьте 1-2 эмодзи в заголовок")
        
        if analysis.get('links_count', 0) == 0:
            priority_medium.append("🟡 Добавьте полезные ссылки: соцсети, похожие видео")
        
        if analysis.get('hashtags_count', 0) < 3:
            priority_medium.append("🟡 Используйте 3-5 релевантных хэштегов (#shorts #топ)")
        
        if not analysis.get('social_links'):
            priority_medium.append("🟡 Добавьте ссылки на соцсети для роста подписчиков")
        
        # НИЗКИЙ ПРИОРИТЕТ
        
        if not analysis.get('has_cta'):
            priority_low.append("🟢 Добавьте призыв к действию в описание")
        
        if analysis.get('cta_count', 0) > 5:
            priority_low.append("🟢 Слишком много призывов к действию - оставьте 2-3 основных")
        
        # Специфичные рекомендации для Shorts
        if video.is_short:
            if video.duration and 'S' in video.duration:
                seconds = int(re.search(r'(\d+)S', video.duration).group(1))
                if seconds > 45:
                    priority_high.append("🔴 Для Shorts сократите длительность до 15-30 секунд")
            
            priority_medium.append("🟡 Используйте вертикальный формат 9:16")
            priority_medium.append("🟡 Добавьте динамичные переходы каждые 3-5 секунд")
        
        # Формирование итоговых рекомендаций
        if priority_high:
            recommendations.append("КРИТИЧНО:\n" + "\n".join(priority_high))
        if priority_medium:
            recommendations.append("\nВАЖНО:\n" + "\n".join(priority_medium))
        if priority_low:
            recommendations.append("\nЖЕЛАТЕЛЬНО:\n" + "\n".join(priority_low))
        
        if not recommendations:
            return "✅ Видео хорошо оптимизировано! Фокусируйтесь на качестве контента."
        
        return "\n".join(recommendations)
    
    def analyze_success_factors(self, video: Video, analysis: Dict[str, Any]) -> str:
        """Детальный анализ факторов успеха"""
        factors = []
        scores = {}
        
        # 1. Анализ заголовка
        if analysis.get('has_clickbait'):
            factors.append("🎯 Интригующий заголовок с элементами кликбейта (+25% CTR)")
            scores['title'] = 3
        elif analysis.get('has_power_words'):
            factors.append("💪 Сильные слова в заголовке привлекают внимание")
            scores['title'] = 2
        
        if analysis.get('has_numbers'):
            factors.append("🔢 Числа в заголовке повышают доверие и CTR")
            scores['title'] = scores.get('title', 0) + 1
        
        # 2. Анализ времени публикации
        if video.publish_date:
            weekday = video.publish_date.weekday()
            hour = video.publish_date.hour
            
            if weekday in [4, 5, 6]:  # Пятница-воскресенье
                factors.append("📅 Публикация в выходные = больше свободного времени у зрителей")
                scores['timing'] = 2
            
            if 18 <= hour <= 22:  # Прайм-тайм
                factors.append("🕐 Публикация в прайм-тайм (18:00-22:00)")
                scores['timing'] = scores.get('timing', 0) + 1
        
        # 3. Анализ вовлеченности
        engagement_level = analysis.get('engagement_quality', '')
        if engagement_level in ['excellent', 'exceptional']:
            factors.append(f"🔥 {engagement_level.upper()} вовлеченность = алгоритм продвигает видео")
            scores['engagement'] = 3
        
        if analysis.get('discussion_level') == 'high':
            factors.append("💬 Высокая дискуссионность = больше комментариев = выше ранжирование")
            scores['engagement'] = scores.get('engagement', 0) + 1
        
        # 4. Анализ формата
        if video.is_short:
            if analysis.get('view_level') in ['viral', 'mega_viral']:
                factors.append("📱 Shorts + вирусность = экспоненциальный рост")
                scores['format'] = 3
        else:
            if video.duration and analysis.get('view_level') in ['popular', 'viral', 'mega_viral']:
                factors.append("🎬 Длинный формат с высоким удержанием")
                scores['format'] = 2
        
        # 5. Анализ трендов
        if analysis.get('is_trendy'):
            trend_list = ", ".join(analysis.get('trend_categories', []))
            factors.append(f"📈 Попадание в тренды: {trend_list}")
            scores['trends'] = 2
        
        # 6. Анализ контента
        if any(cat in analysis.get('trend_categories', []) for cat in ['tutorial', 'review']):
            factors.append("📚 Образовательный контент имеет высокую ценность")
            scores['content'] = 2
        
        # 7. Технические факторы
        if video.has_cc:
            factors.append("📝 Субтитры увеличивают охват (доступность + SEO)")
            scores['technical'] = 1
        
        if video.has_chapters:
            factors.append("📑 Главы улучшают пользовательский опыт")
            scores['technical'] = scores.get('technical', 0) + 1
        
        # 8. Вирусные индикаторы
        viral_score = analysis.get('viral_score', 0)
        if viral_score >= 70:
            factors.append(f"🚀 Вирусный потенциал: {viral_score}/100")
            scores['viral'] = 3
        elif viral_score >= 50:
            factors.append(f"⚡ Высокий потенциал роста: {viral_score}/100")
            scores['viral'] = 2
        
        # Подсчет общего балла успеха
        total_score = sum(scores.values())
        max_score = 20
        success_percentage = (total_score / max_score) * 100
        
        # Формирование вывода
        if factors:
            result = f"📊 Оценка успеха: {success_percentage:.0f}%\n\n"
            result += "КЛЮЧЕВЫЕ ФАКТОРЫ УСПЕХА:\n"
            result += "\n".join(factors)
            
            # Добавление рекомендаций по воспроизведению успеха
            result += "\n\n🎯 ДЛЯ ПОВТОРЕНИЯ УСПЕХА:\n"
            
            if scores.get('title', 0) >= 2:
                result += "• Используйте похожую структуру заголовка\n"
            if scores.get('timing', 0) >= 2:
                result += "• Публикуйте в то же время и день недели\n"
            if scores.get('engagement', 0) >= 2:
                result += "• Провоцируйте дискуссию вопросами\n"
            if scores.get('trends', 0) >= 2:
                result += "• Следите за трендами в нише\n"
            
            return result
        else:
            return "📊 Стандартное видео без явных факторов вирусности. Успех зависит от качества контента."
    
    def generate_content_strategy_advanced(self, video: Video, analysis: Dict[str, Any]) -> str:
        """Генерация детальной стратегии контента"""
        strategies = []
        
        # 1. АНАЛИЗ НИШИ
        strategies.append("📊 АНАЛИЗ НИШИ И ПОЗИЦИОНИРОВАНИЕ:")
        
        keywords = analysis.get('keywords', [])[:5]
        if keywords:
            strategies.append(f"• Ключевые темы: {', '.join(keywords)}")
            strategies.append(f"• Создайте серию из 5-7 видео вокруг этих тем")
        
        # 2. ФОРМАТ И ДЛИТЕЛЬНОСТЬ
        strategies.append("\n📱 ОПТИМАЛЬНЫЙ ФОРМАТ:")
        
        if video.is_short:
            strategies.append("• Фокус на Shorts - публикуйте 1-2 в день")
            strategies.append("• Длительность: 15-30 секунд")
            strategies.append("• Вертикальный формат 9:16")
            strategies.append("• Цепляющие первые 3 секунды")
        else:
            if video.duration:
                strategies.append(f"• Оптимальная длительность: {video.duration}")
                strategies.append("• Структура: вступление (15 сек) → контент → CTA")
        
        # 3. ВРЕМЯ ПУБЛИКАЦИИ
        strategies.append("\n⏰ РАСПИСАНИЕ ПУБЛИКАЦИЙ:")
        
        if video.publish_date:
            weekday_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            weekday = weekday_names[video.publish_date.weekday()]
            hour = video.publish_date.hour
            strategies.append(f"• Лучшее время: {weekday} в {hour}:00")
            strategies.append("• Регулярность: минимум 2-3 видео в неделю")
        
        # 4. ОПТИМИЗАЦИЯ
        strategies.append("\n🎯 ОПТИМИЗАЦИЯ ДЛЯ АЛГОРИТМОВ:")
        
        if analysis.get('has_clickbait') or analysis.get('has_power_words'):
            strategies.append("• Используйте эмоциональные заголовки")
            strategies.append("• Формула: [Число] + [Результат] + [Время]")
            strategies.append("• Пример: '5 способов заработать $1000 за неделю'")
        
        strategies.append("• Кастомная обложка с крупным текстом")
        strategies.append("• A/B тестирование заголовков")
        
        # 5. КОНТЕНТ-ПЛАН
        strategies.append("\n📅 КОНТЕНТ-ПЛАН НА МЕСЯЦ:")
        
        content_types = []
        if 'tutorial' in analysis.get('trend_categories', []):
            content_types.append("• Обучающие видео (40%)")
        if 'review' in analysis.get('trend_categories', []):
            content_types.append("• Обзоры и распаковки (30%)")
        if 'reaction' in analysis.get('trend_categories', []):
            content_types.append("• Реакции и мнения (20%)")
        content_types.append("• Развлекательный контент (10%)")
        
        strategies.extend(content_types)
        
        # 6. МОНЕТИЗАЦИЯ
        strategies.append("\n💰 СТРАТЕГИЯ МОНЕТИЗАЦИИ:")
        
        if video.views > 100000:
            strategies.append("• Потенциал для спонсорства: высокий")
            strategies.append("• Средняя ставка: $20-50 за 1000 просмотров")
        elif video.views > 10000:
            strategies.append("• Потенциал для партнерок: средний")
            strategies.append("• Фокус на affiliate-ссылках")
        
        strategies.append("• Создайте воронку: YouTube → Email → Продукт")
        
        # 7. МАСШТАБИРОВАНИЕ
        strategies.append("\n🚀 ПЛАН РОСТА:")
        
        growth_rate = analysis.get('growth_rate', 'steady')
        if growth_rate in ['explosive', 'rapid']:
            strategies.append("• Удвойте частоту публикаций")
            strategies.append("• Запустите похожие серии видео")
        
        strategies.append("• Коллаборации с похожими каналами")
        strategies.append("• Кросс-промо в других соцсетях")
        strategies.append("• Создание плейлистов для увеличения сессий")
        
        # 8. КЛЮЧЕВЫЕ МЕТРИКИ
        strategies.append("\n📈 KPI ДЛЯ ОТСЛЕЖИВАНИЯ:")
        strategies.append("• CTR обложек: целевой >10%")
        strategies.append("• Удержание: >50% на отметке 30%")
        strategies.append("• Вовлеченность: >5%")
        strategies.append("• Рост подписчиков: +10-20% в месяц")
        
        return "\n".join(strategies)
    
    def calculate_potential_score(self, video: Video, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Расчет потенциала видео для воспроизведения"""
        score = 0
        max_score = 100
        breakdown = {}
        
        # 1. Потенциал вирусности (30 баллов)
        viral_score = analysis.get('viral_score', 0)
        viral_points = (viral_score / 100) * 30
        breakdown['viral_potential'] = round(viral_points, 1)
        score += viral_points
        
        # 2. Качество оптимизации (20 баллов)
        title_score = analysis.get('title_score', 0)
        desc_score = analysis.get('description_score', 0)
        optimization_points = ((title_score + desc_score) / 20) * 20
        breakdown['optimization'] = round(optimization_points, 1)
        score += optimization_points
        
        # 3. Трендовость (15 баллов)
        trend_score = analysis.get('trend_score', 0)
        trend_points = min(trend_score, 15)
        breakdown['trendiness'] = trend_points
        score += trend_points
        
        # 4. Вовлеченность (20 баллов)
        engagement_quality = analysis.get('engagement_quality', 'average')
        engagement_map = {
            'exceptional': 20,
            'excellent': 15,
            'good': 10,
            'average': 5,
            'poor': 2
        }
        engagement_points = engagement_map.get(engagement_quality, 5)
        breakdown['engagement'] = engagement_points
        score += engagement_points
        
        # 5. Техническое качество (15 баллов)
        technical_score = 0
        if video.has_cc:
            technical_score += 5
        if video.has_chapters:
            technical_score += 5
        if video.video_quality in ['hd', '4k']:
            technical_score += 5
        breakdown['technical'] = technical_score
        score += technical_score
        
        # Итоговая оценка
        total_score = round(score, 1)
        
        # Рекомендация
        if total_score >= 80:
            recommendation = "🟢 ОБЯЗАТЕЛЬНО К ВОСПРОИЗВЕДЕНИЮ! Высочайший потенциал успеха."
        elif total_score >= 60:
            recommendation = "🟡 РЕКОМЕНДУЕТСЯ. Хороший потенциал с небольшими улучшениями."
        elif total_score >= 40:
            recommendation = "🟠 ВОЗМОЖНО. Требуется значительная адаптация."
        else:
            recommendation = "🔴 НЕ РЕКОМЕНДУЕТСЯ. Низкий потенциал успеха."
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': round((total_score / max_score) * 100, 1),
            'breakdown': breakdown,
            'recommendation': recommendation
        }
