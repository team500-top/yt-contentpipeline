"""
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
