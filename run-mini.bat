@echo off
cd /d C:\youtube-analyzer

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting minimal server...
python backend/working_server_mini.py

pause