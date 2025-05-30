@echo off
chcp 65001 >nul
title YouTube Analyzer - Быстрый старт
color 0A

echo.
echo ████████╗ ██████╗ ██╗   ██╗████████╗██╗   ██╗██████╗ ███████╗
echo ╚══██╔══╝██╔═══██╗██║   ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝
echo    ██║   ██║   ██║██║   ██║   ██║   ██║   ██║██████╔╝█████╗  
echo    ██║   ██║   ██║██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  
echo    ██║   ╚██████╔╝╚██████╔╝   ██║   ╚██████╔╝██████╔╝███████╗
echo    ╚═╝    ╚═════╝  ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝
echo.
echo              АНАЛИЗАТОР YOUTUBE КОНКУРЕНТОВ
echo        Автоматический анализ видео и каналов конкурентов
echo.
echo =============================================================================

REM Проверка существования папки проекта
if not exist "C:\youtube-analyzer" (
    echo ❌ Папка C:\youtube-analyzer не найдена!
    echo.
    echo 📋 Для установки выполните следующие шаги:
    echo.
    echo 1. Создайте папку C:\youtube-analyzer
    echo 2. Скачайте файл setup_windows.bat в эту папку
    echo 3. Запустите setup_windows.bat от имени администратора
    echo 4. Поместите файлы проекта в папку
    echo.
    pause
    exit /b 1
)

cd /d "C:\youtube-analyzer"

