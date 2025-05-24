@echo off
chcp 65001 >nul
title YouTube Analyzer - Fixed Version

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Создаем виртуальное окружение...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

cls
echo =======================================
echo    YouTube Analyzer - Fixed Version
echo =======================================
echo.
echo Запускаем исправленный сервер...
echo.

python backend/fixed_server.py

pause