# 🎬 YouTube Analyzer - Полная инструкция установки и использования

## 📋 Системные требования

- **ОС**: Windows 10/11 (64-bit)
- **Python**: 3.8 или выше
- **ОЗУ**: 8+ GB (рекомендуется 16+ GB)
- **Диск**: 5+ GB свободного места
- **Интернет**: Стабильное подключение

## 🚀 Способ 1: Автоматическая установка (Рекомендуется)

### Шаг 1: Скачивание проекта

1. **Создайте папку проекта:**
```cmd
mkdir C:\youtube-analyzer
cd C:\youtube-analyzer
```

2. **Скачайте проект с GitHub:**
   - Перейдите на https://github.com/your-username/youtube-analyzer
   - Нажмите "Code" → "Download ZIP"
   - Распакуйте все файлы в `C:\youtube-analyzer\`

3. **Альтернативно через Git:**
```cmd
git clone https://github.com/your-username/youtube-analyzer.git C:\youtube-analyzer
cd C:\youtube-analyzer
```

### Шаг 2: Автоматическая установка

1. **Запустите автоустановщик:**
   - ПКМ на `УСТАНОВИТЬ_ВСЕ.bat`
   - Выберите "Запуск от имени администратора"
   - Следуйте инструкциям в консоли

2. **Что происходит автоматически:**
   - ✅ Проверка и установка Python (если нужно)
   - ✅ Создание виртуального окружения
   - ✅ Установка всех зависимостей
   - ✅ Загрузка языковых моделей
   - ✅ Создание конфигурационных файлов
   - ✅ Создание ярлыка на рабочем столе

### Шаг 3: Первый запуск

1. **Дважды кликните ярлык "YouTube Analyzer" на рабочем столе**
2. **Или запустите `БЫСТРЫЙ_СТАРТ.bat`**

## 🔧 Способ 2: Ручная установка

### Шаг 1: Установка Python

1. Скачайте Python с https://python.org/downloads/
2. **ВАЖНО!** ✅ Отметьте "Add Python to PATH"
3. Установите с правами администратора

### Шаг 2: Создание проекта

```cmd
# Создание структуры
mkdir C:\youtube-analyzer
cd C:\youtube-analyzer
mkdir data reports logs src templates tests .cache

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install --upgrade pip
```

### Шаг 3: Установка зависимостей

```cmd
# Основные библиотеки
pip install requests beautifulsoup4 pandas numpy python-dotenv openpyxl

# YouTube библиотеки
pip install yt-dlp youtube-transcript-api google-api-python-client

# NLP библиотеки
pip install nltk spacy textstat

# Визуализация
pip install matplotlib seaborn wordcloud

# Утилиты
pip install tqdm rich colorama diskcache fake-useragent
```

### Шаг 4: Языковые модели

```cmd
# NLTK данные
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# spaCy модель
python -m spacy download ru_core_news_sm
```

### Шаг 5: Скачивание файлов проекта

1. Скачайте все файлы из GitHub в `C:\youtube-analyzer\`
2. Убедитесь что структура соответствует:

```
C:\youtube-analyzer\
├── main.py
├── config.py
├── .env.example
├── БЫСТРЫЙ_СТАРТ.bat
├── src\
│   ├── __init__.py
│   ├── utils.py
│   └── analyzer.py (создайте, если отсутствует)
└── venv\
```

## ⚙️ Настройка

### 1. Создание файла .env

```cmd
copy .env.example .env
notepad .env
```

### 2. Основные настройки

```env
# YouTube API ключ (рекомендуется)
YOUTUBE_API_KEY=your_api_key_here

# Cookies файл (при блокировках)
YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt

# Лимиты производительности
MAX_TOTAL_VIDEOS=50
MAX_CHANNELS_TO_ANALYZE=20
MAX_WORKERS=4

# Функциональность
ENABLE_TRANSCRIPT_EXTRACTION=true
ENABLE_CONTENT_ANALYSIS=true
EXCEL_OUTPUT_ENABLED=true

# Логирование
LOG_LEVEL=INFO
LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log
```

### 3. Получение YouTube API ключа (опционально, но рекомендуется)

1. **Перейдите в Google Cloud Console:**
   - https://console.cloud.google.com/

2. **Создайте проект:**
   - Нажмите "Select a project" → "New Project"
   - Введите название проекта
   - Нажмите "Create"

3. **Включите YouTube Data API v3:**
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "YouTube Data API v3"
   - Нажмите "Enable"

4. **Создайте API ключ:**
   - Перейдите в "APIs & Services" → "Credentials"
   - Нажмите "Create Credentials" → "API Key"
   - Скопируйте ключ

5. **Добавьте в .env:**
```env
YOUTUBE_API_KEY=AIzaSyC-ваш-ключ-здесь
```

### 4. Настройка cookies (при блокировках)

1. **Установите расширение браузера:**
   - Chrome/Edge: "Get cookies.txt LOCALLY"
   - Firefox: "cookies.txt"

2. **Экспортируйте cookies:**
   - Зайдите на youtube.com
   - Нажмите на иконку расширения
   - Выберите "Export" → "Netscape format"
   - Сохраните как `C:\youtube-analyzer\cookies.txt`

## 🎮 Использование

### Способ 1: Интерактивное меню (Рекомендуется)

1. **Запустите `БЫСТРЫЙ_СТАРТ.bat`**
2. **Выберите "Запустить анализ конкурентов"**
3. **Введите описание вашего продукта/услуги**
4. **Выберите тип анализа:**
   - 🏃 Быстрый (5 минут) - для первого знакомства
   - 📈 Стандартный (15 минут) - оптимальный вариант
   - 🔬 Детальный (30 минут) - максимум информации

### Способ 2: Командная строка

```cmd
cd C:\youtube-analyzer
venv\Scripts\activate

