import asyncio
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv

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
    print("🚀 Запуск YouTube Analyzer...")
    
    # Проверка файлов
    required_files = ["index.html", "app.js", "styles.css"]
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Найден файл: {file}")
        else:
            print(f"❌ Не найден файл: {file}")
    
    # Инициализация базы данных
    try:
        from database import init_db
        await init_db()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"⚠️  БД недоступна: {e}")
    
    yield
    
    print("\n🛑 Остановка YouTube Analyzer...")

# Создание FastAPI приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    version="1.0.0",
    lifespan=lifespan
)

# API endpoints
try:
    from api import api_router
    app.include_router(api_router, prefix="/api")
    print("✅ API подключен")
except Exception as e:
    print(f"⚠️  API недоступен: {e}")
    
    # Минимальный API для тестирования
    @app.get("/api/test")
    async def api_test():
        return {"status": "ok", "message": "API is working"}
    
    @app.get("/api/videos")
    async def get_videos():
        return {"videos": [], "pagination": {"total": 0, "page": 1, "per_page": 50, "pages": 0}}

# Обработка статических файлов вручную
@app.get("/")
async def read_index():
    """Главная страница"""
    file_path = "index.html"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="""
        <html>
        <body>
            <h1>YouTube Analyzer</h1>
            <p>index.html not found!</p>
            <p>Files in directory:</p>
            <ul>
                %s
            </ul>
        </body>
        </html>
        """ % "".join([f"<li>{f}</li>" for f in os.listdir(".")]))

@app.get("/app.js")
async def read_app_js():
    """JavaScript файл"""
    file_path = "app.js"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    else:
        return HTMLResponse(content="console.error('app.js not found');", media_type="application/javascript")

@app.get("/styles.css")
async def read_styles():
    """CSS файл"""
    file_path = "styles.css"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/css")
    else:
        return HTMLResponse(content="/* styles.css not found */", media_type="text/css")

# Health check
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "YouTube Analyzer is running",
        "files": {
            "index.html": os.path.exists("index.html"),
            "app.js": os.path.exists("app.js"),
            "styles.css": os.path.exists("styles.css")
        }
    }

# WebSocket (если доступен)
try:
    from websocket import websocket_endpoint
    app.add_api_websocket_route("/ws", websocket_endpoint)
except:
    pass

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     YouTube Content Analyzer v1.0     ║
    ║  Система анализа контент-стратегии    ║
    ╚═══════════════════════════════════════╝
    """)
    
    print(f"\n📍 Сервер запускается на http://{HOST}:{PORT}")
    print("📁 Рабочая директория:", os.getcwd())
    print("\nДля остановки нажмите Ctrl+C\n")
    
    # Запуск сервера
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )