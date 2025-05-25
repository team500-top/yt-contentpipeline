# YouTube Content Analyzer

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue.js-3.0-brightgreen.svg" alt="Vue.js">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 📖 О проекте

YouTube Content Analyzer - это локальная веб-система для анализа YouTube контента с целью построения эффективной контент-стратегии. Система позволяет парсить видео и каналы конкурентов, анализировать успешный контент в вашей нише и получать рекомендации по созданию видео.

### 🎯 Основные возможности

- **Парсинг YouTube**: поиск по ключевым словам и анализ каналов
- **Детальный анализ**: 40+ параметров для каждого видео
- **Умные рекомендации**: AI-powered анализ успешности контента
- **Управление задачами**: пауза/возобновление парсинга
- **Аналитика**: визуализация трендов и метрик
- **Экспорт данных**: CSV, Excel, JSON форматы

## 🛠️ Технологии

### Backend
- **Python 3.11+** - основной язык
- **FastAPI** - веб-фреймворк
- **SQLite** - база данных
- **Celery + Redis** - очередь задач
- **YouTube API v3** - официальный API
- **yt-dlp** - расширенный парсинг

### Frontend
- **Vue.js 3** - реактивный интерфейс
- **Tailwind CSS** - современный дизайн
- **Chart.js** - графики и диаграммы
- **WebSocket** - real-time обновления

## 📋 Системные требования

- Windows 11 (или Windows 10)
- Python 3.11 или выше
- Docker Desktop для Windows
- 8 GB свободного места на диске
- Стабильное интернет-соединение

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
cd C:\
git clone https://github.com/team500-top/yt-contentpipeline/ youtube-analyzer
cd youtube-analyzer
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Убедитесь, что файл `.env` содержит:

```env
YOUTUBE_API_KEY=AIzaSyBoBi0pJmn_fhgskNoAYQLnwYxUNG1sJGg
DATABASE_PATH=youtube_data.db
HOST=127.0.0.1
PORT=8000
DEBUG=true
TEMP_DIR=temp
EXPORT_DIR=exports
REDIS_URL=redis://localhost:6379/0
```

### 5. Запуск приложения

```bash
# Запустить все сервисы
start.bat

# Или вручную:
# 1. Redis
docker-compose up -d

# 2. Celery Worker (новое окно)
venv\Scripts\activate
celery -A tasks worker --loglevel=info --pool=solo

# 3. FastAPI (новое окно)
venv\Scripts\activate
python main.py
```

### 6. Открыть в браузере

```
http://127.0.0.1:8000
```

## 📱 Интерфейс

### Вкладка "Парсинг"
- Поиск видео по ключевым словам
- Парсинг видео с канала
- Фильтры: тип видео, сортировка
- История поисковых запросов

### Вкладка "Видео"
- Таблица/карточки с превью
- Фильтрация и сортировка
- Детальная информация о видео
- Экспорт данных

### Вкладка "Задачи"
- Мониторинг активных задач
- Прогресс выполнения
- Управление: пауза/возобновление/отмена
- История завершенных задач

### Вкладка "Аналитика"
- Общая статистика
- Графики трендов
- Топ видео по метрикам
- Инсайты по нише

### Вкладка "Настройки"
- API ключи
- Параметры парсинга
- Экспорт/импорт базы данных

## 🔧 Управление

### Остановка сервисов

```bash
stop.bat
```

### Ручное управление

```bash
# Просмотр логов Redis
docker logs youtube_analyzer_redis

# Мониторинг Celery задач
celery -A tasks flower

# Проверка здоровья API
curl http://127.0.0.1:8000/health
```

## 📊 Собираемые параметры

Система анализирует более 40 параметров для каждого видео:

- **Базовые метрики**: просмотры, лайки, комментарии
- **Вовлеченность**: engagement rate, соотношения
- **Контент**: ключевые слова, длительность, категория
- **Оптимизация**: заголовок, описание, теги
- **Канал**: средние показатели, частота публикаций
- **AI-анализ**: рекомендации, стратегия

## 🐛 Решение проблем

### Redis не запускается
```bash
# Проверить Docker
docker --version

# Перезапустить Docker Desktop
# Запустить Redis вручную
docker run -d --name youtube_analyzer_redis -p 6379:6379 redis:7-alpine
```

### Celery не работает на Windows
```bash
# Использовать solo pool
celery -A tasks worker --loglevel=info --pool=solo
```

### Ошибки с зависимостями
```bash
# Обновить pip
python -m pip install --upgrade pip

# Переустановить проблемный пакет
pip uninstall package_name
pip install package_name
```

## 📝 Лицензия

MIT License - свободное использование и модификация

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing`)
5. Создайте Pull Request

## 📧 Поддержка

- GitHub Issues: [https://github.com/team500-top/yt-contentpipeline/issues](https://github.com/team500-top/yt-contentpipeline/issues)
- Email: support@youtube-analyzer.com

---

<div align="center">
  Made with ❤️ for YouTube Creators
</div>