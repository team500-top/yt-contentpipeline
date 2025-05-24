"""
Патч для исправления проблем с загрузкой frontend
"""
import os
import shutil
from pathlib import Path

print("🔧 Исправление YouTube Analyzer...")

# Проверка структуры файлов
required_files = {
    "frontend/index.html": "Frontend HTML",
    "frontend/app.js": "Frontend JavaScript", 
    "frontend/style.css": "Frontend CSS",
    "backend/main.py": "Backend сервер",
    "backend/services.py": "Backend сервисы"
}

missing = []
for file, desc in required_files.items():
    if not Path(file).exists():
        missing.append(f"❌ {file} ({desc})")
    else:
        print(f"✅ {file} найден")

if missing:
    print("\n⚠️  Отсутствуют файлы:")
    for m in missing:
        print(m)
    print("\nПроверьте структуру проекта!")
    input("Нажмите Enter...")
    exit(1)

# Создание упрощенного запускающего файла
simple_server = '''"""
Упрощенный сервер для YouTube Analyzer
"""
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import sys

# Пути
current_dir = Path(__file__).parent
project_root = current_dir.parent
frontend_path = project_root / "frontend"

# Добавляем пути для импорта
sys.path.append(str(project_root))

# Импортируем сервисы
try:
    from backend.services import (
        tasks_router, youtube_router, 
        analysis_router, data_router, config_router
    )
    services_loaded = True
except Exception as e:
    print(f"⚠️  Ошибка загрузки сервисов: {e}")
    services_loaded = False

# Создаем приложение
app = FastAPI(title="YouTube Analyzer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API роутеры
if services_loaded:
    app.include_router(tasks_router, prefix="/api/tasks")
    app.include_router(youtube_router, prefix="/api/youtube")
    app.include_router(analysis_router, prefix="/api/analysis")
    app.include_router(data_router, prefix="/api/data")
    app.include_router(config_router, prefix="/api/config")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": "YouTube Analyzer"}

@app.get("/api")
async def api_info():
    return {
        "name": "YouTube Analyzer API",
        "version": "2.0",
        "services_loaded": services_loaded
    }

# Монтируем статические файлы
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    print("🚀 Запуск YouTube Analyzer (упрощенный режим)...")
    print(f"📁 Frontend путь: {frontend_path}")
    print(f"✅ Сервисы загружены: {services_loaded}")
    print("🌐 Откройте: http://localhost:8000")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
'''

# Сохраняем упрощенный сервер
with open("backend/simple_server.py", "w", encoding="utf-8") as f:
    f.write(simple_server)

print("\n✅ Создан упрощенный сервер!")

# Создаем новый батник для запуска
new_bat = '''@echo off
chcp 65001 >nul
title YouTube Analyzer - Simple Mode

cd /d "%~dp0"

if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
) else (
    echo Создаем виртуальное окружение...
    python -m venv venv
    call venv\\Scripts\\activate.bat
    pip install fastapi uvicorn python-multipart
)

cls
echo =======================================
echo    YouTube Analyzer - Simple Mode
echo =======================================
echo.

python backend/simple_server.py
'''

with open("run_simple.bat", "w", encoding="utf-8") as f:
    f.write(new_bat)

print("✅ Создан run_simple.bat")
print("\n🎯 Теперь запустите: run_simple.bat")
print("Это запустит упрощенную версию сервера для диагностики")

input("\nНажмите Enter...")