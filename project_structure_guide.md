# YouTube Competitor Analysis Tool

## Структура проекта

```
C:\youtube-analyzer\
├── .env                           # Секретные данные и конфигурация
├── .env.example                   # Пример файла .env
├── .gitignore                     # Игнорируемые Git файлы
├── requirements.txt               # Python зависимости
├── README.md                      # Документация проекта
├── main.py                        # Основной скрипт анализа
├── config.py                      # Конфигурация приложения
├── cookies.txt                    # Cookies для YouTube (опционально)
├── logs/                          # Папка для логов
│   └── youtube_analysis.log       # Лог файл
├── data/                          # Сырые данные
│   ├── videos_raw.json            # Сырые данные видео
│   └── channels_raw.json          # Сырые данные каналов
├── reports/                       # Готовые отчеты
│   ├── videos_analysis_YYYYMMDD_HHMMSS.xlsx
│   ├── channels_analysis_YYYYMMDD_HHMMSS.xlsx
│   └── summary_report_YYYYMMDD_HHMMSS.xlsx
├── src/                           # Исходный код
│   ├── __init__.py
│   ├── analyzer.py                # Основной класс анализатора
│   ├── data_extractors.py         # Извлечение данных
│   ├── content_analyzers.py       # Анализ контента
│   ├── report_generators.py       # Генерация отчетов
│   └── utils.py                   # Вспомогательные функции
├── templates/                     # Шаблоны отчетов
│   ├── excel_styles.py            # Стили для Excel
│   └── report_templates.py        # Шаблоны отчетов
└── tests/                         # Тесты
    ├── __init__.py
    ├── test_analyzer.py
    └── test_extractors.py
```

## Пошаговая установка

### 1. Создание папки проекта

```bash
# Создание основной папки
mkdir C:\youtube-analyzer
cd C:\youtube-analyzer
```

### 2. Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните необходимые данные:

```bash
cp .env.example .env
```

### 5. Установка языковых моделей

```bash
# NLTK данные
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# spaCy русская модель
python -m spacy download ru_core_news_sm
```

### 6. Получение YouTube Data API ключа (опционально)

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите YouTube Data API v3
4. Создайте API ключ
5. Добавьте ключ в файл `.env`

### 7. Настройка cookies для YouTube (опционально)

Если возникают проблемы с доступом:
1. Экспортируйте cookies из браузера в формате Netscape
2. Сохраните в файл `cookies.txt`
3. Укажите путь к файлу в `.env`

## Файлы конфигурации

### .env.example

```env
# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Файл с cookies для YouTube (опционально)
YOUTUBE_COOKIES_FILE=cookies.txt

# Прокси настройки (опционально)
HTTP_PROXY=
HTTPS_PROXY=

# Настройки парсинга
MAX_VIDEOS_PER_KEYWORD=10
MAX_TOTAL_VIDEOS=50
MAX_CHANNELS_TO_ANALYZE=20

# Задержки между запросами (секунды)
REQUEST_DELAY=2
API_REQUEST_DELAY=1

# Настройки обработки
ENABLE_TRANSCRIPT_EXTRACTION=true
ENABLE_CONTENT_ANALYSIS=true
ENABLE_SENTIMENT_ANALYSIS=false

# Настройки отчетов
EXCEL_OUTPUT_ENABLED=true
JSON_OUTPUT_ENABLED=true
CHARTS_ENABLED=true

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/youtube_analysis.log

# Параллельная обработка
MAX_WORKERS=4
ENABLE_PARALLEL_PROCESSING=true

# Кэширование
ENABLE_CACHING=true
CACHE_DURATION_HOURS=24
```

### requirements.txt

```txt
# Основные библиотеки
requests==2.31.0
beautifulsoup4==4.12.2
pandas==2.1.4
numpy==1.24.3
python-dotenv==1.0.0
openpyxl==3.1.2

# YouTube и медиа
yt-dlp==2023.12.30
youtube-transcript-api==0.6.1
google-api-python-client==2.110.0

# NLP и анализ текста
nltk==3.8.1
spacy==3.7.2
textstat==0.7.3

# Визуализация
matplotlib==3.8.2
seaborn==0.13.0
wordcloud==1.9.2

# Утилиты
tqdm==4.66.1
colorama==0.4.6
rich==13.7.0
```

### .gitignore

```gitignore
# Секретные данные
.env
cookies.txt

# Виртуальное окружение
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Логи
*.log
logs/*.log

# Временные файлы
*.tmp
*.temp
.cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Отчеты и данные (если не нужны в Git)
reports/*.xlsx
reports/*.json
data/*.json

# OS
.DS_Store
Thumbs.db
```

## Функциональность

### Основные возможности

1. **Поиск видео по ключевым запросам**
   - Автоматическая генерация ключевых слов из оффера
   - Поиск через YouTube Data API
   - Fallback через web scraping
   - Альтернативный поиск через yt-dlp

2. **Извлечение данных видео**
   - Метаданные (название, описание, статистика)
   - Субтитры (несколько методов получения)
   - Анализ контента и тематики
   - Определение CTA и проблематики

3. **Анализ каналов**
   - Статистика канала и активность
   - Анализ контент-стратегии
   - Определение целевой аудитории
   - Выявление воронки продаж

4. **Контент-анализ**
   - NLP обработка текстов
   - Извлечение ключевых тем
   - Анализ тональности
   - Определение формата контента

5. **Генерация отчетов**
   - Excel файлы с детальной аналитикой
   - Сводные дашборды
   - Визуализации и графики
   - Рекомендации по стратегии

### Дополнительные возможности

- **Множественные методы доступа** к YouTube API
- **Обход блокировок** через прокси и cookies
- **Кэширование результатов** для ускорения повторных запусков
- **Параллельная обработка** для увеличения скорости
- **Детальное логирование** всех операций
- **Graceful degradation** при недоступности сервисов

