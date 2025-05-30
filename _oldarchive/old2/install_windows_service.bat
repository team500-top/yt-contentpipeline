@echo off
echo ═══════════════════════════════════════════
echo  YouTube Analyzer - Установка как сервис
echo ═══════════════════════════════════════════
echo.

:: Проверка прав администратора
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Требуются права администратора!
    echo Запустите от имени администратора
    pause
    exit /b 1
)

cd /d "%~dp0"

:: Установка NSSM (Non-Sucking Service Manager)
if not exist "nssm.exe" (
    echo Загрузка NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    move nssm-2.24\win64\nssm.exe .
    rmdir /s /q nssm-2.24
    del nssm.zip
)

:: Остановка старого сервиса если есть
nssm stop YouTubeAnalyzer >nul 2>&1
nssm remove YouTubeAnalyzer confirm >nul 2>&1

:: Установка нового сервиса
echo Установка сервиса...
nssm install YouTubeAnalyzer "%CD%\venv\Scripts\python.exe" "%CD%\backend\main.py"
nssm set YouTubeAnalyzer AppDirectory "%CD%"
nssm set YouTubeAnalyzer DisplayName "YouTube Analyzer Service"
nssm set YouTubeAnalyzer Description "YouTube Content Analysis Service"
nssm set YouTubeAnalyzer Start SERVICE_AUTO_START

:: Настройка перезапуска при сбое
nssm set YouTubeAnalyzer AppThrottle 1500
nssm set YouTubeAnalyzer AppStopMethodSkip 14
nssm set YouTubeAnalyzer AppStopMethodConsole 1500
nssm set YouTubeAnalyzer AppStopMethodWindow 1500
nssm set YouTubeAnalyzer AppStopMethodThreads 1500

:: Запуск сервиса
echo Запуск сервиса...
nssm start YouTubeAnalyzer

echo.
echo ✅ Сервис установлен и запущен!
echo.
echo Управление:
echo   - Автозапуск при включении ПК: ДА
echo   - Остановка: nssm stop YouTubeAnalyzer
echo   - Запуск: nssm start YouTubeAnalyzer
echo   - Удаление: nssm remove YouTubeAnalyzer
echo.
echo Интерфейс доступен: http://localhost:8000
echo.
pause