@echo off
chcp 65001 >nul
title YouTube Analyzer Service

:: Check if already running
tasklist /FI "WINDOWTITLE eq YouTube Analyzer Service*" 2>nul | find /I "cmd.exe" >nul
if not errorlevel 1 (
    echo YouTube Analyzer уже запущен!
    echo Закройте существующее окно или используйте stop.bat
    pause
    exit /b
)

cd /d "%~dp0"

:: Quick start without reinstalling
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    goto :start_app
)

:: First time setup only
echo Первый запуск - настройка окружения...
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

:start_app
cls
echo =======================================
echo    YouTube Analyzer Service v2.0
echo =======================================
echo.
echo [%TIME%] Starting service...
echo.
echo Web Interface: http://localhost:8000
echo API Docs:      http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo =======================================
echo.

python backend/main.py