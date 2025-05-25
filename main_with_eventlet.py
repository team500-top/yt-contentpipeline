import eventlet
eventlet.monkey_patch()

import asyncio
import signal
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from dotenv import load_dotenv
import os

# Импорт модулей проекта
from database import init_db, close_db
from api import api_router
from websocket import websocket_endpoint
from tasks import celery_app, start_celery_worker

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Создание необходимых директорий
Path("temp").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

# Глобальная переменная для graceful shutdown
shutdown_event = asyncio.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("🚀 Запуск YouTube Analyzer...")
    
    # Инициализация базы данных
    await init_db()
    print("✅ База данных инициализирована")
    
    # Запуск Celery worker в отдельном процессе
    if sys.platform == "win32":
        # Для Windows используем threading вместо multiprocessing
        import threading
        # celery_thread = threading.Thread(target=start_celery_worker, daemon=True)
        # celery_thread.start()
        print("✅ Celery worker должен быть запущен отдельно")
    
    yield
    
    # Очистка при выключении
    print("\n🛑 Остановка YouTube Analyzer...")
    await close_db()
    shutdown_event.set()
    print("✅ Приложение остановлено")

# Создание FastAPI приложения
app = FastAPI(
    title="YouTube Content Analyzer",
    description="Система анализа YouTube контента для построения контент-стратегии",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение API роутеров
app.include_router(api_router, prefix="/api")

# WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)

# Статические файлы (CSS, JS)
@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css", media_type="text/css")

@app.get("/app.js")
async def get_app():
    return FileResponse("app.js", media_type="application/javascript")

# Главная страница
@app.get("/")
async def get_index():
    return FileResponse("index.html", media_type="text/html")

# Обработчик сигналов для graceful shutdown
def signal_handler(sig, frame):
    """Обработка Ctrl+C и завершения процесса"""
    print("\n⚠️ Получен сигнал завершения. Сохранение состояния...")
    # Здесь можно добавить сохранение состояния задач
    asyncio.create_task(shutdown_application())

async def shutdown_application():
    """Корректное завершение приложения"""
    shutdown_event.set()
    # Даем время на завершение активных задач
    await asyncio.sleep(2)
    sys.exit(0)

# Регистрация обработчиков сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     YouTube Content Analyzer v1.0     ║
    ║  Система анализа контент-стратегии    ║
    ╚═══════════════════════════════════════╝
    """)
    
    # Конфигурация uvicorn
    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning",
        access_log=DEBUG,
        use_colors=True
    )
    
    # Запуск сервера
    server = uvicorn.Server(config)
    
    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("\n👋 До встречи!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)