# Базовый анализ
python main.py --offer "Онлайн курсы Python программирования"

# Расширенный анализ
python main.py --offer "Фитнес тренировки дома" --max-videos 100 --max-channels 25

# Быстрый анализ без субтитров
python main.py --offer "Кулинарные рецепты" --no-transcripts --max-videos 30
```

### Способ 3: Простой запуск

1. **Запустите `run_analysis.bat`**
2. **Следуйте инструкциям в консоли**

## 📊 Примеры использования

### IT-сфера
```cmd
python main.py --offer "Курсы веб-разработки" --keywords "html,css,javascript,react,программирование"
```

### Бизнес-консультации
```cmd
python main.py --offer "Бизнес консультации для стартапов" --keywords "стартап,бизнес план,инвестиции"
```

### Фитнес и здоровье
```cmd
python main.py --offer "Домашние тренировки для похудения" --keywords "фитнес дома,похудение,тренировки"
```

### Образование
```cmd
python main.py --offer "Онлайн школа английского языка" --keywords "английский онлайн,изучение языка"
```

## 📈 Результаты анализа

### Создаются 3 Excel файла:

**1. `videos_analysis_YYYYMMDD_HHMMSS.xlsx`**
- URL и основные метрики каждого видео
- Анализ темы и формата
- Глобальная проблема, которую решает видео
- Вопросы зрителей и ответы спикера
- Призывы к действию (CTA)
- Обоснование популярности темы
- Мнение спикера

**2. `channels_analysis_YYYYMMDD_HHMMSS.xlsx`**
- Статистика активности каналов
- Анализ контент-стратегии
- Определение целевой аудитории
- Позиционирование канала
- Предлагаемые продукты/услуги
- Воронка продаж
- Фишки эффективности

**3. `summary_report_YYYYMMDD_HHMMSS.xlsx`**
- Общая статистика проекта
- Топ видео и каналов по метрикам
- Трендовые темы и форматы
- Рекомендации по стратегии
- Конкурентный анализ

### Где найти результаты:
- 📁 `C:\youtube-analyzer\reports\`
- 📊 Автоматически откроется папка после анализа
- 💡 Через меню "Просмотр готовых отчетов"

## 🛠️ Устранение неполадок

### ❌ "Python не найден"

**Решение:**
1. Переустановите Python с https://python.org/downloads/
2. ✅ Обязательно отметьте "Add Python to PATH"
3. Перезагрузите компьютер
4. Проверьте: `python --version`

### ❌ "Ошибка установки пакетов"

**Решение:**
```cmd
# Обновите pip
python -m pip install --upgrade pip

# Установка с дополнительными параметрами
pip install --user package_name
pip install --trusted-host pypi.org --trusted-host pypi.python.org package_name
```

### ❌ "YouTube блокирует запросы"

**Решение:**
1. Добавьте cookies.txt файл (инструкция выше)
2. Настройте прокси в .env:
```env
HTTP_PROXY=http://proxy.example.com:8080
```
3. Увеличьте задержки:
```env
REQUEST_DELAY=5.0
MAX_WORKERS=2
```

### ❌ "Медленная работа"

**Решение:**
1. Уменьшите количество видео:
```cmd
python main.py --offer "ваш оффер" --max-videos 25 --max-channels 10
```
2. Отключите субтитры:
```cmd
python main.py --offer "ваш оффер" --no-transcripts
```
3. Увеличьте потоки (если много ОЗУ):
```env
MAX_WORKERS=6
```

### ❌ "Файлы не найдены"

**Решение:**
1. Убедитесь что все файлы в `C:\youtube-analyzer\`
2. Проверьте структуру папок
3. Переустановите проект с начала

## 🔍 Диагностика

### Проверка системы:
```cmd
cd C:\youtube-analyzer
БЫСТРЫЙ_СТАРТ.bat
# Выберите "Диагностика системы"
```

### Проверка конфигурации:
```cmd
cd C:\youtube-analyzer
venv\Scripts\activate
python -c "from config import validate_config; print(validate_config())"
```

### Просмотр логов:
```cmd
type C:\youtube-analyzer\logs\youtube_analysis.log
```

## 🎯 Советы по использованию

### Для лучших результатов:

1. **Точно опишите ваш оффер:**
   - ❌ "курсы"
   - ✅ "Онлайн курсы Python программирования для начинающих"

2. **Добавьте релевантные ключевые слова:**
```cmd
--keywords "python,программирование,курсы,обучение,для начинающих"
```

3. **Начните со стандартного анализа:**
   - 50 видео, 20 каналов - оптимальный баланс

4. **Используйте YouTube API ключ:**
   - Значительно повышает стабильность
   - Больше данных, меньше блокировок

5. **Анализируйте результаты:**
   - Изучите топ-видео по просмотрам
   - Обратите внимание на успешные форматы
   - Проанализируйте частоту публикаций лидеров

## 📞 Поддержка

### При проблемах:

1. **Проверьте логи:** `logs\youtube_analysis.log`
2. **Запустите диагностику** через `БЫСТРЫЙ_СТАРТ.bat`
3. **Создайте issue на GitHub** с описанием проблемы
4. **Приложите информацию:**
   - Версия Python: `python --version`
   - Версия ОС: `systeminfo | findstr "OS"`
   - Текст ошибки из логов
   - Используемые параметры

## 🎉 Поздравляем!

Теперь у вас есть мощный инструмент для анализа YouTube конкурентов! 

**Следующие шаги:**
1. 🚀 Запустите первый анализ
2. 📊 Изучите результаты в Excel
3. 💡 Примените инсайты к вашей стратегии
4. 🔄 Регулярно отслеживайте конкурентов

---

**🌟 Удачи в развитии вашего YouTube канала!**