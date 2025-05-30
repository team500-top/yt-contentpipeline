# 🎬 YouTube Analyzer - Установка для Windows

## 📋 Пошаговая инструкция установки

### 🔧 Предварительные требования

**Системные требования:**
- Windows 10/11 (64-bit)
- 8+ GB RAM (рекомендуется 16+ GB)
- 5+ GB свободного места на диске
- Стабильное интернет-соединение

**Программное обеспечение:**
- Python 3.8+ (обязательно)
- Git (опционально)

### 📥 Шаг 1: Установка Python

1. **Скачайте Python** с официального сайта: https://python.org/downloads/
2. **Запустите установщик** с правами администратора
3. **ВАЖНО!** ✅ Отметьте "Add Python to PATH"
4. Выберите "Customize installation"
5. Убедитесь что выбраны:
   - ✅ pip
   - ✅ py launcher
   - ✅ Add Python to environment variables

**Проверка установки:**
```cmd
# Откройте командную строку (Win+R -> cmd)
python --version
pip --version
```

### 📁 Шаг 2: Автоматическая установка

**Вариант A: Скачать и запустить setup_windows.bat**

1. Создайте папку `C:\youtube-analyzer`
2. Скачайте файл `setup_windows.bat` в эту папку
3. Запустите `setup_windows.bat` **от имени администратора**
4. Следуйте инструкциям в консоли

**Вариант B: Ручная установка**

1. Создайте структуру папок:
```cmd
mkdir C:\youtube-analyzer
cd C:\youtube-analyzer
mkdir data
mkdir reports  
mkdir logs
mkdir src
mkdir templates
mkdir tests
```

2. Создайте виртуальное окружение:
```cmd
python -m venv venv
venv\Scripts\activate
```

3. Установите зависимости:
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
pip install tqdm rich colorama diskcache
```

4. Загрузите языковые модели:
```cmd
# NLTK данные
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# spaCy модель
python -m spacy download ru_core_news_sm
```

### 📄 Шаг 3: Размещение файлов проекта

Поместите следующие файлы в `C:\youtube-analyzer\`:

```
C:\youtube-analyzer\
├── main.py                    # Основной скрипт
├── config.py                  # Конфигурация  
├── requirements.txt           # Зависимости
├── .env.example              # Пример настроек
├── .env                      # Ваши настройки (создать)
├── run_analysis.bat          # Скрипт запуска
├── setup_windows.bat         # Скрипт установки
├── src\
│   ├── __init__.py
│   ├── analyzer.py
│   ├── utils.py
│   └── ... (другие модули)
└── venv\                     # Виртуальное окружение
```

### ⚙️ Шаг 4: Настройка конфигурации

1. **Скопируйте .env.example в .env:**
```cmd
copy .env.example .env
```

2. **Отредактируйте .env файл** в любом текстовом редакторе:

```env
# Основные настройки
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt
MAX_TOTAL_VIDEOS=50
MAX_CHANNELS_TO_ANALYZE=20
MAX_WORKERS=4
LOG_LEVEL=INFO
LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log
```

### 🔑 Шаг 5: Получение YouTube API ключа (рекомендуется)

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите **YouTube Data API v3**:
   - API & Services → Library
   - Найдите "YouTube Data API v3"
   - Нажмите Enable
4. Создайте API ключ:
   - API & Services → Credentials  
   - Create Credentials → API Key
   - Скопируйте ключ
5. Добавьте ключ в `.env` файл:
```env
YOUTUBE_API_KEY=AIzaSyC-ваш-ключ-здесь
```

### 🍪 Шаг 6: Настройка cookies (для обхода ограничений)

**Если возникают проблемы с доступом к YouTube:**

1. **Установите расширение браузера:**
   - Chrome: "Get cookies.txt"
   - Firefox: "cookies.txt"

2. **Экспортируйте cookies:**
   - Зайдите на youtube.com
   - Нажмите на иконку расширения
   - Выберите "Export" → "Netscape format"
   - Сохраните как `C:\youtube-analyzer\cookies.txt`

### 🚀 Шаг 7: Первый запуск

**Автоматический запуск:**
```cmd
# Дважды кликните по файлу или выполните в cmd:
C:\youtube-analyzer\run_analysis.bat
```

**Ручной запуск:**
```cmd
cd C:\youtube-analyzer
venv\Scripts\activate
python main.py --offer "Онлайн курсы Python программирования"
```

## 🛠️ Устранение неполадок

### ❌ Python не найден

**Ошибка:** `'python' is not recognized as an internal or external command`

**Решение:**
1. Переустановите Python с галочкой "Add Python to PATH"
2. Или добавьте Python в PATH вручную:
   - Win+R → `sysdm.cpl`
   - Advanced → Environment Variables
   - System Variables → Path → Edit
   - Добавьте пути: `C:\Python3X\` и `C:\Python3X\Scripts\`

### ❌ Ошибки установки пакетов

**Ошибка:** Не устанавливаются пакеты через pip

**Решение:**
```cmd
# Обновите pip
python -m pip install --upgrade pip

