@echo off
chcp 65001 >nul
echo =============================================================================
echo YouTube Competitor Analysis Tool - Запуск анализа
echo =============================================================================
echo.

REM Переход в папку проекта
cd /d "C:\youtube-analyzer"

REM Проверка существования файлов
if not exist "main.py" (
    echo ❌ Файл main.py не найден в C:\youtube-analyzer\
    echo Убедитесь, что все файлы проекта скопированы в эту папку
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo ❌ Виртуальное окружение не найдено
    echo Запустите setup_windows.bat для установки
    pause
    exit /b 1
)

REM Активация виртуального окружения
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate

REM Проверка .env файла
if not exist ".env" (
    echo ⚠️  Файл .env не найден. Создаю базовый...
    echo YOUTUBE_API_KEY=>.env
    echo YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt>>.env
    echo MAX_TOTAL_VIDEOS=50>>.env
    echo MAX_CHANNELS_TO_ANALYZE=20>>.env
    echo MAX_WORKERS=4>>.env
    echo LOG_LEVEL=INFO>>.env
    echo LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log>>.env
)

echo.
echo 🎯 ЗАПУСК АНАЛИЗА YOUTUBE КОНКУРЕНТОВ
echo.

REM Получение оффера от пользователя
set /p offer="Введите ваш оффер (описание продукта/услуги): "

if "%offer%"=="" (
    echo ❌ Оффер не может быть пустым!
    pause
    exit /b 1
)

echo.
echo 📊 Опции анализа:
echo 1. Базовый анализ (50 видео, 20 каналов)
echo 2. Расширенный анализ (100 видео, 30 каналов)
echo 3. Быстрый анализ (только каналы, без субтитров)
echo 4. Пользовательские настройки
echo.

set /p choice="Выберите опцию (1-4): "

if "%choice%"=="1" (
    set params=--max-videos 50 --max-channels 20
    echo ✅ Выбран базовый анализ
) else if "%choice%"=="2" (
    set params=--max-videos 100 --max-channels 30 --parallel 6
    echo ✅ Выбран расширенный анализ
) else if "%choice%"=="3" (
    set params=--channels-only --no-transcripts --max-channels 25
    echo ✅ Выбран быстрый анализ
) else if "%choice%"=="4" (
    echo.
    set /p max_videos="Максимум видео (по умолчанию 50): "
    set /p max_channels="Максимум каналов (по умолчанию 20): "
    set /p parallel="Потоков (по умолчанию 4): "
    
    if "%max_videos%"=="" set max_videos=50
    if "%max_channels%"=="" set max_channels=20
    if "%parallel%"=="" set parallel=4
    
    set params=--max-videos %max_videos% --max-channels %max_channels% --parallel %parallel%
    echo ✅ Пользовательские настройки применены
) else (
    set params=--max-videos 50 --max-channels 20
    echo ✅ Использованы настройки по умолчанию
)

REM Дополнительные ключевые слова
echo.
set /p keywords="Дополнительные ключевые слова через запятую (необязательно): "

if not "%keywords%"=="" (
    set params=%params% --keywords "%keywords%"
)

echo.
echo 🚀 Запуск анализа...
echo Оффер: %offer%
echo Параметры: %params%
echo.

REM Запуск анализа
python main.py --offer "%offer%" %params%

set exit_code=%errorlevel%

echo.
if %exit_code% equ 0 (
    echo =============================================================================
    echo 🎉 АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!
    echo =============================================================================
    echo.
    echo 📁 Результаты сохранены в: C:\youtube-analyzer\reports\
    echo.
    echo 📊 Созданные отчеты:
    dir reports\*.xlsx /b 2>nul
    echo.
    echo 💡 Откройте Excel файлы для просмотра результатов анализа
    echo.
    
    REM Предложение открыть папку с отчетами
    set /p open_folder="Открыть папку с отчетами? (y/n): "
    if /i "%open_folder%"=="y" (
        explorer reports
    )
) else (
    echo =============================================================================
    echo ❌ АНАЛИЗ ЗАВЕРШЕН С ОШИБКАМИ
    echo =============================================================================
    echo.
    echo 📋 Проверьте лог файл: C:\youtube-analyzer\logs\youtube_analysis.log
    echo.
    echo 🔧 Возможные причины:
    echo - Проблемы с интернет соединением
    echo - Блокировка запросов YouTube (используйте прокси/cookies)
    echo - Неправильные настройки в .env файле
    echo - Недостаточно места на диске
    echo.
    echo 💡 Попробуйте:
    echo 1. Добавить cookies.txt файл
    echo 2. Настроить прокси в .env
    echo 3. Уменьшить количество видео для анализа
    echo 4. Проверить настройки антивируса/файрвола
)

echo.
echo =============================================================================
echo 📋 Полезные команды:
echo.
echo Повторный запуск:
echo   run_analysis.bat
echo.
echo Ручной запуск с параметрами:
echo   venv\Scripts\activate
echo   python main.py --offer "Ваш оффер" --max-videos 100
echo.
echo Очистка кэша:
echo   rmdir /s /q .cache
echo.
echo Просмотр логов:
echo   type logs\youtube_analysis.log
echo.
echo Обновление зависимостей:
echo   venv\Scripts\activate
echo   pip install --upgrade -r requirements.txt
echo.
echo =============================================================================

pause