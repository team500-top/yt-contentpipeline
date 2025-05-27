import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Импорт модулей приложения
from database import init_db, close_db
from api import api_router
from websocket import websocket_endpoint, manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание необходимых директорий
os.makedirs("temp", exist_ok=True)
os.makedirs("exports", exist_ok=True)
os.makedirs("logs", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting YouTube Content Analyzer...")
    
    # Инициализация базы данных
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down YouTube Content Analyzer...")
    await close_db()
    logger.info("Database connection closed")

# Создание FastAPI приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    description="Система анализа YouTube контента для создания эффективной контент-стратегии",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутера
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket для real-time обновлений"""
    await websocket_endpoint(websocket)

# Внутренний endpoint для отправки WebSocket сообщений из Celery
@app.post("/api/internal/websocket")
async def internal_websocket(data: dict):
    """Внутренний endpoint для отправки WebSocket уведомлений из Celery задач"""
    try:
        await manager.broadcast(data)
        return {"status": "sent"}
    except Exception as e:
        logger.error(f"Error broadcasting WebSocket message: {e}")
        return {"status": "error", "message": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": "YouTube Content Analyzer",
        "version": "1.0.0",
        "database": "connected",
        "websocket_connections": len(manager.active_connections)
    }

# Монтирование статических папок
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ВАЖНО: Монтирование папки components
if Path("components").exists():
    app.mount("/components", StaticFiles(directory="components"), name="components")

# ВАЖНО: Монтирование папки utils
if Path("utils").exists():
    app.mount("/utils", StaticFiles(directory="utils"), name="utils")

# Основная страница
@app.get("/")
async def read_index():
    """Главная страница приложения"""
    index_path = Path("index.html")
    if index_path.exists():
        return FileResponse("index.html")
    else:
        return JSONResponse(
            status_code=404,
            content={
                "error": "index.html not found",
                "message": "Please ensure index.html is in the root directory"
            }
        )

# Дополнительные статические файлы
@app.get("/app.js")
async def read_app_js():
    """JavaScript приложения"""
    app_js_path = Path("app.js")
    if app_js_path.exists():
        return FileResponse("app.js", media_type="application/javascript")
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "app.js not found"}
        )

@app.get("/styles.css")
async def read_styles():
    """CSS стили"""
    styles_path = Path("styles.css")
    if styles_path.exists():
        return FileResponse("styles.css", media_type="text/css")
    else:
        # Возвращаем пустой CSS если файл не найден
        return Response(content="", media_type="text/css")

@app.get("/help.html")
async def read_help():
    """Страница справки"""
    help_path = Path("help.html")
    if help_path.exists():
        return FileResponse("help.html")
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "help.html not found"}
        )

# Обработка ошибок
@app.exception_handler(404)
async def not_found(request: Request, exc):
    """Обработчик 404 ошибок"""
    # Логирование для отладки
    logger.warning(f"404 Not Found: {request.url.path}")
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "path": str(request.url.path),
            "message": "The requested resource was not found"
        }
    )

@app.exception_handler(500)
async def internal_error(request: Request, exc):
    """Обработчик 500 ошибок"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

# API документация
@app.get("/api")
async def api_info():
    """Информация об API"""
    return {
        "name": "YouTube Content Analyzer API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "videos": "/api/videos",
            "channels": "/api/channels",
            "tasks": "/api/tasks",
            "parse": "/api/parse",
            "analytics": "/api/analytics/stats",
            "settings": "/api/settings",
            "export": "/api/videos/export",
            "help": "/api/help/content"
        }
    }

# Запуск сервера
if __name__ == "__main__":
    # Получение настроек из переменных окружения
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"API documentation available at: http://{host}:{port}/docs")
    
    # Проверка наличия важных файлов
    required_files = ["index.html", "app.js"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            logger.warning(f"Warning: {file} not found in root directory")
    
    # Проверка наличия компонентов
    if not Path("components").exists():
        logger.warning("Warning: components directory not found")
    else:
        component_files = list(Path("components").glob("*.js"))
        logger.info(f"Found {len(component_files)} component files")
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
    
    # Конфигурация Uvicorn
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        reload_dirs=[".", "api", "models", "tasks", "components", "utils"] if debug else None,
        log_level="info",
        access_log=True
    )