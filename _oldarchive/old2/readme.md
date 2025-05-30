# 🎥 YouTube Content Analyzer

> Мощный инструмент для анализа YouTube контента, трендов и оптимизации видео стратегий

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Возможности

- 🔍 **Поиск и анализ видео** по ключевым запросам
- 📺 **Анализ каналов** and их контент-стратегий  
- 🎤 **Транскрибация видео** через Whisper AI
- 📊 **Метрики вовлеченности** и аналитика
- 💡 **Автоматические рекомендации** по улучшению контента
- 📈 **Экспорт данных** в Excel для дальнейшего анализа
- 🌐 **Современный веб-интерфейс** с real-time обновлениями

## 🚀 Быстрый старт

### 1. Скачивание и установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/youtube-analyzer.git
cd youtube-analyzer

# Запуск (Windows)
run.bat

# Запуск (Linux/macOS)
chmod +x run.sh
./run.sh
```

### 2. Настройка YouTube API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите YouTube Data API v3
4. Создайте API ключ
5. Добавьте ключ в файл `.env`:

```env
YOUTUBE_API_KEY=your_api_key_here
```

### 3. Использование

1. Откройте http://localhost:8000 в браузере
2. Перейдите в "Настройки" и добавьте YouTube API ключ
3. Создайте новую задачу анализа
4. Просматривайте результаты в разделах "Видео" и "Каналы"

## 📋 Требования

- **Python 3.8+** (рекомендуется 3.10+)
- **YouTube Data API v3** ключ
- **4GB RAM** (минимум для Whisper)
- **1GB свободного места** для временных файлов

### Системные зависимости

**Windows:**
```bash
# Установите Python с python.org
# FFmpeg будет установлен автоматически
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg
```

**macOS:**
```bash
brew install python ffmpeg
```

## 🏗️ Архитектура

```
youtube-analyzer/
├── 📁 backend/              # FastAPI сервер
│   ├── main.py             # Главный файл приложения
│   ├── services.py         # API сервисы
│   ├── models.py           # Модели данных
│   └── database.py         # Управление БД
├── 📁 frontend/            # Веб-интерфейс
│   ├── index.html          # Главная страница
│   ├── app.js              # JavaScript логика
│   └── style.css           # Стили
├── 📁 shared/              # Общие модули
│   ├── config.py           # Конфигурация
│   ├── utils.py            # Утилиты
│   └── youtube_parser.py   # YouTube API
├── requirements.txt        # Python зависимости
└── run.bat                 # Скрипт запуска
```

## 📊 Анализируемые данные

### Основные метрики
- **Просмотры, лайки, комментарии**
- **Коэффициент вовлеченности**
- **Соотношения лайков и комментариев**
- **Длительность и тип видео** (Shorts/обычное)

### Контент-анализ
- **Транскрипция видео** (субтитры + Whisper)
- **Ключевые слова** из транскриптов
- **Скорость речи** и структура контента
- **Анализ заголовков** и описаний
- **Рекламные интеграции**

### Технические данные
- **Качество видео** (SD/HD/4K)
- **Наличие субтитров**
- **Использование эмодзи**
- **Количество ссылок в описании**

## ⚙️ Конфигурация

### Основные настройки (.env)
```env
YOUTUBE_API_KEY=your_api_key_here
DATABASE_PATH=youtube_data.db
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

### Лимиты обработки (config.json)
```json
{
  "max_long_videos_channel": 5,
  "max_long_videos_search": 5,
  "max_shorts_channel": 5,
  "max_shorts_search": 5,
  "whisper_model": "tiny",
  "max_transcript_length": 50000
}
```

## 🔧 API Endpoints

### Задачи
- `POST /api/tasks` - Создать задачу анализа
- `GET /api/tasks` - Получить список задач
- `POST /api/tasks/{id}/pause` - Поставить задачу на паузу

### Данные
- `GET /api/data/videos` - Получить видео
- `GET /api/data/channels` - Получить каналы
- `GET /api/data/stats` - Статистика
- `GET /api/data/export` - Экспорт в Excel

### Конфигурация
- `GET /api/config` - Получить настройки
- `POST /api/config` - Обновить настройки

Полная документация API: http://localhost:8000/docs

## 📈 Примеры использования

### Анализ конкурентов
```python
# Создать задачу для анализа конкурентов
keywords = [
    "python tutorial 2024",
    "web development guide",
    "machine learning basics"
]

channels = [
    "https://youtube.com/@competitor1",
    "https://youtube.com/@competitor2"
]
```

### Исследование трендов
- Анализ популярных ключевых слов в нише
- Сравнение метрик вовлеченности
- Оптимизация длины и структуры контента
- A/B тестирование заголовков

## 🚀 Оптимизация производительности

### Для быстрой работы:
- Используйте модель Whisper `tiny` для ускорения
- Ограничивайте количество видео до 50 за задачу
- Включите кэширование результатов

### Для точности анализа:
- Используйте модель Whisper `base` или `small`
- Анализируйте больше видео для статистической значимости
- Комбинируйте поиск по релевантности и дате

### GPU ускорение (опционально):
```bash
# Для NVIDIA GPU
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🔒 Безопасность данных

### Что НЕ попадает в Git:
- ✅ **API ключи** (.env, config.json)
- ✅ **База данных** с проанализированными видео
- ✅ **Временные файлы** и кэш
- ✅ **Экспортированные отчеты**

### Что можно коммитить:
- ✅ **Исходный код** (.py, .html, .js)
- ✅ **Примеры конфигурации** (.env.example)
- ✅ **Документация** (README.md)
- ✅ **Структура БД** (без данных)

## 🐛 Решение проблем

### Частые ошибки:

**❌ "YouTube API key not configured"**
```bash
# Добавьте API ключ в .env файл
echo "YOUTUBE_API_KEY=your_key_here" > .env
```

**❌ "Quota exceeded"**
```bash
# Уменьшите лимиты в config.json
# YouTube API: 10,000 запросов/день по умолчанию
```

**❌ "Whisper model not found"**
```bash
# Переустановите Whisper
pip uninstall openai-whisper
pip install openai-whisper
```

**❌ "Port 8000 already in use"**
```bash
# Измените порт в .env
echo "PORT=8001" >> .env
```

### Логи и отладка:
```bash
# Проверка статуса
curl http://localhost:8000/health

# Просмотр логов
tail -f logs/app.log
```

## 📚 Дополнительные ресурсы

- 📖 [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- 🎤 [OpenAI Whisper](https://github.com/openai/whisper)
- ⚡ [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🐍 [Python Best Practices](https://docs.python.org/3/)

## 🤝 Участие в разработке

1. **Fork** репозитория
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Создайте **Pull Request**

### Стандарты кода:
- Используйте **Black** для форматирования
- Добавляйте **типы** (type hints)
- Пишите **документацию** для функций
- Покрывайте код **тестами**

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- [OpenAI Whisper](https://github.com/openai/whisper) за транскрипцию
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) за загрузку видео
- [FastAPI](https://fastapi.tiangolo.com/) за отличный API фреймворк
- [Lucide Icons](https://lucide.dev/) за современные иконки

---

<p align="center">
  <strong>YouTube Content Analyzer</strong><br>
  Сделано с ❤️ для создателей контента
</p>