# Подробная инструкция по установке YouTube Content Analyzer

## Системные требования
- Windows 11
- Python 3.11+
- 8 GB свободного места на диске
- Интернет-соединение

## Шаг 1: Установка Docker Desktop для Windows

### 1.1 Проверка системных требований для Docker
1. Откройте PowerShell от имени администратора
2. Выполните команду для проверки виртуализации:
```powershell
Get-ComputerInfo -property "HyperVRequirementVirtualizationFirmwareEnabled"
```
Должно показать `True`

### 1.2 Включение WSL 2 (Windows Subsystem for Linux)
В PowerShell от имени администратора выполните:
```powershell
# Включение WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Включение Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Перезагрузите компьютер
Restart-Computer
```

### 1.3 Установка WSL 2
После перезагрузки откройте PowerShell от имени администратора:
```powershell
# Установка WSL 2
wsl --install

# Установка WSL 2 как версии по умолчанию
wsl --set-default-version 2

# Обновление ядра WSL
wsl --update
```

### 1.4 Установка Docker Desktop
1. Скачайте Docker Desktop с официального сайта:
   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. Запустите установщик и следуйте инструкциям:
   - ✅ Отметьте "Use WSL 2 instead of Hyper-V"
   - ✅ Отметьте "Add shortcut to desktop"

3. После установки перезагрузите компьютер

4. Запустите Docker Desktop:
   - При первом запуске примите лицензионное соглашение
   - Дождитесь, пока Docker полностью запустится (иконка в трее станет зеленой)

### 1.5 Проверка установки Docker
Откройте новое окно командной строки:
```cmd
docker --version
docker-compose --version
docker run hello-world
```

## Шаг 2: Альтернатива - Установка Redis без Docker

Если не хотите использовать Docker, можно установить Redis напрямую:

### 2.1 Скачивание Redis для Windows
1. Скачайте Redis с GitHub:
   https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.msi

2. Установите Redis, следуя инструкциям установщика

3. Redis автоматически запустится как служба Windows

### 2.2 Проверка Redis
```cmd
redis-cli ping
```
Должно вернуть `PONG`

## Шаг 3: Установка проекта YouTube Analyzer

### 3.1 Клонирование репозитория
```cmd
cd C:\
git clone https://github.com/team500-top/yt-contentpipeline/ youtube-analyzer
cd youtube-analyzer
```

### 3.2 Создание виртуального окружения Python
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3.3 Обновление pip
```cmd
python -m pip install --upgrade pip
```

### 3.4 Установка зависимостей
```cmd
pip install -r requirements.txt
```

Если возникают ошибки с конкретными пакетами:
```cmd
# Установка проблемных пакетов по отдельности
pip install --no-deps celery==5.3.4
pip install redis==4.6.0
pip install kombu==5.4.0
```

### 3.5 Установка дополнительных компонентов для Windows
```cmd
# Для Celery на Windows
pip install eventlet
```

## Шаг 4: Настройка проекта

### 4.1 Проверка файла .env
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

### 4.2 Создание необходимых директорий
```cmd
mkdir temp
mkdir exports
```

## Шаг 5: Запуск приложения

### 5.1 Если используете Docker:
```cmd
# Запуск Redis через Docker
docker-compose up -d

# Проверка, что Redis работает
docker ps
```

### 5.2 Если установили Redis напрямую:
Redis уже должен работать как служба Windows

### 5.3 Запуск Celery Worker (в отдельном терминале)
```cmd
# Активируйте виртуальное окружение
cd C:\youtube-analyzer
venv\Scripts\activate

# Запуск Celery для Windows
celery -A tasks worker --loglevel=info --pool=eventlet
```

### 5.4 Запуск основного приложения (в новом терминале)
```cmd
# Активируйте виртуальное окружение
cd C:\youtube-analyzer
venv\Scripts\activate

# Запуск приложения
python main.py
```

## Шаг 6: Проверка работы

1. Откройте браузер и перейдите по адресу: http://127.0.0.1:8000
2. Вы должны увидеть интерфейс YouTube Analyzer

## Устранение проблем

### Проблема: "Docker Desktop requires Windows 10 Pro/Enterprise"
**Решение**: Используйте установку Redis без Docker (см. Шаг 2)

### Проблема: "pip install" выдает ошибки с torch
**Решение**: Установите PyTorch отдельно:
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Проблема: Celery не запускается на Windows
**Решение**: Используйте eventlet:
```cmd
pip install eventlet
celery -A tasks worker --loglevel=info --pool=eventlet
```

### Проблема: "Microsoft Visual C++ 14.0 is required"
**Решение**: Установите Microsoft C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Проблема: Ошибки с lxml
**Решение**: Установите предкомпилированную версию:
```cmd
pip install --upgrade --force-reinstall lxml
```

## Быстрый запуск (после установки)

Создайте файл `start.bat` в папке проекта:
```batch
@echo off
echo Starting YouTube Analyzer...

:: Запуск Redis (если используете Docker)
start "Redis" docker-compose up

:: Ждем 5 секунд для запуска Redis
timeout /t 5

:: Запуск Celery
start "Celery Worker" cmd /k "venv\Scripts\activate && celery -A tasks worker --loglevel=info --pool=eventlet"

:: Ждем 3 секунды
timeout /t 3

:: Запуск приложения
start "YouTube Analyzer" cmd /k "venv\Scripts\activate && python main.py"

:: Открытие браузера
timeout /t 5
start http://127.0.0.1:8000

echo YouTube Analyzer запущен!
pause
```

## Остановка приложения

Создайте файл `stop.bat`:
```batch
@echo off
echo Stopping YouTube Analyzer...

:: Остановка процессов Python
taskkill /F /IM python.exe

:: Остановка Redis через Docker
docker-compose down

echo YouTube Analyzer остановлен!
pause
```

## Дополнительные настройки

### Автозапуск при старте Windows
1. Нажмите `Win + R`, введите `shell:startup`
2. Скопируйте `start.bat` в открывшуюся папку

### Настройка брандмауэра Windows
Если возникают проблемы с подключением:
1. Откройте "Брандмауэр Windows в режиме повышенной безопасности"
2. Создайте правило для входящих подключений на порт 8000
3. Создайте правило для Redis на порт 6379

## Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все службы запущены
3. Проверьте, что порты 8000 и 6379 не заняты другими приложениями:
```cmd
netstat -an | findstr :8000
netstat -an | findstr :6379
```