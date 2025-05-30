#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Competitor Analysis Tool
Основной скрипт для анализа видео и каналов конкурентов на YouTube
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Импорты из проекта
from src.analyzer import YouTubeAnalyzer
from src.utils import setup_logging, load_config, validate_environment
from config import Config

def parse_arguments() -> argparse.Namespace:
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="YouTube Competitor Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --offer "Онлайн курсы Python"
  %(prog)s --offer "Фитнес тренировки" --max-videos 100
  %(prog)s --keywords "python обучение,программирование курс" --max-channels 15
        """
    )
    
    # Основные параметры
    parser.add_argument(
        '--offer', 
        type=str, 
        required=True,
        help='Описание вашего оффера/продукта для анализа конкурентов'
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        help='Дополнительные ключевые слова (через запятую)'
    )
    
    # Ограничения
    parser.add_argument(
        '--max-videos',
        type=int,
        default=50,
        help='Максимальное количество видео для анализа (по умолчанию: 50)'
    )
    
    parser.add_argument(
        '--max-channels',
        type=int,
        default=20,
        help='Максимальное количество каналов для анализа (по умолчанию: 20)'
    )
    
    # Настройки поведения
    parser.add_argument(
        '--no-transcripts',
        action='store_true',
        help='Пропустить извлечение субтитров (быстрее, но менее детально)'
    )
    
    parser.add_argument(
        '--channels-only',
        action='store_true',
        help='Анализировать только каналы, без детального анализа видео'
    )
    
    parser.add_argument(
        '--parallel',
        type=int,
        default=4,
        help='Количество параллельных потоков (по умолчанию: 4)'
    )
    
    # Вывод и отчеты
    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports',
        help='Папка для сохранения отчетов (по умолчанию: reports)'
    )
    
    parser.add_argument(
        '--format',
        choices=['excel', 'json', 'both'],
        default='excel',
        help='Формат выходных файлов (по умолчанию: excel)'
    )
    
    # Отладка
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод (режим отладки)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Показать план действий без выполнения'
    )
    
    return parser.parse_args()

def generate_keywords_from_offer(offer: str, additional_keywords: List[str] = None) -> List[str]:
    """Генерация ключевых запросов из оффера"""
    
    # Базовые слова из оффера
    offer_words = [word.lower().strip() for word in offer.split() if len(word) > 3]
    
    # Популярные модификаторы для YouTube поиска
    modifiers = [
        'как', 'что такое', 'лучший', 'топ', 'обзор', 'гайд', 'урок',
        'курс', 'обучение', 'для начинающих', 'с нуля', 'пошагово'
    ]
    
    # Формирование ключевых запросов
    keywords = []
    
    # Добавляем базовые слова
    keywords.extend(offer_words[:3])  # Берем 3 основных слова
    
    # Комбинируем с модификаторами
    for base_word in offer_words[:2]:  # Берем 2 основных слова
        for modifier in modifiers[:5]:  # Берем 5 модификаторов
            keywords.append(f"{modifier} {base_word}")
    
    # Добавляем дополнительные ключевые слова
    if additional_keywords:
        keywords.extend(additional_keywords)
    
    # Добавляем популярные комбинации
    trending_combinations = [
        f"{offer_words[0]} 2025" if offer_words else "2025",
        f"лучшие {offer_words[0]}" if offer_words else "лучшие",
        f"топ {offer_words[0]}" if offer_words else "топ"
    ]
    keywords.extend(trending_combinations)
    
    # Удаляем дубликаты и ограничиваем количество
    unique_keywords = list(dict.fromkeys(keywords))  # Сохраняем порядок
    
    return unique_keywords[:15]  # Ограничиваем 15 ключевыми запросами

def display_analysis_plan(args: argparse.Namespace, keywords: List[str]) -> None:
    """Отображение плана анализа"""
    print("\n" + "="*60)
    print("ПЛАН АНАЛИЗА YOUTUBE КОНКУРЕНТОВ")
    print("="*60)
    
    print(f"\n🎯 ОФФЕР: {args.offer}")
    print(f"📊 МАСШТАБ АНАЛИЗА:")
    print(f"   • Максимум видео: {args.max_videos}")
    print(f"   • Максимум каналов: {args.max_channels}")
    print(f"   • Параллельные потоки: {args.parallel}")
    
    print(f"\n🔍 КЛЮЧЕВЫЕ ЗАПРОСЫ ({len(keywords)}):")
    for i, keyword in enumerate(keywords, 1):
        print(f"   {i:2d}. {keyword}")
    
    print(f"\n⚙️  НАСТРОЙКИ:")
    print(f"   • Извлечение субтитров: {'Нет' if args.no_transcripts else 'Да'}")
    print(f"   • Только каналы: {'Да' if args.channels_only else 'Нет'}")
    print(f"   • Формат отчетов: {args.format}")
    print(f"   • Папка результатов: {args.output_dir}")
    
    print(f"\n📋 ЭТАПЫ ВЫПОЛНЕНИЯ:")
    steps = [
        "1. Поиск видео по ключевым запросам",
        "2. Извлечение данных видео" + ("" if not args.no_transcripts else " (без субтитров)"),
        "3. Определение уникальных каналов",
        "4. Анализ каналов конкурентов",
        "5. Контент-анализ и NLP обработка",
        "6. Генерация отчетов в формате " + args.format.upper()
    ]
    
    if args.channels_only:
        steps = [s for s in steps if "видео" not in s.lower() or "Определение" in s]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n" + "="*60)

def main():
    """Основная функция"""
    print("🎬 YouTube Competitor Analysis Tool")
    print("📊 Анализ видео и каналов конкурентов\n")
    
    # Парсинг аргументов
    args = parse_arguments()
    
    # Настройка логирования
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Валидация окружения
        validate_environment()
        
        # Проверка что мы в правильной папке
        if not Path.cwd().name == "youtube-analyzer" and not str(Path.cwd()) == r"C:\youtube-analyzer":
            logger.warning(f"Текущая папка: {Path.cwd()}")
            logger.warning("Рекомендуется запускать из C:\\youtube-analyzer")
        
        # Инициализация структуры проекта
        from src.utils import initialize_project_structure
        initialize_project_structure()
        
        # Генерация ключевых запросов
        additional_keywords = []
        if args.keywords:
            additional_keywords = [kw.strip() for kw in args.keywords.split(',')]
        
        keywords = generate_keywords_from_offer(args.offer, additional_keywords)
        
        # Отображение плана
        display_analysis_plan(args, keywords)
        
        if args.dry_run:
            print("\n🔍 Режим dry-run: план показан, выполнение пропущено")
            return
        
        # Подтверждение запуска
        if not args.verbose:  # В обычном режиме спрашиваем подтверждение
            response = input("\n▶️  Начать анализ? [y/N]: ").strip().lower()
            if response not in ['y', 'yes', 'да', 'д']:
                print("❌ Анализ отменен")
                return
        
        print("\n🚀 Запуск анализа...")
        start_time = datetime.now()
        
        # Инициализация анализатора
        analyzer = YouTubeAnalyzer(
            max_workers=args.parallel,
            extract_transcripts=not args.no_transcripts,
            output_dir=args.output_dir
        )
        
        # === ЭТАП 1: Поиск видео ===
        print("\n📹 Этап 1: Поиск видео по ключевым запросам...")
        video_urls = analyzer.search_videos_by_keywords(
            keywords=keywords,
            max_results=args.max_videos
        )
        
        if not video_urls:
            logger.error("❌ Видео не найдены. Проверьте ключевые слова или соединение")
            return
        
        print(f"✅ Найдено {len(video_urls)} видео для анализа")
        
        # === ЭТАП 2: Анализ видео (если не только каналы) ===
        videos_data = []
        if not args.channels_only:
            print(f"\n🔍 Этап 2: Анализ видео (0/{len(video_urls)})...")
            videos_data = analyzer.analyze_videos_batch(video_urls)
            print(f"✅ Проанализировано {len(videos_data)} видео")
        
        # === ЭТАП 3: Определение каналов ===
        print(f"\n📺 Этап 3: Определение уникальных каналов...")
        if args.channels_only:
            # Если анализируем только каналы, извлекаем channel_id из URL
            channel_ids = analyzer.extract_channel_ids_from_urls(video_urls)
        else:
            # Извлекаем из проанализированных видео
            channel_ids = list(set([v.channel_id for v in videos_data if v.channel_id]))
        
        channel_ids = channel_ids[:args.max_channels]  # Ограничиваем количество
        print(f"✅ Найдено {len(channel_ids)} уникальных каналов")
        
        # === ЭТАП 4: Анализ каналов ===
        print(f"\n🏢 Этап 4: Анализ каналов (0/{len(channel_ids)})...")
        channels_data = analyzer.analyze_channels_batch(channel_ids)
        print(f"✅ Проанализировано {len(channels_data)} каналов")
        
        # === ЭТАП 5: Контент-анализ ===
        print(f"\n🧠 Этап 5: Дополнительный контент-анализ...")
        if videos_data:
            analyzer.enhance_video_analysis(videos_data)
        analyzer.enhance_channel_analysis(channels_data)
        print(f"✅ Контент-анализ завершен")
        
        # === ЭТАП 6: Генерация отчетов ===
        print(f"\n📊 Этап 6: Генерация отчетов...")
        
        report_files = []
        if args.format in ['excel', 'both']:
            excel_files = analyzer.create_excel_reports(videos_data, channels_data)
            report_files.extend(excel_files)
        
        if args.format in ['json', 'both']:
            json_files = analyzer.create_json_reports(videos_data, channels_data)
            report_files.extend(json_files)
        
        # === ЗАВЕРШЕНИЕ ===
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 АНАЛИЗ ЗАВЕРШЕН!")
        print(f"⏱️  Время выполнения: {duration}")
        print(f"📊 Статистика:")
        print(f"   • Видео проанализировано: {len(videos_data)}")
        print(f"   • Каналов проанализировано: {len(channels_data)}")
        print(f"   • Отчетов создано: {len(report_files)}")
        
        print(f"\n📁 Результаты сохранены:")
        for file_path in report_files:
            print(f"   • {file_path}")
        
        print(f"\n💡 Рекомендации:")
        if len(videos_data) > 0:
            avg_views = sum(v.views for v in videos_data) / len(videos_data)
            print(f"   • Средние просмотры в нише: {avg_views:,.0f}")
        
        if len(channels_data) > 0:
            active_channels = [c for c in channels_data if c.videos_last_3_months > 0]
            print(f"   • Активных каналов (публикации за 3 мес): {len(active_channels)}")
        
        # Основные инсайты
        print(f"\n🔍 Основные инсайты:")
        print(f"   • Проверьте топ-видео в отчете для анализа успешных форматов")
        print(f"   • Изучите позиционирование лидирующих каналов")
        print(f"   • Обратите внимание на частоту публикаций конкурентов")
        
    except KeyboardInterrupt:
        print("\n⏹️  Анализ прерван пользователем")
        logger.info("Анализ прерван пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        print(f"\n❌ Критическая ошибка: {e}")
        print("📋 Подробности в логе: logs/youtube_analysis.log")
        sys.exit(1)

if __name__ == "__main__":
    main()