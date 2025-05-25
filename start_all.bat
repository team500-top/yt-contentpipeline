@echo off
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              YouTube Analyzer - Full System Start            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Проверка Redis
echo [1/3] Проверка Redis...
docker ps | findstr redis >nul
if errorlevel 1 (
    echo Запускаю Redis...
    start "Redis Docker" cmd /k "docker-compose up"
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ Redis уже работает
)

:: Запуск Celery
echo [2/3] Запуск Celery Worker...
start "Celery Worker" cmd /k "cd /d %~dp0 && venv\Scripts\activate && celery -A tasks worker --loglevel=info --pool=solo"

:: Пауза
timeout /t 3 /nobreak >nul

:: Запуск приложения
echo [3/3] Запуск веб-приложения...
start "YouTube Analyzer Web" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python main_no_eventlet.py"

:: Открытие браузера
timeout /t 5 /nobreak >nul
start http://127.0.0.1:8000

echo.
echo ✅ Система запущена!
echo.
echo Компоненты:
echo - Redis (Docker)
echo - Celery Worker (обработка задач)
echo - Web Interface (http://127.0.0.1:8000)
echo.
pause