@echo off
title YouTube Analyzer Launcher
color 0A

echo ================================================================================
echo                         YouTube Content Analyzer v1.0.0
echo                  Content Strategy System for YouTube Creators
echo ================================================================================
echo.

:: Проверка виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo And: pip install -r requirements.txt
    pause
    exit /b 1
)

:: Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH!
    echo Please install Docker Desktop for Windows
    pause
    exit /b 1
)

echo [1/4] Checking Redis...
docker ps 2>nul | findstr "youtube_analyzer_redis" >nul
if errorlevel 1 (
    echo Starting Redis container...
    docker-compose up -d
    if errorlevel 1 (
        echo [ERROR] Failed to start Redis!
        echo Make sure Docker Desktop is running
        pause
        exit /b 1
    )
    timeout /t 5 /nobreak >nul
    echo Redis started successfully!
) else (
    echo Redis is already running
)

:: Проверка Redis соединения
echo [2/4] Testing Redis connection...
docker exec youtube_analyzer_redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis is not responding, waiting...
    timeout /t 5 /nobreak >nul
)

:: Запуск Celery Worker
echo [3/4] Starting Celery Worker...
start "Celery Worker - YouTube Analyzer" cmd /c "cd /d %~dp0 && venv\Scripts\activate && python -m celery -A tasks worker --loglevel=info --pool=solo"
timeout /t 3 /nobreak >nul

:: Запуск FastAPI
echo [4/4] Starting Web Application...
start "FastAPI - YouTube Analyzer" cmd /c "cd /d %~dp0 && venv\Scripts\activate && python main.py"

:: Ожидание запуска
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

:: Проверка доступности
echo.
echo Checking service availability...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Service is still starting, please wait...
    timeout /t 5 /nobreak >nul
)

:: Открытие браузера
echo.
echo Opening browser...
start http://127.0.0.1:8000

echo.
echo ================================================================================
echo                            SYSTEM STARTED SUCCESSFULLY!
echo ================================================================================
echo.
echo Services running:
echo   - Redis:     redis://localhost:6379
echo   - API:       http://127.0.0.1:8000
echo   - WebSocket: ws://127.0.0.1:8000/ws
echo   - API Docs:  http://127.0.0.1:8000/docs
echo.
echo To stop all services, close this window or press Ctrl+C
echo ================================================================================
echo.
pause