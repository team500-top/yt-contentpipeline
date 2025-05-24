@echo off
cd /d C:\youtube-analyzer

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting complete server...
python backend/complete_server.py

pause