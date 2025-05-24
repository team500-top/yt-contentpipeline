"""
YouTube Analyzer - Minimal Working Server
"""
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path

# Пути
current_dir = Path(__file__).parent
project_root = current_dir.parent
frontend_path = project_root / "frontend"

# Создание приложения
app = FastAPI(title="YouTube Analyzer - Minimal")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Основная страница
@app.get("/")
async def root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>index.html not found</h1>")

# JavaScript
@app.get("/app.js")
async def get_app_js():
    js_path = frontend_path / "app.js"
    if js_path.exists():
        return FileResponse(str(js_path), media_type="application/javascript")
    return JSONResponse({"error": "app.js not found"}, status_code=404)

# CSS
@app.get("/style.css")
async def get_style_css():
    css_path = frontend_path / "style.css"
    if css_path.exists():
        return FileResponse(str(css_path), media_type="text/css")
    return JSONResponse({"error": "style.css not found"}, status_code=404)

# Все HTML файлы
@app.get("/{filename}.html")
async def get_html_file(filename: str):
    file_path = frontend_path / f"{filename}.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return HTMLResponse(f"<h1>{filename}.html not found</h1>", status_code=404)

# API заглушки
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api")
async def api_info():
    return {"name": "YouTube Analyzer", "version": "minimal"}

@app.get("/api/tasks")
async def get_tasks():
    return []

@app.get("/api/config") 
async def get_config():
    return {"youtube_api_key": "", "max_long_videos_channel": 5}

@app.get("/api/data/videos")
async def get_videos():
    return []

@app.get("/api/data/stats")
async def get_stats():
    return {"total_videos": 0, "total_channels": 0}

# Статические файлы
app.mount("/", StaticFiles(directory=str(frontend_path)), name="static")

if __name__ == "__main__":
    print("YouTube Analyzer - Minimal Server")
    print(f"Frontend: {frontend_path}")
    print("URL: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
