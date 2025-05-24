"""
Скрипт для исправления синтаксических ошибок в utils.py
"""

# Читаем файл
try:
    with open('shared/utils.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
except Exception as e:
    print(f"Ошибка чтения файла: {e}")
    exit(1)

# Ищем и исправляем проблемные строки
fixed_lines = []
for i, line in enumerate(lines):
    # Исправляем незакрытые регулярные выражения
    if "re.match(r'^[a-zA-Z0-9_-]{11}" in line and "stop_words" in line:
        line = "        return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))\n"
        print(f"Исправлена строка {i+1}: video_id regex")
    
    elif "re.match(r'^UC[a-zA-Z0-9_-]{22}" in line and "stop_words" in line:
        line = "        return bool(re.match(r'^UC[a-zA-Z0-9_-]{22}$', channel_id))\n"
        print(f"Исправлена строка {i+1}: channel_id regex")
    
    elif "re.match(r'^[a-zA-Z0-9_-]+" in line and "stop_words" in line:
        line = "        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):\n"
        print(f"Исправлена строка {i+1}: api_key regex")
    
    fixed_lines.append(line)

# Сохраняем исправленный файл
try:
    with open('shared/utils.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    print("\n✅ Файл shared/utils.py успешно исправлен!")
except Exception as e:
    print(f"Ошибка записи файла: {e}")
    exit(1)

print("\nТеперь попробуйте запустить: python backend/main.py")