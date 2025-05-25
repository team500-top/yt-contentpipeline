import asyncio
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Создание необходимых директорий
Path("temp").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("🚀 Запуск YouTube Analyzer (упрощенная версия)...")
    
    # Пропускаем инициализацию БД для теста
    print("⚠️  Инициализация БД пропущена для отладки")
    
    yield
    
    print("\n🛑 Остановка YouTube Analyzer...")

# Создание FastAPI приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    description="Система анализа YouTube контента для построения контент-стратегии",
    version="1.0.0",
    lifespan=lifespan
)

# Импортируем API роутер
try:
    from api import api_router
    app.include_router(api_router, prefix="/api")
    print("✅ API роутер подключен")
except Exception as e:
    print(f"❌ Ошибка подключения API: {e}")

# Статические файлы (CSS, JS)
@app.get("/styles.css")
async def get_styles():
    if os.path.exists("styles.css"):
        return FileResponse("styles.css", media_type="text/css")
    return {"error": "styles.css not found"}

@app.get("/app.js")
async def get_app():
    if os.path.exists("app.js"):
        return FileResponse("app.js", media_type="application/javascript")
    return {"error": "app.js not found"}

# Главная страница
@app.get("/")
async def get_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html", media_type="text/html")
    return {"error": "index.html not found", "status": "Please check if all files are in place"}

# Тестовый endpoint
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "message": "YouTube Analyzer is running (simplified mode)"
    }

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║  YouTube Analyzer v1.0 (Simple Mode)  ║
    ║  Система анализа контент-стратегии    ║
    ╚═══════════════════════════════════════╝
    """)
    
    print(f"Запуск на http://{HOST}:{PORT}")
    print("Для проверки откройте http://127.0.0.1:8000/health")
    
    # Запуск сервера
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )