"""
Проверка services.py на наличие проблем
"""
import ast
import sys
from pathlib import Path

print("🔍 Диагностика services.py...")

# Добавляем пути
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "backend"))

# 1. Проверка синтаксиса
print("\n1️⃣ Проверка синтаксиса Python...")
try:
    with open('backend/services.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    ast.parse(content)
    print("✅ Синтаксис корректен!")
except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка:")
    print(f"   Строка {e.lineno}: {e.msg}")
    print(f"   Текст: {e.text}")
    print(f"   Позиция: {' ' * (e.offset-1)}^")

# 2. Проверка импортов
print("\n2️⃣ Проверка импортов...")
try:
    # Проверяем базовые импорты
    import json
    import asyncio
    import uuid
    from datetime import datetime, timedelta
    print("✅ Базовые модули Python доступны")
    
    # Проверяем FastAPI
    try:
        from fastapi import APIRouter, HTTPException
        print("✅ FastAPI установлен")
    except ImportError:
        print("❌ FastAPI не установлен!")
        print("   Выполните: pip install fastapi")
    
    # Проверяем локальные модули
    try:
        from models import *
        print("✅ models.py доступен")
    except ImportError as e:
        print(f"❌ Ошибка импорта models.py: {e}")
    
    try:
        from database import DatabaseManager
        print("✅ database.py доступен")
    except ImportError as e:
        print(f"❌ Ошибка импорта database.py: {e}")
    
    try:
        from shared.config import settings
        print("✅ shared/config.py доступен")
    except ImportError as e:
        print(f"❌ Ошибка импорта shared/config.py: {e}")
    
    try:
        from shared.utils import Utils
        print("✅ shared/utils.py доступен")
    except ImportError as e:
        print(f"❌ Ошибка импорта shared/utils.py: {e}")
    
    try:
        from shared.youtube_parser import YouTubeParser
        print("✅ shared/youtube_parser.py доступен")
    except ImportError as e:
        print(f"❌ Ошибка импорта shared/youtube_parser.py: {e}")

except Exception as e:
    print(f"❌ Общая ошибка импортов: {e}")

# 3. Попытка импорта services
print("\n3️⃣ Попытка импорта services.py...")
try:
    import services
    print("✅ services.py успешно импортирован!")
    
    # Проверяем наличие роутеров
    routers = ['tasks_router', 'youtube_router', 'analysis_router', 'data_router', 'config_router']
    for router in routers:
        if hasattr(services, router):
            print(f"✅ {router} найден")
        else:
            print(f"❌ {router} не найден")
            
except Exception as e:
    print(f"❌ Ошибка импорта services.py:")
    print(f"   {type(e).__name__}: {e}")
    
    # Детальная диагностика
    import traceback
    print("\n📋 Полный traceback:")
    traceback.print_exc()

# 4. Рекомендации
print("\n💡 Рекомендации:")
print("1. Если есть синтаксические ошибки - запустите fix_services_complete.py")
print("2. Если не хватает модулей - установите зависимости: pip install -r requirements.txt")
print("3. Если все проверки пройдены - запустите: python backend/main.py")
print("4. В крайнем случае используйте: python backend/complete_server.py")

input("\nНажмите Enter для завершения...")