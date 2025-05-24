@echo off
chcp 65001 >nul
title YouTube Analyzer - Simple Mode

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Создаем виртуальное окружение...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install fastapi uvicorn python-multipart
)

cls
echo =======================================
echo    YouTube Analyzer - Simple Mode
echo =======================================
echo.

python backend/simple_server.py
