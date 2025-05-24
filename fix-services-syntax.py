"""
Исправление синтаксической ошибки в services.py
"""
import re

print("🔧 Исправление синтаксической ошибки в services.py...")

try:
    with open('backend/services.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Ищем строку 389 и окружающий контекст
    fixed = False
    in_try_block = False
    try_indent = ""
    
    for i in range(len(lines)):
        line = lines[i]
        
        # Определяем начало try блока
        if line.strip().startswith('try:'):
            in_try_block = True
            try_indent = line[:len(line) - len(line.lstrip())]
        
        # Если мы в try блоке и встречаем строку с меньшим отступом
        elif in_try_block and line.strip() and not line.startswith(try_indent + ' '):
            # Проверяем, есть ли except или finally
            if not line.strip().startswith(('except', 'finally')):
                # Вставляем except перед этой строкой
                lines.insert(i, f"{try_indent}except Exception as e:\n")
                lines.insert(i+1, f"{try_indent}    print(f'Ошибка: {{e}}')\n")
                lines.insert(i+2, f"{try_indent}    pass\n")
                fixed = True
                print(f"✅ Добавлен блок except в строку {i}")
                break
            else:
                in_try_block = False
    
    # Если не нашли конкретную проблему, ищем незакрытые try блоки
    if not fixed:
        content = ''.join(lines)
        
        # Паттерн для поиска try без except/finally
        pattern = r'(\n\s*)try:((?:\n(?!\1(?:except|finally)).*)*)'
        
        def add_except(match):
            indent = match.group(1)
            return match.group(0) + f"{indent}except Exception as e:{indent}    pass\n"
        
        # Заменяем все try блоки без except
        new_content = re.sub(pattern, add_except, content)
        
        if new_content != content:
            lines = new_content.splitlines(True)
            fixed = True
            print("✅ Добавлены недостающие блоки except")
    
    # Сохраняем исправленный файл
    with open('backend/services.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    if fixed:
        print("✅ Файл services.py успешно исправлен!")
    else:
        print("⚠️  Не удалось найти проблему автоматически")
        print("   Проверьте строку 389 вручную")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Альтернативное решение - упрощенный запуск без services
print("\n💡 Альтернативное решение:")
print("   Если проблема не решена, используйте упрощенный сервер:")
print("   python backend/working_server.py")

input("\nНажмите Enter для завершения...")