# БЕЗ eventlet!
import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
import uvicorn
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# Создание директорий
Path("temp").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

# FastAPI приложение
app = FastAPI(title="YouTube Content Analyzer", version="1.0.0")

# Главная страница - прямое чтение файла
@app.get("/", response_class=HTMLResponse)
def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"<h1>Error loading index.html</h1><p>{str(e)}</p>"

# JavaScript
@app.get("/app.js", response_class=PlainTextResponse)
def read_js():
    try:
        with open("app.js", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "console.error('app.js not found');"

# CSS
@app.get("/styles.css", response_class=PlainTextResponse)
def read_css():
    try:
        with open("styles.css", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "/* styles.css not found */"

# API заглушки для работы интерфейса
@app.get("/api/videos")
def get_videos():
    return {"videos": [], "pagination": {"total": 0, "page": 1, "per_page": 50, "pages": 0}}

@app.get("/api/tasks")
def get_tasks():
    return []

@app.get("/api/analytics/stats")
def get_stats():
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
def get_search_queries():
    return []

@app.get("/api/settings")
def get_settings():
    return {
        "youtubeApiKey": os.getenv("YOUTUBE_API_KEY", ""),
        "autoRetry": True,
        "requestDelay": 3
    }

@app.post("/api/settings")
def save_settings(settings: dict):
    return {"status": "saved"}

@app.post("/api/parse")
def start_parsing(request_data: dict):
    return {
        "id": 1,
        "task_id": "test_task",
        "task_type": "search",
        "parameters": request_data,
        "status": "pending",
        "progress": 0,
        "total_items": 0,
        "processed_items": 0,
        "created_at": "2025-05-25T12:00:00"
    }

# Health check
@app.get("/health")
def health():
    return {"status": "ok", "files": {
        "index.html": os.path.exists("index.html"),
        "app.js": os.path.exists("app.js"),
        "styles.css": os.path.exists("styles.css")
    }}

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║  YouTube Analyzer (No Eventlet Mode)  ║
    ╚═══════════════════════════════════════╝
    """)
    print(f"\n✅ Запуск на http://{HOST}:{PORT}")
    print("✅ Без eventlet - должно работать!\n")
    
    uvicorn.run(app, host=HOST, port=PORT)