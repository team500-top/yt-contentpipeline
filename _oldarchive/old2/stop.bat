@echo off
echo Остановка YouTube Analyzer...

:: Find and kill Python processes running our app
for /f "tokens=2" %%i in ('tasklist ^| findstr /i "python.exe"') do (
    taskkill /PID %%i /F 2>nul
)

echo YouTube Analyzer остановлен
timeout /t 2 >nul