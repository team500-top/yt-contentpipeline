"""
Патч для исправления JSON ошибки в services.py
"""
import re

print("🔧 Исправление JSON ошибки в services.py...")

# Читаем файл
try:
    with open('backend/services.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправление 1: process_task_with_checkpoints
    old_code1 = """processed_items = set(json.loads(current_task.get('items_processed', '[]')))
        failed_items = set(json.loads(current_task.get('items_failed', '[]')))"""
    
    new_code1 = """items_processed_data = current_task.get('items_processed', '[]')
        items_failed_data = current_task.get('items_failed', '[]')
        
        # Проверяем тип данных перед парсингом
        if isinstance(items_processed_data, str):
            processed_items = set(json.loads(items_processed_data))
        elif isinstance(items_processed_data, list):
            processed_items = set(items_processed_data)
        else:
            processed_items = set()
        
        if isinstance(items_failed_data, str):
            failed_items = set(json.loads(items_failed_data))
        elif isinstance(items_failed_data, list):
            failed_items = set(items_failed_data)
        else:
            failed_items = set()"""
    
    # Применяем исправление
    if old_code1 in content:
        content = content.replace(old_code1, new_code1)
        print("✅ Исправлена функция process_task_with_checkpoints")
    else:
        # Попробуем другой вариант поиска
        pattern = r'processed_items = set\(json\.loads\(current_task\.get\(\'items_processed\', \'\[\]\'\)\)\)'
        if re.search(pattern, content):
            content = re.sub(
                r'processed_items = set\(json\.loads\(current_task\.get\(\'items_processed\', \'\[\]\'\)\)\)\s*\n\s*failed_items = set\(json\.loads\(current_task\.get\(\'items_failed\', \'\[\]\'\)\)\)',
                new_code1,
                content
            )
            print("✅ Исправлена функция process_task_with_checkpoints (regex)")
    
    # Сохраняем файл
    with open('backend/services.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Файл services.py успешно исправлен!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Также проверим database.py
print("\n🔧 Проверка database.py...")

try:
    with open('backend/database.py', 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    # Ищем похожие проблемы
    if 'json.loads(' in db_content:
        # Добавляем безопасную обработку JSON
        old_pattern = r'(\w+) = json\.loads\((\w+)\)'
        new_pattern = r'try:\n            \1 = json.loads(\2) if isinstance(\2, str) else \2\n        except:\n            \1 = []'
        
        # Сохраняем только если есть изменения
        new_db_content = re.sub(old_pattern, new_pattern, db_content)
        if new_db_content != db_content:
            with open('backend/database.py', 'w', encoding='utf-8') as f:
                f.write(new_db_content)
            print("✅ Добавлена безопасная обработка JSON в database.py")
        else:
            print("✅ database.py уже безопасен")
            
except Exception as e:
    print(f"⚠️  Не удалось проверить database.py: {e}")

print("\n✅ Готово! Теперь запустите run_fixed.bat")
input("Нажмите Enter для завершения...")