@echo off
cd /d "%~dp0"

:: Check if service is running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% == 0 (
    echo Останавливаем YouTube Analyzer...
    call stop.bat
) else (
    echo Запускаем YouTube Analyzer...
    start "YouTube Analyzer Service" /MIN run.bat
    timeout /t 3 >nul
    start http://localhost:8000
)

exit