# Установка с дополнительными параметрами
pip install --user package_name
pip install --trusted-host pypi.org --trusted-host pypi.python.org package_name
```

### ❌ spaCy модель не загружается

**Ошибка:** `Can't find model 'ru_core_news_sm'`

**Решение:**
```cmd
# Попробуйте альтернативные команды
python -m spacy download ru_core_news_sm --user
pip install https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.7.0/ru_core_news_sm-3.7.0-py3-none-any.whl
```

### ❌ YouTube блокирует запросы

**Ошибка:** `HTTP 429` или `Access denied`

**Решение:**
1. Добавьте cookies.txt файл
2. Настройте прокси в .env:
```env
HTTP_PROXY=http://proxy.example.com:8080
```
3. Увеличьте задержки:
```env
REQUEST_DELAY=5.0
MAX_WORKERS=2
```

### ❌ Недостаточно памяти

**Ошибка:** `MemoryError` или медленная работа

**Решение:**
1. Уменьшите количество видео:
```cmd
python main.py --offer "ваш оффер" --max-videos 25 --max-channels 10
```
2. Отключите извлечение субтитров:
```cmd
python main.py --offer "ваш оффер" --no-transcripts
```

### ❌ Проблемы с правами доступа

**Ошибка:** `Permission denied` при создании файлов

**Решение:**
1. Запустите командную строку от имени администратора
2. Измените права папки:
   - ПКМ на папке → Properties → Security
   - Дайте полные права для вашего пользователя

## 📊 Проверка установки

**Тест системы:**
```cmd
cd C:\youtube-analyzer
venv\Scripts\activate
python -c "
import requests, pandas, yt_dlp, nltk, openpyxl
print('✅ Все основные библиотеки работают!')
"
```

**Тест анализатора:**
```cmd
python main.py --dry-run --offer "тест"
```

## 🔄 Обновление

**Обновление зависимостей:**
```cmd
cd C:\youtube-analyzer
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

**Обновление языковых моделей:**
```cmd
python -m spacy download ru_core_news_sm --upgrade
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## 📞 Поддержка

**Если проблемы не решаются:**

1. **Проверьте логи:**
```cmd
type C:\youtube-analyzer\logs\youtube_analysis.log
```

2. **Создайте issue** с описанием проблемы и приложите:
   - Версию Python: `python --version`
   - Версию ОС: `systeminfo | findstr "OS"`
   - Текст ошибки из логов
   - Используемые параметры запуска

3. **Полная переустановка:**
```cmd
# Удалите папку
rmdir /s /q C:\youtube-analyzer

# Повторите установку с начала
```

---

**🎉 После успешной установки вы сможете анализировать YouTube конкурентов одной командой!**