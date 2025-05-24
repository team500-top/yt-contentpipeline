"""
Проверка структуры файлов проекта
"""
from pathlib import Path

# Проверяем все необходимые файлы
files_to_check = [
    "frontend/index.html",
    "frontend/app.js",
    "frontend/style.css",
    "backend/main.py",
    "backend/services.py",
    "backend/models.py",
    "backend/database.py",
    "shared/config.py",
    "shared/utils.py",
    "shared/youtube_parser.py",
]

print("=== Проверка файлов YouTube Analyzer ===\n")

for file_path in files_to_check:
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        print(f"✅ {file_path} ({size:,} bytes)")
    else:
        print(f"❌ {file_path} - НЕ НАЙДЕН!")

# Проверка содержимого frontend файлов
print("\n=== Проверка frontend файлов ===")

# index.html
index_path = Path("frontend/index.html")
if index_path.exists():
    content = index_path.read_text(encoding='utf-8')
    if '<script src="app.js"></script>' in content:
        print("✅ index.html содержит подключение app.js")
    else:
        print("❌ index.html НЕ содержит подключение app.js")
    
    if 'lucide' in content:
        print("✅ index.html содержит Lucide icons")
    else:
        print("❌ index.html НЕ содержит Lucide icons")

# app.js
app_js_path = Path("frontend/app.js")
if app_js_path.exists():
    content = app_js_path.read_text(encoding='utf-8')
    if 'class ApiClient' in content:
        print("✅ app.js содержит ApiClient")
    else:
        print("❌ app.js НЕ содержит ApiClient")
    
    if 'document.addEventListener' in content:
        print("✅ app.js содержит инициализацию")
    else:
        print("❌ app.js НЕ содержит инициализацию")

print("\n=== Проверка завершена ===")
input("Нажмите Enter...")