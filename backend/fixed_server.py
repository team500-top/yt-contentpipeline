"""
YouTube Analyzer - Fixed Server
Исправленная версия с правильной обработкой статических файлов
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path
import json

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

# Импорт сервисов
try:
    from services import (
        tasks_router,
        youtube_router, 
        analysis_router,
        data_router,
        config_router
    )
    
    # Подключение роутеров API
    app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(youtube_router, prefix="/api/youtube", tags=["YouTube"])
    app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
    app.include_router(data_router, prefix="/api/data", tags=["Data"])
    app.include_router(config_router, prefix="/api/config", tags=["Config"])
    
    services_loaded = True
    print("✅ Все сервисы подключены")
except Exception as e:
    print(f"⚠️  Ошибка загрузки сервисов: {e}")
    services_loaded = False

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
    return JSONResponse({"error": "app.js not found"}, status_code=404)

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
    return JSONResponse({"error": "style.css not found"}, status_code=404)

# Обработчик для всех HTML файлов
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
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0",
        "message": "YouTube Analyzer работает",
        "services_loaded": services_loaded
    })

# API info
@app.get("/api")
async def api_info():
    """Информация об API"""
    return JSONResponse({
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
        "redoc": "/redoc",
        "services_loaded": services_loaded
    })

# Export endpoint
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
            content={"error": "API endpoint не найден", "path": request.url.path}
        )
    
    # Для статических файлов
    if request.url.path.endswith(('.js', '.css', '.png', '.jpg', '.ico')):
        return JSONResponse(
            status_code=404,
            content={"error": "Файл не найден", "path": request.url.path}
        )
    
    # Для остальных запросов возвращаем главную страницу
    return await root()

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

# Монтирование статических файлов - В САМОМ КОНЦЕ!
# Это будет обрабатывать все остальные файлы (изображения и т.д.)
app.mount("/", StaticFiles(directory=str(frontend_path), html=False), name="static")

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
    
    print("🚀 Запуск YouTube Analyzer (Fixed)...")
    print(f"📁 Frontend путь: {frontend_path}")
    print(f"✅ Сервисы загружены: {services_loaded}")
    print("📡 Сервер будет доступен по адресу: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("❤️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=False
    )

if __name__ == "__main__":
    main()