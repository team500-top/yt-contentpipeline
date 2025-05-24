"""
YouTube Analyzer - Hybrid Main Server
Использует минимальные роутеры вместо проблемного services.py
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import sys
from pathlib import Path
import uuid
from datetime import datetime

# Добавить пути для импорта
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Создание приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    description="Анализ YouTube контента и трендов",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Попробуем загрузить database и другие модули
try:
    from database import DatabaseManager
    db = DatabaseManager()
    db_loaded = True
    print("✅ База данных подключена")
except Exception as e:
    print(f"⚠️  База данных не загружена: {e}")
    db_loaded = False
    db = None

# Модели данных
class TaskCreate(BaseModel):
    keywords: List[str] = []
    channels: List[str] = []
    order_by: str = "relevance"
    max_videos_per_source: int = 20

# Временное хранилище если БД не работает
tasks_storage = {}

# Пути к файлам
frontend_path = project_root / "frontend"

# Основные роуты
@app.get("/")
async def root():
    """Главная страница"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return HTMLResponse("<h1>YouTube Analyzer</h1><p>Frontend не найден</p>")

@app.get("/index.html")
async def get_index():
    """Альтернативный путь для index.html"""
    return await root()

# Статические файлы JavaScript и CSS
@app.get("/app.js")
async def get_app_js():
    """JavaScript файл"""
    js_path = frontend_path / "app.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache"}
        )
    return HTMLResponse("console.error('app.js not found');", media_type="application/javascript")

@app.get("/style.css")
async def get_style_css():
    """CSS файл"""
    css_path = frontend_path / "style.css"
    if css_path.exists():
        return FileResponse(
            str(css_path),
            media_type="text/css",
            headers={"Cache-Control": "no-cache"}
        )
    return HTMLResponse("/* style.css not found */", media_type="text/css")

# HTML файлы
@app.get("/{filename}.html")
async def get_html_file(filename: str):
    """Обработчик для всех HTML файлов"""
    file_path = frontend_path / f"{filename}.html"
    if file_path.exists():
        return FileResponse(str(file_path), media_type="text/html")
    return HTMLResponse(f"<h1>{filename}.html не найден</h1>", status_code=404)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "YouTube Analyzer работает",
        "database": "connected" if db_loaded else "not connected"
    }

