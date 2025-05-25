@echo off
title YouTube Analyzer - Stopping Services
color 0C

echo ================================================================================
echo                        Stopping YouTube Analyzer Services
echo ================================================================================
echo.

:: Остановка Python процессов
echo [1/3] Stopping Python processes...
taskkill /F /FI "WINDOWTITLE eq Celery Worker - YouTube Analyzer*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FastAPI - YouTube Analyzer*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq python*" >nul 2>&1
echo Python processes stopped

:: Остановка Redis
echo [2/3] Stopping Redis container...
docker-compose down >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Could not stop Redis container
) else (
    echo Redis container stopped
)

:: Очистка
echo [3/3] Cleaning up...
:: Удаление временных файлов
if exist "temp\*.tmp" del /q "temp\*.tmp" >nul 2>&1

echo.
echo ================================================================================
echo                          All services have been stopped
echo ================================================================================
echo.
pause