REM Проверка установки
if not exist "venv\Scripts\python.exe" (
    echo ❌ Виртуальное окружение не найдено!
    echo.
    echo 🔧 Запустите установку:
    echo    setup_windows.bat
    echo.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo ❌ Основные файлы проекта не найдены!
    echo.
    echo 📁 Убедитесь, что в C:\youtube-analyzer\ находятся:
    echo    - main.py
    echo    - config.py  
    echo    - src\*.py файлы
    echo    - requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Инициализация проекта...
call venv\Scripts\activate

REM Проверка .env файла
if not exist ".env" (
    echo ⚙️  Создание базовой конфигурации...
    (
        echo # YouTube Analyzer Configuration
        echo YOUTUBE_API_KEY=
        echo YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt
        echo MAX_TOTAL_VIDEOS=50
        echo MAX_CHANNELS_TO_ANALYZE=20
        echo MAX_WORKERS=4
        echo REQUEST_DELAY=2.0
        echo LOG_LEVEL=INFO
        echo LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log
        echo ENABLE_TRANSCRIPT_EXTRACTION=true
        echo ENABLE_CONTENT_ANALYSIS=true
        echo EXCEL_OUTPUT_ENABLED=true
    ) > .env
    echo ✅ Базовая конфигурация создана
)

echo.
echo 🎯 ДОБРО ПОЖАЛОВАТЬ В YOUTUBE ANALYZER!
echo.
echo 📊 Этот инструмент поможет вам:
echo    • Найти и проанализировать видео конкурентов
echo    • Изучить стратегии успешных каналов  
echo    • Определить популярные темы и форматы
echo    • Получить insights для вашей контент-стратегии
echo.

:main_menu
echo =============================================================================
echo 🎮 ГЛАВНОЕ МЕНЮ
echo =============================================================================
echo.
echo 1. 🚀 Запустить анализ конкурентов
echo 2. ⚙️  Настроить конфигурацию  
echo 3. 📊 Просмотреть готовые отчеты
echo 4. 🔧 Диагностика системы
echo 5. 📚 Помощь и документация
echo 6. 🚪 Выход
echo.

set /p choice="Выберите опцию (1-6): "

if "%choice%"=="1" goto analysis
if "%choice%"=="2" goto config
if "%choice%"=="3" goto reports  
if "%choice%"=="4" goto diagnostics
if "%choice%"=="5" goto help
if "%choice%"=="6" goto exit
echo ❌ Неверный выбор. Попробуйте снова.
goto main_menu

:analysis
cls
echo =============================================================================
echo 🚀 ЗАПУСК АНАЛИЗА КОНКУРЕНТОВ
echo =============================================================================
echo.

set /p offer="📝 Введите ваш оффер (описание продукта/услуги): "

if "%offer%"=="" (
    echo ❌ Оффер не может быть пустым!
    pause
    goto main_menu
)

echo.
echo 📊 Выберите тип анализа:
echo.
echo 1. 🏃 Быстрый (25 видео, 15 каналов, без субтитров) - ~5 минут
echo 2. 📈 Стандартный (50 видео, 20 каналов) - ~15 минут  
echo 3. 🔬 Детальный (100 видео, 30 каналов) - ~30 минут
echo 4. 🎯 Только каналы (без анализа видео) - ~10 минут
echo 5. ⚙️  Пользовательские настройки
echo.

set /p analysis_type="Выберите тип (1-5): "

if "%analysis_type%"=="1" (
    set params=--max-videos 25 --max-channels 15 --no-transcripts --parallel 6
    set duration=5 минут
) else if "%analysis_type%"=="2" (
    set params=--max-videos 50 --max-channels 20 --parallel 4
    set duration=15 минут
) else if "%analysis_type%"=="3" (
    set params=--max-videos 100 --max-channels 30 --parallel 6
    set duration=30 минут
) else if "%analysis_type%"=="4" (
    set params=--channels-only --max-channels 25 --no-transcripts
    set duration=10 минут
) else if "%analysis_type%"=="5" (
    echo.
    set /p max_videos="Максимум видео: "
    set /p max_channels="Максимум каналов: "
    set /p parallel="Количество потоков: "
    
    set params=--max-videos %max_videos% --max-channels %max_channels% --parallel %parallel%
    set duration=зависит от настроек
) else (
    set params=--max-videos 50 --max-channels 20
    set duration=15 минут
)

echo.
set /p keywords="📎 Дополнительные ключевые слова через запятую (Enter = пропустить): "
if not "%keywords%"=="" set params=%params% --keywords "%keywords%"

echo.
echo 🎯 Параметры анализа:
echo    • Оффер: %offer%
echo    • Настройки: %params%  
echo    • Ожидаемое время: %duration%
echo.

set /p confirm="▶️  Начать анализ? (y/n): "
if /i not "%confirm%"=="y" goto main_menu

echo.
echo 🚀 Запуск анализа... Это может занять несколько минут.
echo 💡 Не закрывайте это окно до завершения!
echo.

python main.py --offer "%offer%" %params%

set result=%errorlevel%

echo.
if %result% equ 0 (
    echo 🎉 АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!
    echo.
    echo 📁 Результаты сохранены в: C:\youtube-analyzer\reports\
    
    set /p open_reports="📊 Открыть папку с отчетами? (y/n): "
    if /i "%open_reports%"=="y" explorer reports
) else (
    echo ❌ Анализ завершился с ошибками
    echo 📋 Проверьте лог: logs\youtube_analysis.log
)

pause
goto main_menu

:config
cls
echo =============================================================================
echo ⚙️  НАСТРОЙКА КОНФИГУРАЦИИ
echo =============================================================================
echo.

echo Текущая конфигурация (.env):
echo.
type .env
echo.
echo.

echo 🔧 Опции настройки:
echo.
echo 1. 🔑 Добавить YouTube API ключ
echo 2. 🍪 Настроить cookies файл
echo 3. 🌐 Настроить прокси
echo 4. ⚡ Изменить лимиты производительности
echo 5. 📝 Редактировать .env в блокноте
echo 6. 🔄 Сбросить к настройкам по умолчанию
echo 7. ⬅️  Назад в главное меню
echo.

set /p config_choice="Выберите опцию (1-7): "

if "%config_choice%"=="1" (
    echo.
    echo 🔑 YouTube API Key настройка:
    echo.
    echo 📋 Для получения API ключа:
    echo 1. Перейдите на https://console.cloud.google.com/
    echo 2. Создайте проект и включите YouTube Data API v3
    echo 3. Создайте API Key в разделе Credentials
    echo.
    set /p api_key="Введите ваш API ключ (или Enter для пропуска): "
    
    if not "%api_key%"=="" (
        powershell -Command "(Get-Content .env) -replace 'YOUTUBE_API_KEY=.*', 'YOUTUBE_API_KEY=%api_key%' | Set-Content .env"
        echo ✅ API ключ сохранен
    )
) else if "%config_choice%"=="2" (
    echo.
    echo 🍪 Cookies настройка:
    echo.
    echo 📋 Для получения cookies:
    echo 1. Установите расширение "Get cookies.txt" в Chrome/Firefox
    echo 2. Зайдите на youtube.com
    echo 3. Экспортируйте cookies в Netscape формате
    echo 4. Сохраните файл как C:\youtube-analyzer\cookies.txt
    echo.
    
    if exist "cookies.txt" (
        echo ✅ Файл cookies.txt уже существует
    ) else (
        echo ⚠️  Файл cookies.txt не найден
        echo Создайте его согласно инструкции выше
    )
) else if "%config_choice%"=="3" (
    echo.
    echo 🌐 Прокси настройка:
    echo.
    set /p proxy="Введите прокси (формат: http://proxy:port или Enter для отключения): "
    
    powershell -Command "(Get-Content .env) -replace 'HTTP_PROXY=.*', 'HTTP_PROXY=%proxy%' | Set-Content .env"
    echo ✅ Настройки прокси сохранены
) else if "%config_choice%"=="4" (
    echo.
    echo ⚡ Настройка производительности:
    echo.
    set /p max_videos="Максимум видео (текущий: 50): "
    set /p max_channels="Максимум каналов (текущий: 20): "
    set /p max_workers="Количество потоков (текущий: 4): "
    
    if not "%max_videos%"=="" powershell -Command "(Get-Content .env) -replace 'MAX_TOTAL_VIDEOS=.*', 'MAX_TOTAL_VIDEOS=%max_videos%' | Set-Content .env"
    if not "%max_channels%"=="" powershell -Command "(Get-Content .env) -replace 'MAX_CHANNELS_TO_ANALYZE=.*', 'MAX_CHANNELS_TO_ANALYZE=%max_channels%' | Set-Content .env"
    if not "%max_workers%"=="" powershell -Command "(Get-Content .env) -replace 'MAX_WORKERS=.*', 'MAX_WORKERS=%max_workers%' | Set-Content .env"
    
    echo ✅ Настройки производительности сохранены
) else if "%config_choice%"=="5" (
    notepad .env
) else if "%config_choice%"=="6" (
    set /p confirm="⚠️  Сбросить все настройки? (y/n): "
    if /i "%confirm%"=="y" (
        copy .env.example .env >nul 2>&1
        echo ✅ Настройки сброшены к значениям по умолчанию
    )
) else if "%config_choice%"=="7" (
    goto main_menu
)

pause
goto config

:reports
cls
echo =============================================================================
echo 📊 ПРОСМОТР ГОТОВЫХ ОТЧЕТОВ
echo =============================================================================
echo.

if not exist "reports" (
    echo ❌ Папка с отчетами не найдена
    echo 🚀 Запустите анализ для создания отчетов
    pause
    goto main_menu
)

echo 📁 Доступные отчеты:
echo.
dir reports\*.xlsx /b 2>nul
echo.

if %errorlevel% neq 0 (
    echo ❌ Excel отчеты не найдены
    echo 🚀 Запустите анализ для создания отчетов
) else (
    echo 💡 Опции:
    echo.
    echo 1. 📂 Открыть папку с отчетами
    echo 2. 📊 Открыть последний отчет по видео
    echo 3. 🏢 Открыть последний отчет по каналам  
    echo 4. 📈 Открыть сводный отчет
    echo 5. ⬅️  Назад в главное меню
    echo.
    
    set /p report_choice="Выберите опцию (1-5): "
    
    if "%report_choice%"=="1" (
        explorer reports
    ) else if "%report_choice%"=="2" (
        for /f %%i in ('dir reports\videos_analysis_*.xlsx /b /o-d 2^>nul ^| findstr /n "^" ^| findstr "^1:"') do (
            set latest=%%i
            set latest=!latest:~2!
            start excel "reports\!latest!"
        )
    ) else if "%report_choice%"=="3" (
        for /f %%i in ('dir reports\channels_analysis_*.xlsx /b /o-d 2^>nul ^| findstr /n "^" ^| findstr "^1:"') do (
            set latest=%%i
            set latest=!latest:~2!
            start excel "reports\!latest!"
        )
    ) else if "%report_choice%"=="4" (
        for /f %%i in ('dir reports\summary_report_*.xlsx /b /o-d 2^>nul ^| findstr /n "^" ^| findstr "^1:"') do (
            set latest=%%i
            set latest=!latest:~2!
            start excel "reports\!latest!"
        )
    )
)

pause
goto main_menu

:diagnostics
cls
echo =============================================================================
echo 🔧 ДИАГНОСТИКА СИСТЕМЫ
echo =============================================================================
echo.

echo 🔍 Проверка компонентов системы...
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python: 
    python --version
) else (
    echo ❌ Python не найден или не работает
)

