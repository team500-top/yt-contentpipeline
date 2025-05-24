"""
YouTube Analyzer - Main FastAPI Server
Объединенный сервер для локального запуска
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
# Добавим импорт
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path

# Добавить пути для импорта
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Импорт сервисов
from services import (
    tasks_router,
    youtube_router, 
    analysis_router,
    data_router,
    config_router
)


# Добавьте эти строки в начало backend/main.py после импортов

import mimetypes

# Инициализация MIME типов
mimetypes.init()
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Замените функции get_app_js и get_style_css на эти:

@app.get("/app.js")
async def get_app_js():
    """JavaScript файл с правильным MIME типом"""
    js_path = frontend_path / "app.js"
    if js_path.exists():
        return FileResponse(
            path=str(js_path),
            media_type="application/javascript",
            headers={
                "Content-Type": "application/javascript; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return HTMLResponse("console.error('app.js not found');", media_type="application/javascript")

@app.get("/style.css") 
async def get_style_css():
    """CSS файл с правильным MIME типом"""
    css_path = frontend_path / "style.css"
    if css_path.exists():
        return FileResponse(
            path=str(css_path),
            media_type="text/css",
            headers={
                "Content-Type": "text/css; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return HTMLResponse("/* style.css not found */", media_type="text/css")

# Также добавьте монтирование статических файлов после роутеров:
app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")



# Создание приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    description="Анализ YouTube контента и трендов",
    version="2.0.0"
)

# CORS middleware - разрешаем все источники для локальной разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров API
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(youtube_router, prefix="/api/youtube", tags=["YouTube"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(data_router, prefix="/api/data", tags=["Data"])
app.include_router(config_router, prefix="/api/config", tags=["Config"])

# Пути к файлам
frontend_path = project_root / "frontend"

# Основные роуты
@app.get("/")
async def root():
    """Главная страница"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
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
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="application/javascript")
    return HTMLResponse("console.error('app.js not found');", media_type="application/javascript")

@app.get("/style.css")
async def get_style_css():
    """CSS файл"""
    css_path = frontend_path / "style.css"
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="text/css")
    return HTMLResponse("/* style.css not found */", media_type="text/css")

# Дополнительные статические файлы
@app.get("/frontend/{file_path:path}")
async def get_frontend_file(file_path: str):
    """Обработка запросов к frontend файлам"""
    file_full_path = frontend_path / file_path
    if file_full_path.exists() and file_full_path.is_file():
        return FileResponse(str(file_full_path))
    return {"error": f"File {file_path} not found"}

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
    return {"error": "Файл не найден"}
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "YouTube Analyzer работает"
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

# Тестовая страница
@app.get("/test.html")
async def test_page():
    """Тестовая страница для проверки API"""
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>YouTube Analyzer - API Test</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .test { margin: 10px 0; padding: 15px; border-radius: 4px; border: 1px solid #ddd; }
        .success { background: #d4edda; border-color: #c3e6cb; }
        .error { background: #f8d7da; border-color: #f5c6cb; }
        .loading { background: #cfe2ff; border-color: #b6d4fe; }
        pre { margin: 5px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; overflow-x: auto; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 YouTube Analyzer API Test</h1>
        <p>Проверка работоспособности всех API endpoints</p>
        <hr>
        <div id="results"></div>
    </div>
    
    <script>
        const tests = [
            { name: '🏥 Health Check', url: '/health', method: 'GET' },
            { name: '📡 API Info', url: '/api', method: 'GET' },
            { name: '📋 Tasks List', url: '/api/tasks', method: 'GET' },
            { name: '⚙️ Configuration', url: '/api/config', method: 'GET' },
            { name: '🎬 Videos', url: '/api/data/videos?limit=10', method: 'GET' },
            { name: '📺 Channels', url: '/api/data/channels', method: 'GET' },
            { name: '📊 Statistics', url: '/api/data/stats', method: 'GET' },
            { name: '🎯 Active Tasks', url: '/api/tasks/active', method: 'GET' }
        ];
        
        const results = document.getElementById('results');
        
        async function testAPI() {
            results.innerHTML = '<div class="test loading">⏳ Начинаем тестирование...</div>';
            await new Promise(resolve => setTimeout(resolve, 500));
            results.innerHTML = '';
            
            for (const test of tests) {
                const div = document.createElement('div');
                div.className = 'test loading';
                div.innerHTML = `⏳ ${test.name}: Проверка...`;
                results.appendChild(div);
                
                try {
                    const startTime = Date.now();
                    const response = await fetch(test.url, { method: test.method });
                    const duration = Date.now() - startTime;
                    const data = await response.json();
                    
                    if (response.ok) {
                        div.className = 'test success';
                        div.innerHTML = `
                            ✅ <strong>${test.name}</strong>: OK (${response.status}) - ${duration}ms
                            <br><small>${test.url}</small>
                            <pre>${JSON.stringify(data, null, 2).substring(0, 200)}${JSON.stringify(data).length > 200 ? '...' : ''}</pre>
                        `;
                    } else {
                        div.className = 'test error';
                        div.innerHTML = `
                            ❌ <strong>${test.name}</strong>: Error ${response.status} - ${duration}ms
                            <br><small>${test.url}</small>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        `;
                    }
                } catch (error) {
                    div.className = 'test error';
                    div.innerHTML = `
                        ❌ <strong>${test.name}</strong>: Network Error
                        <br><small>${test.url}</small>
                        <pre>${error.message}</pre>
                    `;
                }
                
                // Небольшая задержка между тестами
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            // Итоговая статистика
            const successCount = document.querySelectorAll('.test.success').length;
            const errorCount = document.querySelectorAll('.test.error').length;
            const total = successCount + errorCount;
            
            const summary = document.createElement('div');
            summary.className = 'test ' + (errorCount === 0 ? 'success' : 'error');
            summary.innerHTML = `
                <strong>📊 Итого:</strong> ${successCount}/${total} тестов пройдено успешно
                ${errorCount > 0 ? '<br>⚠️ Есть ошибки, проверьте логи сервера' : '<br>✅ Все системы работают нормально'}
            `;
            results.appendChild(summary);
        }
        
        // Запуск тестов при загрузке страницы
        testAPI();
        
        // Кнопка для повторного тестирования
        const retestBtn = document.createElement('button');
        retestBtn.textContent = '🔄 Повторить тест';
        retestBtn.style.cssText = 'margin-top: 20px; padding: 10px 20px; font-size: 16px; cursor: pointer;';
        retestBtn.onclick = testAPI;
        document.querySelector('.container').appendChild(retestBtn);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# Обработка ошибок
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Обработчик 404 ошибок"""
    if request.url.path.startswith("/api/"):
        return {"error": "API endpoint не найден", "path": request.url.path, "status": 404}
    
    # Для не-API запросов возвращаем главную страницу (SPA routing)
    return await root()

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Обработчик 500 ошибок"""
    return {
        "error": "Внутренняя ошибка сервера", 
        "detail": str(exc),
        "status": 500
    }

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
    
    print("🚀 Запуск YouTube Analyzer...")
    print("📡 Сервер будет доступен по адресу: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")
    print("🧪 Тестовая страница: http://localhost:8000/test.html")
    print("❤️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=False  # Отключаем access log, используем наш middleware
    )

if __name__ == "__main__":
    main()