## Алгоритм работы

### 1. Инициализация (main.py)

```python
1. Загрузка конфигурации из .env
2. Настройка логирования
3. Инициализация анализатора
4. Проверка доступности API и сервисов
```

### 2. Генерация ключевых запросов

```python
Input: Оффер пользователя
↓
1. Токенизация оффера
2. Извлечение ключевых слов
3. Добавление модификаторов ("как", "топ", "обзор")
4. Создание комбинаций ключевых слов
↓
Output: Список ключевых запросов
```

### 3. Поиск видео

```python
For each ключевое_слово:
    ├── Try: YouTube Data API поиск
    ├── Fallback: Web scraping поиск  
    ├── Fallback: yt-dlp поиск
    └── Delay между запросами
    
Результат: Список URL видео (до 50 штук)
```

### 4. Извлечение данных видео

```python
For each video_url:
    ├── Извлечение video_id
    ├── Получение метаданных:
    │   ├── Try: yt-dlp extraction
    │   ├── Fallback: Direct page parsing
    │   └── Fallback: API запрос
    ├── Получение субтитров:
    │   ├── Try: YouTube Transcript API
    │   ├── Try: yt-dlp subtitles  
    │   └── Try: Direct subtitle URLs
    ├── Контент-анализ:
    │   ├── Определение темы/формата
    │   ├── Извлечение проблематики
    │   ├── Поиск вопросов/ответов
    │   ├── Анализ CTA
    │   └── Мнение спикера
    └── Сохранение в VideoData объект
```

### 5. Анализ каналов

```python
For each unique_channel_id:
    ├── Получение информации о канале:
    │   ├── Try: YouTube Data API
    │   ├── Try: Web scraping
    │   └── Try: yt-dlp
    ├── Получение списка видео канала
    ├── Временной анализ активности
    ├── Контент-анализ:
    │   ├── Основные темы
    │   ├── Ключевые слова  
    │   ├── Типы CTA
    │   ├── Анализ воронки
    │   ├── Целевая аудитория
    │   ├── Позиционирование
    │   └── Фишки эффективности
    └── Сохранение в ChannelData объект
```

### 6. Контент-анализ (NLP Pipeline)

```python
For each text_content:
    ├── Токенизация (NLTK)
    ├── Удаление стоп-слов
    ├── Извлечение именованных сущностей (spaCy)
    ├── Частотный анализ слов
    ├── Определение тональности
    ├── Извлечение ключевых фраз
    └── Семантический анализ
```

### 7. Генерация отчетов

```python
1. Подготовка данных:
   ├── Агрегация статистики
   ├── Вычисление метрик
   └── Подготовка визуализаций

2. Создание Excel отчетов:
   ├── Лист "Анализ видео"
   ├── Лист "Анализ каналов"  
   ├── Лист "Сводная статистика"
   ├── Лист "Рекомендации"
   └── Применение стилей

3. Сохранение файлов:
   ├── reports/videos_analysis_TIMESTAMP.xlsx
   ├── reports/channels_analysis_TIMESTAMP.xlsx
   └── reports/summary_report_TIMESTAMP.xlsx
```

### 8. Обработка ошибок и устойчивость

```python
Error Handling Strategy:
├── Rate limiting с exponential backoff
├── Retry механизм для API запросов
├── Graceful degradation при недоступности сервисов
├── Логирование всех ошибок
├── Продолжение работы при частичных сбоях
└── Сохранение промежуточных результатов
```

## Запуск

### Базовый запуск

```bash
python main.py
```

### Запуск с параметрами

```bash
python main.py --offer "Онлайн курс по Python" --max-videos 100
```

### Примеры использования

```bash
# Анализ конкурентов для IT курсов
python main.py --offer "Курсы программирования Python" --keywords "python обучение,python курс,программирование с нуля"

# Анализ с использованием прокси
python main.py --offer "Фитнес тренировки" --proxy "http://proxy:8080"

# Только анализ каналов без извлечения субтитров
python main.py --offer "Бизнес консультации" --no-transcripts --channels-only
```

## Результаты анализа

### Excel отчеты содержат:

#### Анализ видео (videos_analysis.xlsx)
- URL, название, описание
- Статистика просмотров, лайков, комментариев
- Анализ темы и формата
- Глобальная проблема ЦА
- Вопросы зрителей и ответы спикера
- Призывы к действию (CTA)
- Обоснование популярности темы
- Проверка актуальности
- Мнение спикера

#### Анализ каналов (channels_analysis.xlsx)
- Основная информация о канале
- Статистика активности
- Анализ контент-стратегии
- Целевая аудитория
- Позиционирование
- Предлагаемые продукты
- Воронка продаж
- Фишки эффективности

#### Сводный отчет (summary_report.xlsx)
- Общая статистика проекта
- Топ видео и каналов
- Трендовые темы
- Рекомендации по стратегии
- Конкурентный анализ
- Возможности для развития

## Устранение неполадок

### Частые проблемы:

1. **YouTube блокирует запросы**
   - Используйте cookies.txt
   - Настройте прокси
   - Увеличьте задержки между запросами

2. **Не удается получить субтитры**
   - Проверьте наличие субтитров у видео
   - Используйте несколько методов извлечения
   - Проверьте настройки языка

3. **API ключ не работает**
   - Проверьте лимиты API
   - Убедитесь что API включен
   - Проверьте правильность ключа

4. **Медленная работа**
   - Увеличьте количество воркеров
   - Включите кэширование
   - Используйте SSD диск

### Логи и отладка:

Все операции логируются в `logs/youtube_analysis.log`. Уровень логирования можно настроить в `.env`:

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```