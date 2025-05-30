@echo off
chcp 65001 >nul
title YouTube Analyzer - Полная установка
color 0B

echo.
echo ███████╗███████╗████████╗██╗   ██╗██████╗ 
echo ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
echo ███████╗█████╗     ██║   ██║   ██║██████╔╝
echo ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝ 
echo ███████║███████╗   ██║   ╚██████╔╝██║     
echo ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     
echo.
echo          YOUTUBE ANALYZER - ПОЛНАЯ УСТАНОВКА
echo               Автоматическая настройка системы
echo.
echo =============================================================================

REM Проверка прав администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА!
    echo.
    echo 🔒 Для установки необходимо запустить этот файл от имени администратора:
    echo    1. Щелкните правой кнопкой мыши по файлу
    echo    2. Выберите "Запуск от имени администратора"
    echo.
    pause
    exit /b 1
)

echo ✅ Права администратора получены
echo.

REM Создание базовой структуры
echo 📁 Создание структуры проекта...
if not exist "C:\" (
    echo ❌ Диск C: недоступен!
    pause
    exit /b 1
)

REM Создание основной папки с правами
mkdir "C:\youtube-analyzer" 2>nul
cd /d "C:\youtube-analyzer"

REM Установка полных прав для папки
icacls "C:\youtube-analyzer" /grant Everyone:F /T /Q >nul 2>&1

echo ✅ Папка C:\youtube-analyzer создана с полными правами

REM Создание подпапок
for %%d in (data reports logs src templates tests .cache venv) do (
    mkdir "%%d" 2>nul
)

echo ✅ Структура папок создана

REM Проверка и установка Python
echo.
echo 🐍 Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден!
    echo.
    echo 📥 Автоматическая установка Python...
    
    REM Скачивание и установка Python
    powershell -Command "& {
        $url = 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe'
        $output = 'python-installer.exe'
        Write-Host 'Скачивание Python...'
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host 'Установка Python...'
        Start-Process -FilePath $output -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait
        Remove-Item $output
    }"
    
    REM Обновление PATH
    refreshenv >nul 2>&1
    
    REM Повторная проверка
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Автоматическая установка Python не удалась
        echo 🔧 Установите Python вручную с https://python.org/downloads/
        echo ⚠️  ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH"
        pause
        exit /b 1
    )
)

echo ✅ Python установлен:
python --version

REM Создание виртуального окружения
echo.
echo 🔧 Настройка виртуального окружения...
if not exist "venv\Scripts\python.exe" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
)

echo ✅ Виртуальное окружение создано

REM Активация и обновление pip
call venv\Scripts\activate
python -m pip install --upgrade pip --quiet

echo ✅ pip обновлен

REM Установка зависимостей поэтапно
echo.
echo 📦 Установка зависимостей...

echo   📊 Основные библиотеки...
pip install --quiet requests beautifulsoup4 pandas numpy python-dotenv
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки основных библиотек
    pause
    exit /b 1
)

echo   📁 Excel поддержка...
pip install --quiet openpyxl xlsxwriter
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки Excel библиотек
    pause
    exit /b 1
)

echo   📺 YouTube библиотеки...
pip install --quiet yt-dlp youtube-transcript-api google-api-python-client
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки YouTube библиотек
    pause
    exit /b 1
)

echo   🧠 NLP библиотеки...
pip install --quiet nltk spacy textstat
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки NLP библиотек
    pause
    exit /b 1
)

echo   📈 Визуализация...
pip install --quiet matplotlib seaborn wordcloud plotly
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки библиотек визуализации
    pause
    exit /b 1
)

echo   🛠️  Утилиты...
pip install --quiet tqdm rich colorama diskcache fake-useragent
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки утилит
    pause
    exit /b 1
)

echo ✅ Все зависимости установлены

REM Загрузка языковых моделей
echo.
echo 🌍 Загрузка языковых моделей...

echo   📝 NLTK данные...
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('vader_lexicon', quiet=True)
print('✅ NLTK данные загружены')
"

echo   🔤 spaCy модель...
python -m spacy download ru_core_news_sm --quiet
if %errorlevel% equ 0 (
    echo ✅ spaCy модель загружена
) else (
    echo ⚠️  spaCy модель не загружена (будет использован fallback)
)

REM Создание файлов конфигурации
echo.
echo ⚙️  Создание конфигурации...

REM Создание .env файла
(
echo # =============================================================================
echo # YouTube Analyzer Configuration - Автоматически создано
echo # =============================================================================
echo.
echo # YouTube Data API v3 Key
echo # Получить на: https://console.cloud.google.com/
echo YOUTUBE_API_KEY=
echo.
echo # Cookies файл для обхода ограничений
echo YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt
echo.
echo # Прокси настройки ^(опционально^)
echo HTTP_PROXY=
echo HTTPS_PROXY=
echo.
echo # Лимиты анализа
echo MAX_TOTAL_VIDEOS=50
echo MAX_CHANNELS_TO_ANALYZE=20
echo MAX_VIDEOS_PER_KEYWORD=10
echo.
echo # Производительность
echo MAX_WORKERS=4
echo REQUEST_DELAY=2.0
echo API_REQUEST_DELAY=1.0
echo.
echo # Функциональность
echo ENABLE_TRANSCRIPT_EXTRACTION=true
echo ENABLE_CONTENT_ANALYSIS=true
echo ENABLE_SENTIMENT_ANALYSIS=false
echo.
echo # Вывод
echo EXCEL_OUTPUT_ENABLED=true
echo JSON_OUTPUT_ENABLED=false
echo CHARTS_ENABLED=true
echo.
echo # Логирование
echo LOG_LEVEL=INFO
echo LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log
echo.
echo # Кэширование
echo ENABLE_CACHING=true
echo CACHE_DURATION_HOURS=24
) > .env

echo ✅ Базовая конфигурация .env создана

REM Создание .gitignore
(
echo # Секретные данные
echo .env
echo cookies.txt
echo *.key
echo.
echo # Python
echo __pycache__/
echo *.pyc
echo venv/
echo.
echo # Логи и кэш
echo logs/
echo .cache/
echo *.log
echo.
echo # Временные файлы
echo *.tmp
echo .DS_Store
echo Thumbs.db
) > .gitignore

echo ✅ .gitignore создан

REM Создание __init__.py файлов
echo. > src\__init__.py
echo. > templates\__init__.py  
echo. > tests\__init__.py

REM Создание requirements.txt
(
echo # YouTube Analyzer Requirements
echo requests==2.31.0
echo beautifulsoup4==4.12.2
echo pandas==2.1.4
echo numpy==1.24.3
echo python-dotenv==1.0.0
echo openpyxl==3.1.2
echo yt-dlp==2023.12.30
echo youtube-transcript-api==0.6.1
echo google-api-python-client==2.110.0
echo nltk==3.8.1
echo spacy==3.7.2
echo textstat==0.7.3
echo matplotlib==3.8.2
echo seaborn==0.13.0
echo wordcloud==1.9.2
echo tqdm==4.66.1
echo rich==13.7.0
echo colorama==0.4.6
echo diskcache==5.6.3
echo fake-useragent==1.4.0
) > requirements.txt

echo ✅ requirements.txt создан

