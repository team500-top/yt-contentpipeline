"""
Исправления для utils.py - запустите этот файл для автоматического исправления
"""
import re

# Читаем файл
with open('shared/utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Исправляем сломанные регулярные выражения
fixes = [
    # Исправление 1
    (r"if not re.match\(r'\^[a-zA-Z0-9_-]\+\s*stop_words =, api_key\):",
     r"if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):"),
    
    # Исправление 2
    (r"return bool\(re.match\(r'\^[a-zA-Z0-9_-]\{11\}\s*stop_words =, video_id\)\)",
     r"return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))"),
    
    # Исправление 3
    (r"return bool\(re.match\(r'\^UC[a-zA-Z0-9_-]\{22\}\s*stop_words =, channel_id\)\)",
     r"return bool(re.match(r'^UC[a-zA-Z0-9_-]{22}$', channel_id))"),
]

# Применяем исправления
for old, new in fixes:
    content = re.sub(old, new, content)

# Дополнительные исправления для незакрытых строк
content = re.sub(r"r'\^[^']+\s+stop_words =", lambda m: m.group(0).split('stop_words')[0] + "$'", content)

# Сохраняем исправленный файл
with open('shared/utils.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Файл utils.py исправлен!")