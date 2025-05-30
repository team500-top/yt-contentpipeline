"""
YouTube Analyzer - Complete Minimal Server
Полный минимальный сервер со всеми необходимыми endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from pathlib import Path
import uuid
from datetime import datetime

# Модели данных
class TaskCreate(BaseModel):
    keywords: List[str] = []
    channels: List[str] = []
    order_by: str = "relevance"
    max_videos_per_source: int = 20

# Пути
current_dir = Path(__file__).parent
project_root = current_dir.parent
frontend_path = project_root / "frontend"

# Создание приложения
app = FastAPI(title="YouTube Analyzer - Complete")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище данных в памяти (для тестирования)
tasks_storage = {}
videos_storage = []
channels_storage = []

# === HTML PAGES ===

@app.get("/")
async def root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>index.html not found</h1>")

@app.get("/app.js")
async def get_app_js():
    js_path = frontend_path / "app.js"
    if js_path.exists():
        return FileResponse(str(js_path), media_type="application/javascript")
    return JSONResponse({"error": "app.js not found"}, status_code=404)

@app.get("/style.css")
async def get_style_css():
    css_path = frontend_path / "style.css"
    if css_path.exists():
        return FileResponse(str(css_path), media_type="text/css")
    return JSONResponse({"error": "style.css not found"}, status_code=404)

@app.get("/{filename}.html")
async def get_html_file(filename: str):
    file_path = frontend_path / f"{filename}.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return HTMLResponse(f"<h1>{filename}.html not found</h1>", status_code=404)

# === API ENDPOINTS ===

# Health & Info
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "YouTube Analyzer"}

@app.get("/api")
async def api_info():
    return {
        "name": "YouTube Analyzer API",
        "version": "2.0.0",
        "endpoints": {
            "tasks": "/api/tasks",
            "youtube": "/api/youtube",
            "data": "/api/data",
            "config": "/api/config"
        }
    }

# Tasks endpoints
@app.get("/api/tasks")
@app.get("/api/tasks/")
async def get_tasks():
    return list(tasks_storage.values())

@app.post("/api/tasks")
@app.post("/api/tasks/")
async def create_task(task: TaskCreate):
    task_id = str(uuid.uuid4())
    new_task = {
        "task_id": task_id,
        "status": "created",
        "progress": 0,
        "total_items": len(task.keywords) + len(task.channels),
        "created_at": datetime.now().isoformat(),
        "config": task.dict()
    }
    tasks_storage[task_id] = new_task
    
    # Симуляция выполнения
    new_task["status"] = "running"
    
    return {
        "task_id": task_id,
        "status": "created",
        "message": "Задача создана успешно"
    }

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id in tasks_storage:
        return tasks_storage[task_id]
    raise HTTPException(status_code=404, detail="Задача не найдена")

@app.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: str):
    if task_id in tasks_storage:
        tasks_storage[task_id]["status"] = "paused"
        return {"message": "Задача поставлена на паузу", "status": "paused"}
    raise HTTPException(status_code=404, detail="Задача не найдена")

@app.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: str):
    if task_id in tasks_storage:
        tasks_storage[task_id]["status"] = "running"
        return {"message": "Задача возобновлена", "status": "running"}
    raise HTTPException(status_code=404, detail="Задача не найдена")

# Config endpoints
@app.get("/api/config")
@app.get("/api/config/")
async def get_config():
    return {
        "youtube_api_key": "",
        "max_long_videos_channel": 5,
        "max_long_videos_search": 5,
        "max_shorts_channel": 5,
        "max_shorts_search": 5,
        "whisper_model": "base"
    }

@app.post("/api/config")
@app.post("/api/config/")
async def update_config(config: dict):
    return {
        "message": "Конфигурация обновлена",
        "status": "success",
        "config": config
    }

# Data endpoints
@app.get("/api/data/videos")
async def get_videos(limit: int = 50, offset: int = 0):
    # Возвращаем тестовые данные
    if not videos_storage:
        return []
    return videos_storage[offset:offset+limit]

@app.get("/api/data/channels")
async def get_channels():
    # Возвращаем тестовые данные
    return channels_storage

@app.get("/api/data/stats")
async def get_stats():
    return {
        "total_videos": len(videos_storage),
        "total_channels": len(channels_storage),
        "total_tasks": len(tasks_storage),
        "completed_tasks": sum(1 for t in tasks_storage.values() if t.get("status") == "completed"),
        "avg_engagement": 3.5,
        "videos_by_type": {"shorts": 10, "long": 20},
        "active_tasks": sum(1 for t in tasks_storage.values() if t.get("status") == "running")
    }

@app.get("/api/data/export")
async def export_data():
    return {
        "filename": "youtube_analysis_2024.xlsx",
        "status": "exported",
        "created_at": datetime.now().isoformat()
    }

@app.delete("/api/data/clear")
async def clear_database():
    videos_storage.clear()
    channels_storage.clear()
    tasks_storage.clear()
    return {"message": "База данных очищена", "status": "success"}

# YouTube endpoints (заглушки)
@app.get("/api/youtube/search")
async def search_youtube(query: str, max_results: int = 10):
    return {
        "videos": [],
        "count": 0,
        "query": query
    }

@app.get("/api/youtube/channel/{channel_id}")
async def get_channel_info(channel_id: str):
    return {
        "channel_id": channel_id,
        "channel_title": "Test Channel",
        "subscriber_count": 1000
    }

# Добавим несколько тестовых данных
def add_test_data():
    # Тестовая задача
    test_task_id = str(uuid.uuid4())
    tasks_storage[test_task_id] = {
        "task_id": test_task_id,
        "status": "completed",
        "progress": 10,
        "total_items": 10,
        "created_at": datetime.now().isoformat(),
        "config": {
            "keywords": ["python tutorial", "web development"],
            "channels": [],
            "order_by": "relevance"
        }
    }
    
    # Тестовые видео
    for i in range(5):
        videos_storage.append({
            "video_id": f"test_video_{i}",
            "title": f"Test Video {i+1}",
            "channel_title": "Test Channel",
            "views": 1000 * (i + 1),
            "likes": 100 * (i + 1),
            "comments": 10 * (i + 1),
            "engagement_rate": 3.5,
            "is_short": i % 2 == 0,
            "publish_date": datetime.now().isoformat()
        })
    
    # Тестовый канал
    channels_storage.append({
        "channel_id": "test_channel_1",
        "channel_title": "Test Channel",
        "subscriber_count": 10000,
        "video_count": 50,
        "view_count": 100000
    })

# Монтирование статических файлов (в конце!)
app.mount("/", StaticFiles(directory=str(frontend_path)), name="static")

if __name__ == "__main__":
    # Добавляем тестовые данные
    add_test_data()
    
    print("\n" + "="*50)
    print("YouTube Analyzer - Complete Server")
    print("="*50)
    print(f"Frontend: {frontend_path}")
    print("URL: http://localhost:8000")
    print("\nТестовые страницы:")
    print("- http://localhost:8000/simple_ui.html")
    print("- http://localhost:8000/test.html")
    print("- http://localhost:8000/debug_routes.html")
    print("- http://localhost:8000/standalone.html")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)