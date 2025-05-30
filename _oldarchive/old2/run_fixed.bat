@echo off
cd /d C:\youtube-analyzer

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting fixed server...
python backend/main_fixed.py

pause