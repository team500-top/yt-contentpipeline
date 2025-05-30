"""
Скрипт для диагностики и исправления проблем с импортами
Сохраните как fix_imports.py и запустите
"""
import sys
import os
from pathlib import Path

print("🔍 Диагностика YouTube Analyzer...")
print(f"Python версия: {sys.version}")
print(f"Текущая директория: {os.getcwd()}")

# Проверка структуры
required_files = [
    "backend/main.py",
    "backend/services.py", 
    "backend/models.py",
    "backend/database.py",
    "shared/config.py",
    "shared/utils.py",
    "shared/youtube_parser.py"
]

missing = []
for file in required_files:
    if Path(file).exists():
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - НЕ НАЙДЕН!")
        missing.append(file)

if missing:
    print("\n❌ Отсутствуют необходимые файлы!")
    exit(1)

print("\n📦 Проверка импортов...")

# Добавляем пути
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "backend"))
sys.path.insert(0, str(current_dir / "shared"))

# Пробуем импортировать модули
try:
    print("Импорт models...", end=" ")
    from backend import models
    print("✅")
except Exception as e:
    print(f"❌\n  Ошибка: {e}")
    
try:
    print("Импорт database...", end=" ")
    from backend import database
    print("✅")
except Exception as e:
    print(f"❌\n  Ошибка: {e}")

try:
    print("Импорт config...", end=" ")
    from shared import config
    print("✅")
except Exception as e:
    print(f"❌\n  Ошибка: {e}")

try:
    print("Импорт utils...", end=" ")
    from shared import utils
    print("✅")
except Exception as e:
    print(f"❌\n  Ошибка: {e}")

try:
    print("Импорт youtube_parser...", end=" ")
    from shared import youtube_parser
    print("✅")
except Exception as e:
    print(f"❌\n  Ошибка: {e}")

try:
    print("Импорт services...", end=" ")
    from backend import services
    print("✅")
except Exception as e:
    print(f"❌\n  Ошибка: {e}")

print("\n🚀 Пробуем запустить сервер...")

# Создаем простой тестовый запуск
test_server = '''
import sys
from pathlib import Path

# Добавляем пути
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

# Теперь импортируем
try:
    from main import app
    import uvicorn
    
    print("✅ Импорты успешны, запускаем сервер...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
'''

# Сохраняем тестовый запускатор
with open("backend/test_run.py", "w", encoding="utf-8") as f:
    f.write(test_server)

print("\n✅ Создан backend/test_run.py")
print("\nТеперь попробуйте:")
print("1. cd C:\\youtube-analyzer")
print("2. python backend/test_run.py")

# Проверяем установленные пакеты
print("\n📋 Проверка установленных пакетов...")
import subprocess

required_packages = [
    "fastapi",
    "uvicorn", 
    "pydantic",
    "pandas",
    "openpyxl"
]

for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} - НЕ УСТАНОВЛЕН!")
        print(f"   Установите: pip install {package}")

print("\n" + "="*50)
input("Нажмите Enter для завершения...")