"""
Скрипт для автоматического исправления проблем с YouTube Analyzer
"""
import os
import shutil
from pathlib import Path

print("🔧 Исправление YouTube Analyzer...")

# 1. Исправляем main.py
main_path = Path("backend/main.py")
if main_path.exists():
    print("📝 Исправляем main.py...")
    
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем обработчики ошибок
    if "'dict' object is not callable" in content or "@app.exception_handler(404)" in content:
        # Добавляем импорт JSONResponse если его нет
        if "from fastapi.responses import JSONResponse" not in content:
            content = content.replace(
                "from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse",
                "from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse"
            )
        
        # Исправляем обработчик 404
        old_404 = """@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    \"\"\"Обработчик 404 ошибок\"\"\"
    if request.url.path.startswith("/api/"):
        return {"error": "API endpoint не найден", "path": request.url.path, "status": 404}
    
    # Для не-API запросов возвращаем главную страницу (SPA routing)
    return await root()"""
        
        new_404 = """@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    \"\"\"Обработчик 404 ошибок\"\"\"
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "API endpoint не найден", "path": request.url.path, "status": 404}
        )
    
    # Для не-API запросов возвращаем главную страницу (SPA routing)
    return await root()"""
        
        content = content.replace(old_404, new_404)
        
        # Исправляем обработчик 500
        old_500 = """@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    \"\"\"Обработчик 500 ошибок\"\"\"
    return {
        "error": "Внутренняя ошибка сервера", 
        "detail": str(exc),
        "status": 500
    }"""
        
        new_500 = """@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    \"\"\"Обработчик 500 ошибок\"\"\"
    return JSONResponse(
        status_code=500,
        content={
            "error": "Внутренняя ошибка сервера", 
            "detail": str(exc),
            "status": 500
        }
    )"""
        
        content = content.replace(old_500, new_500)
        
        # Сохраняем исправленный файл
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ main.py исправлен")

# 2. Создаем тестовую страницу для исправления
fix_html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Fix Frontend</title>
</head>
<body>
    <h1>Исправление Frontend</h1>
    <div id="status">Загрузка...</div>
    
    <script>
        // Принудительная загрузка и инициализация
        fetch('/app.js')
            .then(r => r.text())
            .then(code => {
                eval(code);
                
                if (typeof ApiClient !== 'undefined') {
                    window.apiClient = new ApiClient();
                    document.getElementById('status').innerHTML = '✅ Frontend исправлен! <br><a href="/">Перейти на главную</a>';
                    
                    // Сохраняем в localStorage для автоматической загрузки
                    localStorage.setItem('forceInit', 'true');
                } else {
                    document.getElementById('status').innerHTML = '❌ Не удалось исправить';
                }
            })
            .catch(e => {
                document.getElementById('status').innerHTML = '❌ Ошибка: ' + e;
            });
    </script>
</body>
</html>"""

with open("frontend/fix.html", "w", encoding="utf-8") as f:
    f.write(fix_html)
    print("✅ Создан frontend/fix.html")

# 3. Добавляем автоинициализацию в index.html
index_path = Path("frontend/index.html")
if index_path.exists():
    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    if "forceInit" not in index_content:
        # Добавляем скрипт перед </body>
        init_script = """
    <!-- Автоматическая инициализация если обычная не работает -->
    <script>
        if (localStorage.getItem('forceInit') === 'true') {
            console.log('Применяем принудительную инициализацию...');
            
            setTimeout(() => {
                if (typeof ApiClient === 'undefined') {
                    fetch('/app.js')
                        .then(r => r.text())
                        .then(code => {
                            eval(code);
                            if (typeof ApiClient !== 'undefined') {
                                window.apiClient = new ApiClient();
                                console.log('✅ Frontend инициализирован принудительно');
                            }
                        });
                }
            }, 1000);
        }
    </script>
"""
        index_content = index_content.replace("</body>", init_script + "\n</body>")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print("✅ Добавлена автоинициализация в index.html")

print("\n🎉 Исправления применены!")
print("\nТеперь:")
print("1. Перезапустите сервер (закройте консоль и запустите run.bat)")
print("2. Откройте http://localhost:8000/fix.html")
print("3. После успешного исправления перейдите на главную страницу")

input("\nНажмите Enter для завершения...")