"""
Скрипт для проверки всех компонентов системы
"""
import sys
import os
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

# Тест 1: Python версия
def test_python():
    print_header("Проверка Python")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} - требуется 3.8+")
        return False

# Тест 2: Проверка импортов
def test_imports():
    print_header("Проверка основных библиотек")
    
    required_imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("aiosqlite", "Aiosqlite"),
        ("googleapiclient", "Google API Client"),
        ("celery", "Celery"),
        ("redis", "Redis-py"),
        ("websockets", "WebSockets"),
        ("pandas", "Pandas"),
        ("nltk", "NLTK"),
        ("dotenv", "Python-dotenv"),
        ("eventlet", "Eventlet (для Windows)")
    ]
    
    all_ok = True
    for module, name in required_imports:
        try:
            __import__(module)
            print_success(f"{name}")
        except ImportError as e:
            print_error(f"{name} - {e}")
            all_ok = False
    
    return all_ok

# Тест 3: Проверка Redis
async def test_redis():
    print_header("Проверка Redis подключения")
    
    try:
        import redis.asyncio as redis
        
        # Подключение к Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Тест ping
        pong = await r.ping()
        if pong:
            print_success("Redis отвечает на ping")
        
        # Тест записи/чтения
        await r.set('test_key', 'test_value')
        value = await r.get('test_key')
        if value == 'test_value':
            print_success("Redis запись/чтение работает")
        
        # Очистка
        await r.delete('test_key')
        
        await r.close()
        return True
        
    except Exception as e:
        print_error(f"Не удалось подключиться к Redis: {e}")
        print_info("Убедитесь, что Docker контейнер запущен: docker-compose up -d")
        return False

# Тест 4: Проверка Celery
def test_celery():
    print_header("Проверка Celery конфигурации")
    
    try:
        from celery import Celery
        app = Celery('test')
        app.conf.update(
            broker_url='redis://localhost:6379/0',
            result_backend='redis://localhost:6379/0'
        )
        
        # Проверка подключения к брокеру
        try:
            conn = app.connection()
            conn.ensure_connection(max_retries=1)
            print_success("Celery может подключиться к Redis")
            return True
        except Exception as e:
            print_error(f"Celery не может подключиться к Redis: {e}")
            return False
            
    except Exception as e:
        print_error(f"Ошибка импорта Celery: {e}")
        return False

# Тест 5: Проверка файлов проекта
def test_project_files():
    print_header("Проверка файлов проекта")
    
    required_files = [
        "main.py",
        "models.py",
        "database.py",
        "api.py",
        "websocket.py",
        "youtube_api.py",
        "analyzer.py",
        "tasks.py",
        "index.html",
        "app.js",
        "styles.css",
        ".env",
        "docker-compose.yml"
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file}")
        else:
            print_error(f"{file} - не найден")
            all_ok = False
    
    return all_ok

# Тест 6: Проверка .env файла
def test_env():
    print_header("Проверка конфигурации (.env)")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            "YOUTUBE_API_KEY",
            "DATABASE_PATH",
            "HOST",
            "PORT"
        ]
        
        all_ok = True
        for var in required_vars:
            value = os.getenv(var)
            if value:
                if var == "YOUTUBE_API_KEY":
                    print_success(f"{var} = ***{value[-4:]}")
                else:
                    print_success(f"{var} = {value}")
            else:
                print_error(f"{var} - не установлен")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_error(f"Ошибка загрузки .env: {e}")
        return False

# Тест 7: Проверка базы данных
async def test_database():
    print_header("Проверка базы данных")
    
    try:
        from database import init_db, get_session
        from models import Video
        
        # Инициализация БД
        await init_db()
        print_success("База данных инициализирована")
        
        # Тестовый запрос
        async with get_session() as session:
            from sqlalchemy import select
            stmt = select(Video).limit(1)
            result = await session.execute(stmt)
            video = result.scalar_one_or_none()
            
            if video is None:
                print_info("База данных пуста (это нормально для новой установки)")
            else:
                print_success(f"В базе есть видео: {video.title[:50]}...")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка работы с БД: {e}")
        return False

# Тест 8: Проверка YouTube API
def test_youtube_api():
    print_header("Проверка YouTube API")
    
    try:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            print_error("YOUTUBE_API_KEY не установлен в .env")
            return False
        
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", developerKey=api_key)
        
        # Простой тестовый запрос
        request = youtube.search().list(
            part="snippet",
            q="test",
            maxResults=1
        )
        response = request.execute()
        
        if 'items' in response:
            print_success("YouTube API работает корректно")
            return True
        else:
            print_warning("YouTube API вернул пустой ответ")
            return False
            
    except Exception as e:
        print_error(f"Ошибка YouTube API: {e}")
        print_info("Проверьте правильность API ключа")
        return False

# Основная функция
async def main():
    print(f"{Fore.MAGENTA}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         YouTube Analyzer - Диагностика системы           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    results = []
    
    # Синхронные тесты
    results.append(("Python", test_python()))
    results.append(("Импорты", test_imports()))
    results.append(("Файлы проекта", test_project_files()))
    results.append(("Конфигурация", test_env()))
    results.append(("YouTube API", test_youtube_api()))
    
    # Асинхронные тесты
    results.append(("Redis", await test_redis()))
    results.append(("Celery", test_celery()))
    results.append(("База данных", await test_database()))
    
    # Итоговый отчет
    print_header("ИТОГОВЫЙ ОТЧЕТ")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print(f"{Fore.GREEN}✅ {name:<20} OK{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ {name:<20} FAILED{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Результат: {passed}/{total} тестов пройдено{Style.RESET_ALL}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 Все компоненты готовы к работе!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Запустите приложение командой: python main.py{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Некоторые компоненты требуют настройки{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Исправьте ошибки выше и запустите тест снова{Style.RESET_ALL}")

if __name__ == "__main__":
    # Установка colorama если не установлена
    try:
        import colorama
    except ImportError:
        print("Устанавливаю colorama для цветного вывода...")
        os.system("pip install colorama")
        import colorama
    
    asyncio.run(main())