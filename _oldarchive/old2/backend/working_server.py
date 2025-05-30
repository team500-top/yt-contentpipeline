"""
YouTube Analyzer - Исправленный сервер
Сохраните как backend/working_server.py
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
from pathlib import Path

# Настройка путей
current_dir = Path(__file__).parent
project_root = current_dir.parent
frontend_path = project_root / "frontend"

# Добавляем пути для импорта
sys.path.insert(0, str(project_root))

# Создание приложения
app = FastAPI(
    title="YouTube Analyzer",
    description="Анализ YouTube контента",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Проверка наличия frontend файлов
if not frontend_path.exists():
    print(f"❌ Ошибка: папка frontend не найдена по пути {frontend_path}")
    exit(1)

print(f"✅ Frontend путь: {frontend_path}")

# API заглушки для тестирования
@app.get("/health")
async def health():
    return {"status": "ok", "service": "YouTube Analyzer"}

@app.get("/api")
async def api_info():
    return {
        "name": "YouTube Analyzer API",
        "version": "2.0",
        "services_loaded": True
    }

@app.get("/api/tasks")
async def get_tasks():
    # Пробуем загрузить из БД
    try:
        from backend.database import DatabaseManager
        db = DatabaseManager()
        tasks = db.get_all_tasks()
        return tasks
    except:
        # Возвращаем тестовые данные
        return []

@app.get("/api/tasks/active")
async def get_active_tasks():
    return {"count": 0, "tasks": []}

@app.get("/api/config")
async def get_config():
    return {
        "youtube_api_key": "",
        "max_long_videos_channel": 5,
        "max_long_videos_search": 5,
        "max_shorts_channel": 5,
        "max_shorts_search": 5,
        "whisper_model": "base"
    }

@app.get("/api/data/videos")
async def get_videos(limit: int = 50, offset: int = 0):
    try:
        from backend.database import DatabaseManager
        db = DatabaseManager()
        videos = db.get_videos(limit, offset)
        return videos
    except:
        return []

@app.get("/api/data/channels")
async def get_channels():
    try:
        from backend.database import DatabaseManager
        db = DatabaseManager()
        channels = db.get_channels()
        return channels
    except:
        return []

@app.get("/api/data/stats")
async def get_stats():
    try:
        from backend.database import DatabaseManager
        db = DatabaseManager()
        stats = db.get_statistics()
        return stats
    except:
        return {
            "total_videos": 0,
            "total_channels": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "avg_engagement": 0,
            "videos_by_type": {}
        }

# Обработка главной страницы
@app.get("/")
async def read_index():
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>index.html не найден</h1>")

# Специальные обработчики для JS и CSS
@app.get("/app.js")
async def get_app_js():
    js_file = frontend_path / "app.js"
    if js_file.exists():
        return FileResponse(
            str(js_file),
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache"}
        )
    return JSONResponse({"error": "app.js not found"}, status_code=404)

@app.get("/style.css")
async def get_style_css():
    css_file = frontend_path / "style.css"
    if css_file.exists():
        return FileResponse(
            str(css_file),
            media_type="text/css",
            headers={"Cache-Control": "no-cache"}
        )
    return JSONResponse({"error": "style.css not found"}, status_code=404)

# Монтируем статические файлы (должно быть в самом конце!)
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

# Попробуем загрузить полные сервисы
try:
    from backend.services import (
        tasks_router, youtube_router,
        analysis_router, data_router, config_router
    )
    
    # Подключаем роутеры
    app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(youtube_router, prefix="/api/youtube", tags=["YouTube"])
    app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
    app.include_router(data_router, prefix="/api/data", tags=["Data"])
    app.include_router(config_router, prefix="/api/config", tags=["Config"])
    
    print("✅ Все сервисы загружены успешно!")
    
except Exception as e:
    print(f"⚠️  Сервисы не загружены: {e}")
    print("   Используются заглушки API")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 YouTube Analyzer - Working Server")
    print("="*50)
    print(f"📁 Frontend: {frontend_path}")
    print(f"🌐 URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nНажмите Ctrl+C для остановки")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")