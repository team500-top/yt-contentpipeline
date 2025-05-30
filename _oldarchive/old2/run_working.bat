@echo off
echo ========================================
echo  YouTube Analyzer - Working Server
echo ========================================
echo.

cd /d "C:\youtube-analyzer"

:: Активируем виртуальное окружение
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Запускаем рабочий сервер
echo Запускаем рабочий сервер...
python backend\working_server.py

pause