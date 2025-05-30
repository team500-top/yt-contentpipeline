
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
