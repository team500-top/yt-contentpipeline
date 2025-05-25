import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# Создание необходимых директорий
Path("temp").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

# Создание FastAPI приложения БЕЗ lifespan для избежания зависания
app = FastAPI(
    title="YouTube Content Analyzer",
    version="1.0.0"
)

# Инициализация БД при старте (синхронно)
print("🚀 Запуск YouTube Analyzer...")
try:
    import sqlite3
    conn = sqlite3.connect('youtube_data.db')
    conn.close()
    print("✅ База данных доступна")
except Exception as e:
    print(f"⚠️  БД недоступна: {e}")

# API endpoints
try:
    from api import api_router
    app.include_router(api_router, prefix="/api")
    print("✅ API подключен")
except Exception as e:
    print(f"⚠️  Ошибка подключения API: {e}")
    
    # Базовые endpoints для работы интерфейса
    @app.get("/api/videos")
    async def get_videos():
        return {
            "videos": [],
            "pagination": {"total": 0, "page": 1, "per_page": 50, "pages": 0}
        }
    
    @app.get("/api/tasks")
    async def get_tasks():
        return []
    
    @app.get("/api/analytics/stats")
    async def get_stats():
        return {
            "stats": {
                "totalVideos": 0,
                "totalChannels": 0,
                "avgEngagement": 0,
                "topCategory": "Не определено",
                "videosThisWeek": 0
            },
            "topVideos": []
        }
    
    @app.get("/api/search-queries")
    async def get_search_queries():
        return []
    
    @app.get("/api/settings")
    async def get_settings():
        return {
            "youtubeApiKey": os.getenv("YOUTUBE_API_KEY", ""),
            "autoRetry": True,
            "requestDelay": 3
        }
    
    @app.post("/api/settings")
    async def save_settings(settings: dict):
        return {"status": "saved"}
    
    @app.post("/api/parse")
    async def start_parsing(request_data: dict):
        import time
        import random
        task_id = f"task_{int(time.time() * 1000)}"
        return {
            "id": random.randint(1, 1000),
            "task_id": task_id,
            "task_type": "search",
            "parameters": request_data,
            "status": "pending",
            "progress": 0,
            "total_items": 0,
            "processed_items": 0,
            "created_at": "2025-05-25T12:00:00"
        }

# WebSocket (опционально)
try:
    from websocket import websocket_endpoint
    app.add_api_websocket_route("/ws", websocket_endpoint)
except:
    # Заглушка для WebSocket
    from fastapi import WebSocket
    
    @app.websocket("/ws")
    async def websocket_mock(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_json({"type": "pong", "timestamp": "2025-05-25T12:00:00"})
        except:
            pass

# Статические файлы
@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html", media_type="text/html")
    return HTMLResponse("<h1>index.html not found</h1>")

@app.get("/app.js")
async def read_app_js():
    if os.path.exists("app.js"):
        return FileResponse("app.js", media_type="application/javascript")
    return HTMLResponse("console.error('app.js not found');", media_type="application/javascript")

@app.get("/styles.css")
async def read_styles():
    if os.path.exists("styles.css"):
        return FileResponse("styles.css", media_type="text/css")
    return HTMLResponse("/* styles.css not found */", media_type="text/css")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "YouTube Analyzer is running"}

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     YouTube Content Analyzer v1.0     ║
    ║  Система анализа контент-стратегии    ║
    ╚═══════════════════════════════════════╝
    """)
    
    print(f"\n📍 Запуск на http://{HOST}:{PORT}")
    print("📁 Директория: {0}".format(os.getcwd()))
    print("\n✅ Приложение готово к работе!")
    print("Для остановки нажмите Ctrl+C\n")
    
    # Запуск
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")