REM Проверка виртуального окружения
if exist "venv\Scripts\python.exe" (
    echo ✅ Виртуальное окружение: установлено
) else (
    echo ❌ Виртуальное окружение: не найдено
)

REM Проверка основных библиотек
echo.
echo 🔍 Проверка библиотек...
call venv\Scripts\activate
python -c "
import sys
packages = {
    'requests': 'HTTP запросы',
    'pandas': 'Обработка данных', 
    'yt_dlp': 'YouTube загрузчик',
    'openpyxl': 'Excel файлы',
    'nltk': 'NLP обработка'
}

for pkg, desc in packages.items():
    try:
        __import__(pkg.replace('-', '_'))
        print(f'✅ {pkg}: {desc}')
    except ImportError:
        print(f'❌ {pkg}: {desc} - НЕ УСТАНОВЛЕН')
"

echo.
echo 🔍 Проверка конфигурации...

if exist ".env" (
    echo ✅ Файл .env: найден
) else (
    echo ❌ Файл .env: не найден
)

if exist "cookies.txt" (
    echo ✅ Cookies файл: найден
) else (
    echo ⚠️  Cookies файл: не найден (необязательно)
)

echo.
echo 🔍 Проверка папок...
for %%d in (data reports logs src) do (
    if exist "%%d" (
        echo ✅ Папка %%d: существует
    ) else (
        echo ❌ Папка %%d: отсутствует
    )
)

echo.
echo 🔍 Системная информация:
echo Папка проекта: %cd%
echo Свободное место: 
powershell -command "Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq 'C:'} | Select-Object @{n='FreeSpace';e={[math]::Round($_.FreeSpace/1GB,2)}} | Format-Table -HideTableHeaders"

echo ОЗУ:
powershell -command "Get-WmiObject -Class Win32_ComputerSystem | Select-Object @{n='TotalRAM';e={[math]::Round($_.TotalPhysicalMemory/1GB,2)}} | Format-Table -HideTableHeaders"

echo.
echo 💡 Если есть проблемы:
echo - ❌ Python: переустановите с python.org
echo - ❌ Библиотеки: запустите setup_windows.bat
echo - ❌ Папки: будут созданы автоматически при первом запуске

pause
goto main_menu

:help
cls
echo =============================================================================
echo 📚 ПОМОЩЬ И ДОКУМЕНТАЦИЯ
echo =============================================================================
echo.

echo 🎯 НАЗНАЧЕНИЕ ПРОГРАММЫ:
echo YouTube Analyzer - это инструмент для анализа конкурентов на YouTube.
echo Программа автоматически находит и анализирует видео и каналы конкурентов,
echo создавая детальные отчеты с рекомендациями для вашей контент-стратегии.
echo.

echo 📋 ЧТО АНАЛИЗИРУЕТ ПРОГРАММА:
echo • Популярные видео по вашей тематике
echo • Статистику просмотров, лайков, комментариев
echo • Темы и форматы успешного контента
echo • Стратегии конкурирующих каналов
echo • Целевую аудиторию и позиционирование
echo • Призывы к действию (CTA) и воронки продаж
echo.

echo 📊 РЕЗУЛЬТАТЫ АНАЛИЗА:
echo • videos_analysis.xlsx - детальный анализ видео
echo • channels_analysis.xlsx - анализ каналов конкурентов
echo • summary_report.xlsx - сводный отчет с рекомендациями
echo.

echo 🚀 БЫСТРЫЙ СТАРТ:
echo 1. Запустите "Анализ конкурентов" из главного меню
echo 2. Введите описание вашего продукта/услуги
echo 3. Выберите тип анализа (рекомендуется "Стандартный")
echo 4. Дождитесь завершения (10-30 минут)
echo 5. Откройте Excel отчеты из папки reports\
echo.

echo ⚙️  НАСТРОЙКИ:
echo • YouTube API ключ - улучшает стабильность (необязательно)
echo • Cookies файл - помогает обходить блокировки
echo • Прокси - для анонимности и обхода ограничений
echo • Лимиты - количество анализируемого контента
echo.

echo 🔧 УСТРАНЕНИЕ ПРОБЛЕМ:
echo • Если YouTube блокирует - добавьте cookies или прокси
echo • Если медленно работает - уменьшите количество видео
echo • Если ошибки установки - запустите setup_windows.bat
echo • Логи ошибок сохраняются в logs\youtube_analysis.log
echo.

echo 📞 ПОДДЕРЖКА:
echo • Все логи и ошибки сохраняются автоматически
echo • При проблемах проверьте раздел "Диагностика"
echo • Документация: README.md и УСТАНОВКА_WINDOWS.md
echo.

pause
goto main_menu

:exit
echo.
echo 👋 Спасибо за использование YouTube Analyzer!
echo 💡 Результаты анализа сохранены в C:\youtube-analyzer\reports\
echo.
pause
exit /b 0