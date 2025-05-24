@echo off
echo Настройка автозапуска YouTube Analyzer...

:: Создание задачи в планировщике
schtask /create /tn "YouTube Analyzer AutoStart" ^
    /tr "\"%~dp0run.bat\"" ^
    /sc onlogon ^
    /delay 0001:00 ^
    /rl highest ^
    /f

:: Дополнительная задача для запуска в определенное время
schtask /create /tn "YouTube Analyzer Daily" ^
    /tr "\"%~dp0run.bat\"" ^
    /sc daily ^
    /st 09:00 ^
    /f

echo.
echo ✅ Автозапуск настроен!
echo.
echo Задачи:
echo 1. При входе в систему (через 1 минуту)
echo 2. Ежедневно в 09:00
echo.
echo Для изменения используйте Планировщик заданий Windows
pause