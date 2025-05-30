# 📁 Структура проекта YouTube Analyzer

## 🎯 Итоговая структура в папке `C:\youtube-analyzer\`

```
C:\youtube-analyzer\
├── 📄 УСТАНОВИТЬ_ВСЕ.bat              # Полная автоматическая установка
├── 📄 БЫСТРЫЙ_СТАРТ.bat               # Интерактивное меню запуска
├── 📄 setup_windows.bat               # Базовая установка зависимостей
├── 📄 run_analysis.bat                # Простой запуск анализа
├── 📄 main.py                         # Основной скрипт анализа
├── 📄 config.py                       # Конфигурация приложения
├── 📄 requirements.txt                # Python зависимости
├── 📄 .env                           # Настройки (создается при установке)
├── 📄 .env.example                   # Пример настроек
├── 📄 .gitignore                     # Git исключения
├── 📄 README.md                      # Документация проекта
├── 📄 УСТАНОВКА_WINDOWS.md           # Подробная инструкция установки
├── 📄 cookies.txt                    # YouTube cookies (опционально)
│
├── 📂 venv\                          # Виртуальное окружение Python
│   ├── Scripts\
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   └── activate.bat
│   └── Lib\
│
├── 📂 src\                           # Исходный код
│   ├── 📄 __init__.py
│   ├── 📄 analyzer.py                # Основной анализатор YouTube
│   ├── 📄 data_extractors.py         # Извлечение данных из YouTube
│   ├── 📄 content_analyzers.py       # NLP анализ контента
│   ├── 📄 report_generators.py       # Генерация Excel отчетов
│   └── 📄 utils.py                   # Вспомогательные функции
│
├── 📂 templates\                     # Шаблоны и стили
│   ├── 📄 __init__.py
│   ├── 📄 excel_styles.py            # Стили для Excel отчетов
│   └── 📄 report_templates.py        # Шаблоны отчетов
│
├── 📂 tests\                         # Тесты (для разработчиков)
│   ├── 📄 __init__.py
│   ├── 📄 test_analyzer.py
│   └── 📄 test_extractors.py
│
├── 📂 data\                          # Сырые данные (создается автоматически)
│   ├── 📄 videos_raw.json
│   ├── 📄 channels_raw.json
│   └── 📄 keywords_cache.json
│
├── 📂 reports\                       # Готовые отчеты (создается автоматически)
│   ├── 📊 videos_analysis_20241215_143022.xlsx
│   ├── 📊 channels_analysis_20241215_143022.xlsx
│   ├── 📊 summary_report_20241215_143022.xlsx
│   ├── 📈 views_distribution.png
│   ├── 📈 channels_activity.png
│   └── ☁️ titles_wordcloud.png
│
├── 📂 logs\                          # Логи выполнения (создается автоматически)
│   ├── 📄 youtube_analysis.log
│   ├── 📄 error.log
│   └── 📄 debug.log
│
└── 📂 .cache\                        # Кэш для ускорения (создается автоматически)
    ├── 📄 search_results.cache
    ├── 📄 video_data.cache
    └── 📄 channel_info.cache
```

## 🚀 Файлы для запуска

### 1. `УСТАНОВИТЬ_ВСЕ.bat` - Полная автоматическая установка
- ✅ Проверяет и устанавливает Python
- ✅ Создает виртуальное окружение
- ✅ Устанавливает все зависимости
- ✅ Загружает языковые модели
- ✅ Создает конфигурационные файлы
- ✅ Создает ярлык на рабочем столе
- ✅ Регистрирует в меню Пуск

### 2. `БЫСТРЫЙ_СТАРТ.bat` - Интерактивное меню
- 🎮 Главное меню с опциями
- 🚀 Запуск анализа с выбором параметров
- ⚙️ Настройка конфигурации
- 📊 Просмотр готовых отчетов
- 🔧 Диагностика системы
- 📚 Встроенная помощь

### 3. `run_analysis.bat` - Простой запуск
- 📝 Ввод оффера и параметров
- ⚡ Быстрый запуск без меню
- 📊 Автоматическое открытие результатов

## 🎯 Основные Python модули

### 1. `main.py` - Точка входа
```python
# Основные функции:
- parse_arguments()          # Парсинг параметров командной строки
- generate_keywords_from_offer()  # Генерация ключевых запросов
- display_analysis_plan()    # Показ плана анализа
- main()                     # Основная логика выполнения
```

### 2. `config.py` - Конфигурация
```python
# Классы и настройки:
- Config                     # Основная конфигурация из .env
- YouTubeConstants          # Константы для YouTube API
- ContentAnalysisConstants  # Константы для анализа контента
- ExcelStylesConfig         # Стили для Excel отчетов
```

