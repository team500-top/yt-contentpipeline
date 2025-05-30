"""
Исправление конкретной ошибки в строке 54-55 services.py
"""

print("🔧 Исправление ошибки отступа в строке 54-55...")

try:
    with open('backend/services.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Всего строк: {len(lines)}")
    
    # Показываем проблемную область
    print("\n📋 Строки 50-60:")
    for i in range(max(0, 49), min(len(lines), 60)):
        print(f"{i+1:3d}: {repr(lines[i])}")
    
    # Находим проблему
    if len(lines) > 54:
        line_54 = lines[53]  # индекс 53 = строка 54
        line_55 = lines[54] if len(lines) > 54 else None
        
        print(f"\nСтрока 54: {repr(line_54)}")
        print(f"Строка 55: {repr(line_55)}")
        
        # Если строка 54 содержит определение функции без тела
        if line_54.strip().startswith('def ') and line_54.strip().endswith(':'):
            # Проверяем, есть ли после неё строка документации
            if line_55 and line_55.strip().startswith('"""'):
                # Вставляем правильный отступ перед docstring
                indent = len(line_54) - len(line_54.lstrip()) + 4
                lines[54] = ' ' * indent + lines[54].lstrip()
                print(f"✅ Исправлен отступ для docstring в строке 55")
                
                # Если после docstring нет кода, добавляем pass
                # Ищем закрывающие кавычки
                docstring_end = -1
                for j in range(54, len(lines)):
                    if '"""' in lines[j] and j > 54:
                        docstring_end = j
                        break
                
                if docstring_end > 0 and docstring_end + 1 < len(lines):
                    next_line = lines[docstring_end + 1]
                    # Если следующая строка имеет меньший отступ, добавляем pass
                    if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= len(line_54) - len(line_54.lstrip()):
                        lines.insert(docstring_end + 1, ' ' * indent + 'pass\n')
                        print(f"✅ Добавлен pass после docstring")
    
    # Альтернативный подход - найти все функции без тела
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Если это определение функции
        if line.strip().startswith('def ') and line.strip().endswith(':'):
            fixed_lines.append(line)
            func_indent = len(line) - len(line.lstrip())
            body_indent = func_indent + 4
            i += 1
            
            # Проверяем следующие строки
            has_body = False
            
            # Пропускаем docstring если есть
            if i < len(lines) and lines[i].strip().startswith('"""'):
                # Исправляем отступ docstring
                fixed_lines.append(' ' * body_indent + lines[i].lstrip())
                i += 1
                
                # Ищем конец docstring
                while i < len(lines) and '"""' not in lines[i-1][lines[i-1].find('"""')+3:]:
                    fixed_lines.append(' ' * body_indent + lines[i].lstrip())
                    i += 1
            
            # Проверяем, есть ли тело функции
            if i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_line.strip() and next_indent > func_indent:
                    has_body = True
            
            # Если нет тела, добавляем pass
            if not has_body:
                fixed_lines.append(' ' * body_indent + 'pass\n')
                print(f"✅ Добавлен pass для функции в строке {len(fixed_lines)}")
        else:
            fixed_lines.append(line)
            i += 1
    
    # Сохраняем исправленный файл
    with open('backend/services.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("\n✅ Файл исправлен!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n🎯 Теперь проверьте файл:")
print("   python check_services.py")

input("\nНажмите Enter...")