import redis
import os
from dotenv import load_dotenv

load_dotenv()

print("Тестирование подключения к Redis...")

# Пробуем разные варианты подключения
connections = [
    ("redis://localhost:6379/0", "localhost"),
    ("redis://127.0.0.1:6379/0", "127.0.0.1"),
    (os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"), "from .env")
]

for url, name in connections:
    print(f"\nПробую {name}: {url}")
    try:
        r = redis.from_url(url)
        pong = r.ping()
        if pong:
            print(f"✅ Успешно подключился через {name}!")
            # Тест записи/чтения
            r.set('test', 'hello')
            value = r.get('test')
            print(f"✅ Тест записи/чтения: {value.decode()}")
            r.delete('test')
            print(f"\nИспользуйте этот URL в Celery: {url}")
            break
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Проверка Docker
print("\n" + "="*50)
print("Проверка Docker контейнеров:")
import subprocess
try:
    result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
    print(result.stdout)
except:
    print("❌ Docker не доступен из командной строки")