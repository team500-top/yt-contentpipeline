@echo off
chcp 65001 >nul
echo =============================================================================
echo YouTube Competitor Analysis Tool - Установка для Windows
echo =============================================================================
echo.

REM Проверка версии Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден в системе!
    echo Установите Python 3.8+ с https://python.org/downloads/
    echo Убедитесь, что добавили Python в PATH при установке
    pause
    exit /b 1
)

echo ✅ Python найден:
python --version

REM Создание основной папки
echo.
echo 📁 Создание папки проекта...
if not exist "C:\youtube-analyzer" (
    mkdir "C:\youtube-analyzer"
    echo ✅ Папка C:\youtube-analyzer создана
) else (
    echo ℹ️  Папка C:\youtube-analyzer уже существует
)

cd /d "C:\youtube-analyzer"

REM Создание структуры папок
echo.
echo 📁 Создание структуры папок...
mkdir data 2>nul
mkdir reports 2>nul
mkdir logs 2>nul
mkdir src 2>nul
mkdir templates 2>nul
mkdir tests 2>nul
mkdir .cache 2>nul

echo ✅ Структура папок создана

REM Создание виртуального окружения
echo.
echo 🐍 Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    echo ✅ Виртуальное окружение создано
) else (
    echo ℹ️  Виртуальное окружение уже существует
)

REM Активация виртуального окружения
echo.
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate

REM Обновление pip
echo.
echo 📦 Обновление pip...
python -m pip install --upgrade pip

REM Установка основных зависимостей
echo.
echo 📦 Установка основных зависимостей...
pip install requests beautifulsoup4 pandas numpy python-dotenv openpyxl

REM Установка YouTube библиотек
echo.
echo 📺 Установка YouTube библиотек...
pip install yt-dlp youtube-transcript-api google-api-python-client

REM Установка NLP библиотек
echo.
echo 🧠 Установка NLP библиотек...
pip install nltk spacy textstat

REM Установка библиотек для визуализации
echo.
echo 📊 Установка библиотек визуализации...
pip install matplotlib seaborn wordcloud

REM Установка утилит
echo.
echo 🛠️  Установка утилит...
pip install tqdm rich colorama diskcache

REM Загрузка языковых моделей
echo.
echo 🌍 Загрузка языковых моделей...
echo Загрузка NLTK данных...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('✅ NLTK данные загружены')"

echo Загрузка spaCy модели для русского языка...
python -m spacy download ru_core_news_sm
if %errorlevel% equ 0 (
    echo ✅ spaCy модель загружена
) else (
    echo ⚠️  Не удалось загрузить spaCy модель. Будет использоваться fallback
)

REM Создание файла .env из примера
echo.
echo ⚙️  Создание конфигурации...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ Файл .env создан из .env.example
        echo ⚠️  Отредактируйте .env файл и добавьте ваши настройки
    ) else (
        echo > .env # YouTube API
        echo YOUTUBE_API_KEY=>> .env
        echo.>> .env
        echo # Cookies файл>> .env
        echo YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt>> .env
        echo.>> .env
        echo # Лимиты>> .env
        echo MAX_TOTAL_VIDEOS=50>> .env
        echo MAX_CHANNELS_TO_ANALYZE=20>> .env
        echo MAX_WORKERS=4>> .env
        echo.>> .env
        echo # Логирование>> .env
        echo LOG_LEVEL=INFO>> .env
        echo LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log>> .env
        echo ✅ Базовый файл .env создан
    )
) else (
    echo ℹ️  Файл .env уже существует
)

REM Создание базовых __init__.py файлов
echo.
echo 📝 Создание __init__.py файлов...
echo. > src\__init__.py
echo. > templates\__init__.py
echo. > tests\__init__.py

REM Проверка установки
echo.
echo ✅ Проверка установки...
python -c "
import sys
packages = ['requests', 'beautifulsoup4', 'pandas', 'yt_dlp', 'nltk', 'openpyxl']
missing = []
for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'✅ {pkg}')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg}')

if missing:
    print(f'\n⚠️  Отсутствуют пакеты: {missing}')
    print('Установите их командой: pip install ' + ' '.join(missing))
else:
    print('\n🎉 Все основные пакеты установлены!')
"

echo.
echo =============================================================================
echo 🎉 УСТАНОВКА ЗАВЕРШЕНА!
echo =============================================================================
echo.
echo 📁 Папка проекта: C:\youtube-analyzer
echo 🐍 Виртуальное окружение: C:\youtube-analyzer\venv
echo ⚙️  Конфигурация: C:\youtube-analyzer\.env
echo.
echo 📋 СЛЕДУЮЩИЕ ШАГИ:
echo.
echo 1. Отредактируйте файл .env и добавьте ваши настройки:
echo    - YouTube API ключ (необязательно, но рекомендуется)
echo    - Путь к cookies файлу (при необходимости)
echo    - Настройки лимитов и производительности
echo.
echo 2. Поместите основные файлы проекта в C:\youtube-analyzer\:
echo    - main.py
echo    - config.py
echo    - requirements.txt
echo    - src\*.py файлы
echo.
echo 3. Для запуска анализа:
echo    cd C:\youtube-analyzer
echo    venv\Scripts\activate
echo    python main.py --offer "Ваш оффер"
echo.
echo 4. Получение YouTube API ключа (опционально):
echo    https://console.cloud.google.com/
echo    YouTube Data API v3 -^> Credentials -^> Create API Key
echo.
echo 5. Настройка cookies для обхода ограничений (при необходимости):
echo    Установите расширение "Get cookies.txt" в браузер
echo    Экспортируйте cookies с youtube.com
echo    Сохраните как C:\youtube-analyzer\cookies.txt
echo.
echo =============================================================================
echo.

pause