REM Создание README файла
(
echo # YouTube Analyzer - Установлено успешно!
echo.
echo ## 🚀 Быстрый запуск
echo.
echo 1. Дважды кликните по файлу `БЫСТРЫЙ_СТАРТ.bat`
echo 2. Выберите "Запустить анализ конкурентов"
echo 3. Введите описание вашего продукта/услуги
echo 4. Дождитесь результатов в папке `reports\`
echo.
echo ## ⚙️ Настройка
echo.
echo - Отредактируйте файл `.env` для продвинутых настроек
echo - Добавьте YouTube API ключ для лучшей стабильности
echo - Настройте cookies.txt при блокировках
echo.
echo ## 📁 Структура
echo.
echo - `reports\` - Excel отчеты с результатами
echo - `logs\` - логи выполнения
echo - `data\` - промежуточные данные
echo - `.env` - конфигурация
echo.
echo Дата установки: %date% %time%
) > README.md

echo ✅ README.md создан

REM Проверка установки
echo.
echo ✅ Проверка установки...
python -c "
import sys
print(f'Python: {sys.version}')

packages = ['requests', 'pandas', 'yt_dlp', 'openpyxl', 'nltk']
missing = []

for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'✅ {pkg}')
    except ImportError:
        missing.append(pkg)
        print(f'❌ {pkg}')

if not missing:
    print('\\n🎉 Все компоненты установлены успешно!')
else:
    print(f'\\n⚠️ Отсутствуют: {missing}')
"

REM Создание ярлыка на рабочем столе
echo.
echo 🖥️  Создание ярлыка на рабочем столе...
powershell -Command "
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\YouTube Analyzer.lnk')
$Shortcut.TargetPath = 'C:\youtube-analyzer\БЫСТРЫЙ_СТАРТ.bat'
$Shortcut.WorkingDirectory = 'C:\youtube-analyzer'
$Shortcut.Description = 'YouTube Competitor Analysis Tool'
$Shortcut.Save()
"

if %errorlevel% equ 0 (
    echo ✅ Ярлык создан на рабочем столе
) else (
    echo ⚠️  Не удалось создать ярлык
)

REM Регистрация в меню Пуск
echo.
echo 📋 Регистрация в меню Пуск...
mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\YouTube Analyzer" 2>nul
powershell -Command "
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\YouTube Analyzer\YouTube Analyzer.lnk')
$Shortcut.TargetPath = 'C:\youtube-analyzer\БЫСТРЫЙ_СТАРТ.bat'
$Shortcut.WorkingDirectory = 'C:\youtube-analyzer'
$Shortcut.Save()
"

echo ✅ Добавлено в меню Пуск

echo.
echo =============================================================================
echo 🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
echo =============================================================================
echo.
echo 📊 YouTube Analyzer готов к работе!
echo.
echo 📁 Местоположение: C:\youtube-analyzer\
echo 🚀 Запуск: Ярлык на рабочем столе или меню Пуск
echo ⚙️  Конфигурация: .env файл
echo 📋 Документация: README.md
echo.
echo 🎯 СЛЕДУЮЩИЕ ШАГИ:
echo.
echo 1. 🔑 РЕКОМЕНДУЕТСЯ: Получить YouTube API ключ
echo    • Перейдите на https://console.cloud.google.com/
echo    • Включите YouTube Data API v3
echo    • Создайте API Key
echo    • Добавьте в .env файл: YOUTUBE_API_KEY=ваш_ключ
echo.
echo 2. 🍪 При проблемах с доступом: Настроить cookies
echo    • Установите расширение "Get cookies.txt"
echo    • Экспортируйте cookies с youtube.com
echo    • Сохраните как C:\youtube-analyzer\cookies.txt
echo.
echo 3. 🚀 ЗАПУСК АНАЛИЗА:
echo    • Дважды кликните ярлык "YouTube Analyzer" на рабочем столе
echo    • ИЛИ запустите БЫСТРЫЙ_СТАРТ.bat
echo    • ИЛИ найдите в меню Пуск
echo.
echo 📊 Результаты анализа будут сохранены в C:\youtube-analyzer\reports\
echo.
echo =============================================================================
echo.
echo 💡 ПОЛЕЗНЫЕ КОМАНДЫ:
echo.
echo Запуск анализа:     БЫСТРЫЙ_СТАРТ.bat
echo Настройки:          notepad .env
echo Просмотр отчетов:   explorer reports
echo Логи:               type logs\youtube_analysis.log
echo Обновление:         pip install --upgrade -r requirements.txt
echo.
echo =============================================================================

REM Предложение сразу запустить
echo.
set /p launch="🚀 Запустить YouTube Analyzer сейчас? (y/n): "
if /i "%launch%"=="y" (
    start "" "БЫСТРЫЙ_СТАРТ.bat"
)

echo.
echo 🎉 Установка завершена! Добро пожаловать в YouTube Analyzer!
echo.
pause