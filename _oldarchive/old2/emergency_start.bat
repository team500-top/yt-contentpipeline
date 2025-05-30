@echo off
echo ========================================
echo  YouTube Analyzer - Emergency Start
echo ========================================
echo.

cd /d "C:\youtube-analyzer"

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python не найден!
    echo Установите Python с python.org
    pause
    exit /b 1
)

:: Активируем виртуальное окружение если есть
if exist "venv\Scripts\activate.bat" (
    echo Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo Виртуальное окружение не найдено
    echo Используем глобальный Python
)

:: Проверяем установку FastAPI
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo FastAPI не установлен. Устанавливаем...
    pip install fastapi uvicorn
)

:: Запускаем сервер
echo.
echo Запуск сервера...
echo.

:: Сначала пробуем main.py
python backend\main.py
if errorlevel 1 (
    echo.
    echo main.py не работает, пробуем working_server.py
    python backend\working_server.py
    if errorlevel 1 (
        echo.
        echo Оба сервера не работают!
        echo Запускаем минимальный HTTP сервер...
        echo.
        cd frontend
        python -m http.server 8000
    )
)

pause