### 3. `src/analyzer.py` - Основной анализатор
```python
# Основной класс:
- YouTubeAnalyzer           # Главный класс анализа
  - search_videos_by_keywords()     # Поиск видео
  - extract_video_data()            # Извлечение данных видео
  - analyze_channel()               # Анализ каналов
  - create_excel_reports()          # Создание отчетов
```

### 4. `src/utils.py` - Утилиты
```python
# Вспомогательные функции:
- setup_logging()           # Настройка логирования
- CacheManager             # Кэширование результатов
- ProgressTracker          # Отслеживание прогресса
- retry_on_error()         # Автоповторы при ошибках
- safe_request()           # Безопасные HTTP запросы
```

## 📊 Структура отчетов

### Excel файлы создаются с временной меткой:

**1. `videos_analysis_YYYYMMDD_HHMMSS.xlsx`**
- 📋 Лист "Анализ видео" - детальная информация по каждому видео
- 📈 Лист "Статистика" - агрегированные данные
- 🎯 Лист "Топ видео" - самые успешные видео

**2. `channels_analysis_YYYYMMDD_HHMMSS.xlsx`**
- 🏢 Лист "Анализ каналов" - подробная информация по каналам
- 📊 Лист "Сравнение" - сравнительная таблица каналов
- 🎯 Лист "Лидеры" - топовые каналы по метрикам

**3. `summary_report_YYYYMMDD_HHMMSS.xlsx`**
- 📋 Лист "Сводка" - общая статистика проекта
- 💡 Лист "Инсайты" - ключевые находки
- 🎯 Лист "Рекомендации" - actionable советы
- 📈 Лист "Тренды" - популярные темы и форматы

## 🔧 Конфигурационные файлы

### `.env` - Основные настройки
```env
# API и доступ
YOUTUBE_API_KEY=           # YouTube Data API ключ
YOUTUBE_COOKIES_FILE=      # Файл cookies
HTTP_PROXY=                # Прокси настройки

# Лимиты анализа
MAX_TOTAL_VIDEOS=50        # Максимум видео
MAX_CHANNELS_TO_ANALYZE=20 # Максимум каналов
MAX_WORKERS=4              # Параллельные потоки

# Функциональность
ENABLE_TRANSCRIPT_EXTRACTION=true  # Извлечение субтитров
ENABLE_CONTENT_ANALYSIS=true       # Анализ контента
EXCEL_OUTPUT_ENABLED=true          # Excel отчеты

# Логирование и кэш
LOG_LEVEL=INFO             # Уровень логирования
ENABLE_CACHING=true        # Кэширование
```

## 📝 Рабочие файлы (создаются автоматически)

### Данные
- `data/videos_raw.json` - Сырые данные видео
- `data/channels_raw.json` - Сырые данные каналов
- `data/keywords_cache.json` - Кэш поисковых запросов

### Логи
- `logs/youtube_analysis.log` - Основной лог
- `logs/error.log` - Логи ошибок
- `logs/debug.log` - Детальная отладка

### Кэш
- `.cache/search_results.cache` - Результаты поиска
- `.cache/video_data.cache` - Данные видео
- `.cache/channel_info.cache` - Информация о каналах

## 🎮 Использование

### Автоматическая установка:
```cmd
# Запустить от имени администратора:
УСТАНОВИТЬ_ВСЕ.bat
```

### Интерактивный запуск:
```cmd
# Дважды кликнуть:
БЫСТРЫЙ_СТАРТ.bat
```

### Командная строка:
```cmd
cd C:\youtube-analyzer
venv\Scripts\activate
python main.py --offer "Ваш оффер"
```

### Быстрый запуск:
```cmd
# Простой интерфейс:
run_analysis.bat
```

## 🔄 Обновление проекта

### Обновление зависимостей:
```cmd
cd C:\youtube-analyzer
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Очистка кэша:
```cmd
rmdir /s /q .cache
mkdir .cache
```

### Архивация результатов:
```cmd
# Создание архива отчетов по дате
mkdir "archive\%date%"
move reports\*.xlsx "archive\%date%\"
```

## 🛡️ Безопасность и приватность

### Защищенные файлы (не попадают в Git):
- `.env` - секретные настройки
- `cookies.txt` - личные данные браузера
- `logs/*.log` - могут содержать личную информацию
- `.cache/*` - кэшированные данные

### Рекомендации по безопасности:
- 🔐 Не передавайте `.env` файл третьим лицам
- 🍪 Регулярно обновляйте `cookies.txt`
- 🔄 Периодически меняйте YouTube API ключ
- 📁 Делайте резервные копии важных отчетов

---

**🎉 Структура проекта оптимизирована для максимального удобства использования в Windows!**