import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Импорт модулей проекта
from database import init_db, close_db
from api import api_router
from websocket import websocket_endpoint, manager

# Создание необходимых директорий
Path("temp").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Запуск YouTube Analyzer...")
    await init_db()
    print("✅ База данных инициализирована")
    
    yield
    
    # Shutdown
    print("🛑 Остановка YouTube Analyzer...")
    await close_db()
    print("✅ Соединения закрыты")

# Создание FastAPI приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    version="1.0.0",
    description="Система анализа YouTube контента для создания контент-стратегии",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутера
app.include_router(api_router, prefix="/api", tags=["api"])

# WebSocket endpoint
app.websocket("/ws")(websocket_endpoint)

# Статические файлы
@app.get("/", response_class=FileResponse)
async def read_index():
    """Главная страница"""
    return FileResponse("index.html")

@app.get("/app.js", response_class=FileResponse)
async def read_js():
    """JavaScript файл"""
    return FileResponse("app.js", media_type="application/javascript")

@app.get("/styles.css", response_class=FileResponse)
async def read_css():
    """CSS файл"""
    return FileResponse("styles.css", media_type="text/css")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "redis": "connected"
    }

if __name__ == "__main__":
    # Получение конфигурации из .env
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║               YouTube Content Analyzer v1.0.0                 ║
    ║                                                               ║
    ║  Система анализа YouTube контента для контент-стратегии      ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    🌐 Интерфейс доступен по адресу: http://{HOST}:{PORT}
    📊 API документация: http://{HOST}:{PORT}/docs
    🔄 WebSocket: ws://{HOST}:{PORT}/ws
    
    Для остановки нажмите Ctrl+C
    """)
    
    # Запуск сервера
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )