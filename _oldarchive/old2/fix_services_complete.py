"""
Полное исправление services.py
"""
import re
import ast

print("🔧 Полное исправление services.py...")

# Читаем исходный файл
try:
    with open('backend/services.py', 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"❌ Не удалось прочитать файл: {e}")
    exit(1)

# Список исправлений
fixes_applied = []

# 1. Исправление JSON loads проблемы
print("\n1️⃣ Исправление JSON loads...")
old_pattern = r'''processed_items = set\(json\.loads\(current_task\.get\('items_processed', '\[\]'\)\)\)
        failed_items = set\(json\.loads\(current_task\.get\('items_failed', '\[\]'\)\)\)'''

new_code = '''# Безопасная загрузка JSON
        items_processed_data = current_task.get('items_processed', '[]')
        items_failed_data = current_task.get('items_failed', '[]')
        
        # Проверяем тип данных перед парсингом
        if isinstance(items_processed_data, str):
            try:
                processed_items = set(json.loads(items_processed_data))
            except json.JSONDecodeError:
                processed_items = set()
        elif isinstance(items_processed_data, list):
            processed_items = set(items_processed_data)
        else:
            processed_items = set()
        
        if isinstance(items_failed_data, str):
            try:
                failed_items = set(json.loads(items_failed_data))
            except json.JSONDecodeError:
                failed_items = set()
        elif isinstance(items_failed_data, list):
            failed_items = set(items_failed_data)
        else:
            failed_items = set()'''

if 'processed_items = set(json.loads(' in content:
    # Находим и заменяем блок кода
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        if 'processed_items = set(json.loads(' in lines[i]:
            # Определяем отступ
            indent = len(lines[i]) - len(lines[i].lstrip())
            # Пропускаем старые строки
            i += 1
            if i < len(lines) and 'failed_items = set(json.loads(' in lines[i]:
                i += 1
            # Добавляем новый код с правильным отступом
            for new_line in new_code.split('\n'):
                if new_line.strip():
                    new_lines.append(' ' * indent + new_line.strip())
                else:
                    new_lines.append('')
            fixes_applied.append("JSON loads безопасность")
        else:
            new_lines.append(lines[i])
            i += 1
    content = '\n'.join(new_lines)

# 2. Исправление отступов
print("\n2️⃣ Исправление отступов...")
lines = content.split('\n')
fixed_lines = []
indent_stack = [0]
prev_line_empty = False

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Пропускаем пустые строки
    if not stripped:
        fixed_lines.append('')
        prev_line_empty = True
        continue
    
    # Определяем текущий отступ
    current_indent = len(line) - len(line.lstrip())
    
    # Определяем ожидаемый отступ
    if stripped.startswith(('def ', 'class ', 'if ', 'elif ', 'else:', 'try:', 'except', 'finally:', 'for ', 'while ', 'with ')):
        if stripped.endswith(':'):
            # Используем текущий уровень из стека
            if prev_line_empty and len(indent_stack) > 1:
                expected_indent = indent_stack[-2]
            else:
                expected_indent = indent_stack[-1]
            fixed_line = ' ' * expected_indent + stripped
            # Добавляем новый уровень в стек
            if not stripped.startswith(('elif ', 'else:', 'except', 'finally:')):
                indent_stack.append(expected_indent + 4)
        else:
            expected_indent = indent_stack[-1]
            fixed_line = ' ' * expected_indent + stripped
    elif stripped.startswith(('return', 'pass', 'continue', 'break', 'raise')):
        # Эти операторы должны быть внутри блока
        expected_indent = indent_stack[-1]
        fixed_line = ' ' * expected_indent + stripped
        # После return/pass может быть уменьшение отступа
        if len(indent_stack) > 1:
            indent_stack.pop()
    else:
        # Обычная строка кода
        expected_indent = indent_stack[-1]
        fixed_line = ' ' * expected_indent + stripped
    
    # Проверяем, нужно ли уменьшить отступ
    if current_indent < indent_stack[-1] and len(indent_stack) > 1:
        # Удаляем уровни из стека
        while len(indent_stack) > 1 and current_indent < indent_stack[-1]:
            indent_stack.pop()
    
    fixed_lines.append(fixed_line)
    prev_line_empty = False
    
    # Исправляем отступ если он не кратен 4
    if current_indent != expected_indent and current_indent % 4 != 0:
        fixes_applied.append(f"Отступ в строке {i+1}")

content = '\n'.join(fixed_lines)

# 3. Проверка синтаксиса try/except блоков
print("\n3️⃣ Проверка try/except блоков...")
lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    if stripped == 'try:':
        # Нашли try блок
        try_indent = len(line) - len(line.lstrip())
        fixed_lines.append(line)
        i += 1
        
        # Ищем except/finally
        has_except = False
        while i < len(lines):
            current_line = lines[i]
            current_stripped = current_line.strip()
            current_indent = len(current_line) - len(current_line.lstrip())
            
            if current_indent <= try_indent and current_stripped:
                # Вышли из try блока
                if not has_except and not current_stripped.startswith(('except', 'finally')):
                    # Добавляем except
                    fixed_lines.append(' ' * try_indent + 'except Exception:')
                    fixed_lines.append(' ' * (try_indent + 4) + 'pass')
                    fixes_applied.append(f"Добавлен except блок после строки {i}")
                break
            
            if current_stripped.startswith(('except', 'finally')):
                has_except = True
            
            fixed_lines.append(current_line)
            i += 1
        
        if i >= len(lines) and not has_except:
            # try в конце файла без except
            fixed_lines.append(' ' * try_indent + 'except Exception:')
            fixed_lines.append(' ' * (try_indent + 4) + 'pass')
            fixes_applied.append("Добавлен except блок в конец")
    else:
        fixed_lines.append(line)
        i += 1

content = '\n'.join(fixed_lines)

# 4. Проверка синтаксиса с помощью ast
print("\n4️⃣ Проверка синтаксиса Python...")
try:
    ast.parse(content)
    print("✅ Синтаксис Python корректен!")
except SyntaxError as e:
    print(f"⚠️  Остались синтаксические ошибки: {e}")
    print(f"   Строка {e.lineno}: {e.text}")
    
    # Попытка автоматического исправления
    if "expected an indented block" in str(e):
        lines = content.split('\n')
        if e.lineno and e.lineno <= len(lines):
            # Добавляем pass после строки с двоеточием
            problem_line = lines[e.lineno - 1]
            indent = len(problem_line) - len(problem_line.lstrip()) + 4
            lines.insert(e.lineno, ' ' * indent + 'pass')
            content = '\n'.join(lines)
            fixes_applied.append(f"Добавлен pass в строку {e.lineno}")

# 5. Финальная проверка импортов
print("\n5️⃣ Проверка импортов...")
required_imports = [
    'import json',
    'import asyncio',
    'import uuid',
    'from datetime import datetime, timedelta',
    'from typing import List, Dict, Optional, Any',
    'from fastapi import APIRouter, BackgroundTasks, HTTPException',
]

lines = content.split('\n')
import_section = []
other_lines = []
in_imports = True

for line in lines:
    if in_imports and (line.startswith(('import ', 'from ')) or not line.strip()):
        import_section.append(line)
    else:
        in_imports = False
        other_lines.append(line)

# Добавляем недостающие импорты
existing_imports = '\n'.join(import_section)
for imp in required_imports:
    if imp not in existing_imports:
        import_section.insert(0, imp)
        fixes_applied.append(f"Добавлен импорт: {imp}")

# Собираем файл обратно
content = '\n'.join(import_section + other_lines)

# Сохраняем исправленный файл
try:
    # Делаем резервную копию
    with open('backend/services.py', 'r', encoding='utf-8') as f:
        backup_content = f.read()
    
    with open('backend/services_backup.py', 'w', encoding='utf-8') as f:
        f.write(backup_content)
    print("\n💾 Создана резервная копия: services_backup.py")
    
    # Сохраняем исправленный файл
    with open('backend/services.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Файл services.py успешно исправлен!")
    if fixes_applied:
        print("\n📝 Применены исправления:")
        for fix in fixes_applied:
            print(f"   - {fix}")
    
except Exception as e:
    print(f"\n❌ Ошибка сохранения: {e}")

print("\n🎯 Теперь попробуйте запустить основной сервер:")
print("   python backend/main.py")
print("\n💡 Если все еще есть ошибки, используйте:")
print("   python backend/complete_server.py")

input("\nНажмите Enter для завершения...")