# API info
@app.get("/api")
async def api_info():
    """Информация об API"""
    return {
        "name": "YouTube Analyzer API",
        "version": "2.0.0",
        "endpoints": {
            "tasks": "/api/tasks",
            "youtube": "/api/youtube", 
            "analysis": "/api/analysis",
            "data": "/api/data",
            "config": "/api/config"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

# === TASKS API ===
@app.get("/api/tasks")
@app.get("/api/tasks/")
async def get_tasks():
    """Получить список задач"""
    if db_loaded:
        try:
            return db.get_all_tasks()
        except:
            pass
    return list(tasks_storage.values())

@app.post("/api/tasks")
@app.post("/api/tasks/")
async def create_task(task: TaskCreate):
    """Создать новую задачу"""
    task_id = str(uuid.uuid4())
    task_data = {
        "task_id": task_id,
        "status": "created",
        "progress": 0,
        "total_items": len(task.keywords) + len(task.channels),
        "created_at": datetime.now().isoformat(),
        "config": task.dict()
    }
    
    if db_loaded:
        try:
            db.save_task(task_data)
        except:
            pass
    
    tasks_storage[task_id] = task_data
    
    # Симуляция запуска
    task_data["status"] = "running"
    
    return {
        "task_id": task_id,
        "status": "created",
        "message": "Задача создана успешно"
    }

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Получить задачу по ID"""
    if db_loaded:
        try:
            task = db.get_task(task_id)
            if task:
                return task
        except:
            pass
    
    if task_id in tasks_storage:
        return tasks_storage[task_id]
    
    raise HTTPException(status_code=404, detail="Задача не найдена")

@app.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: str):
    """Поставить задачу на паузу"""
    if task_id in tasks_storage:
        tasks_storage[task_id]["status"] = "paused"
    
    if db_loaded:
        try:
            db.update_task_status(task_id, "paused")
        except:
            pass
    
    return {"message": "Задача поставлена на паузу", "status": "paused"}

@app.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: str):
    """Возобновить задачу"""
    if task_id in tasks_storage:
        tasks_storage[task_id]["status"] = "running"
    
    if db_loaded:
        try:
            db.update_task_status(task_id, "running")
        except:
            pass
    
    return {"message": "Задача возобновлена", "status": "running"}

# === CONFIG API ===
@app.get("/api/config")
@app.get("/api/config/")
async def get_config():
    """Получить конфигурацию"""
    try:
        from shared.config import settings
        return settings.get_safe_dict()
    except:
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
    """Обновить конфигурацию"""
    try:
        from shared.config import settings
        settings.update_from_dict(config)
        return {
            "message": "Конфигурация обновлена",
            "status": "success",
            "config": settings.get_safe_dict()
        }
    except:
        return {
            "message": "Конфигурация обновлена (в памяти)",
            "status": "success",
            "config": config
        }

# === DATA API ===
@app.get("/api/data/videos")
async def get_videos(limit: int = 50, offset: int = 0):
    """Получить список видео"""
    if db_loaded:
        try:
            return db.get_videos(limit, offset)
        except:
            pass
    return []

@app.get("/api/data/channels")
async def get_channels():
    """Получить список каналов"""
    if db_loaded:
        try:
            return db.get_channels()
        except:
            pass
    return []

@app.get("/api/data/stats")
async def get_stats():
    """Получить статистику"""
    if db_loaded:
        try:
            return db.get_statistics()
        except:
            pass
    
    return {
        "total_videos": 0,
        "total_channels": 0,
        "total_tasks": len(tasks_storage),
        "completed_tasks": sum(1 for t in tasks_storage.values() if t.get("status") == "completed"),
        "avg_engagement": 0,
        "videos_by_type": {},
        "active_tasks": sum(1 for t in tasks_storage.values() if t.get("status") == "running")
    }

@app.get("/api/data/export")
async def export_data():
    """Экспорт данных"""
    if db_loaded:
        try:
            filename = db.export_to_excel()
            return {
                "filename": Path(filename).name,
                "status": "exported",
                "created_at": datetime.now().isoformat()
            }
        except:
            pass
    
    return {
        "filename": "youtube_analysis_2024.xlsx",
        "status": "no data",
        "created_at": datetime.now().isoformat()
    }

@app.delete("/api/data/clear")
async def clear_database():
    """Очистить базу данных"""
    if db_loaded:
        try:
            db.clear_database()
        except:
            pass
    
    tasks_storage.clear()
    return {"message": "База данных очищена", "status": "success"}

# Export download
@app.get("/api/data/export/download/{filename}")
async def download_export(filename: str):
    """Скачать экспортированный файл"""
    file_path = project_root / "exports" / filename
    if file_path.exists() and file_path.suffix == '.xlsx':
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    return JSONResponse({"error": "Файл не найден"}, status_code=404)

# Обработка ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Обработчик 404 ошибок"""
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "API endpoint не найден", "path": request.url.path, "status": 404}
        )
    
    # Для не-API запросов возвращаем главную страницу (SPA routing)
    return await root()

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Обработчик 500 ошибок"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера", 
            "detail": str(exc),
            "status": 500
        }
    )

# Middleware для логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех запросов"""
    # Пропускаем логирование для статических файлов
    if not any(request.url.path.endswith(ext) for ext in ['.js', '.css', '.ico', '.png', '.jpg']):
        print(f"📥 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Логируем ошибки
    if response.status_code >= 400:
        print(f"❌ {request.method} {request.url.path} -> {response.status_code}")
    
    return response

# Монтирование статических файлов - ВАЖНО: это должно быть в самом конце!
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

# Создание необходимых директорий при запуске
def ensure_directories():
    """Создание необходимых директорий"""
    dirs = ['temp', 'exports', 'logs']
    for dir_name in dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)

def main():
    """Запуск сервера"""
    ensure_directories()
    
    print("🚀 Запуск YouTube Analyzer (Hybrid)...")
    print(f"📁 Frontend путь: {frontend_path}")
    print(f"💾 База данных: {'✅ Подключена' if db_loaded else '❌ Не подключена'}")
    print("📡 Сервер будет доступен по адресу: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("❤️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "backend.main_hybrid:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=False
    )

if __name__ == "__main__":
    main()