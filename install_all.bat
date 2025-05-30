@echo off
REM =============================================================================
REM YouTube Analyzer - Complete Installation (Fixed Encoding)
REM =============================================================================

title YouTube Analyzer - Full Installation
color 0B

echo.
echo ===============================================================================
echo    YOUTUBE ANALYZER - COMPLETE INSTALLATION
echo    Automatic system setup
echo ===============================================================================
echo.

REM Check administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] ADMINISTRATOR RIGHTS REQUIRED!
    echo.
    echo To install, you need to run this file as administrator:
    echo    1. Right-click on the file
    echo    2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Administrator rights obtained
echo.

REM Create base structure
echo [STEP] Creating project structure...
if not exist "C:\" (
    echo [ERROR] Drive C: is not accessible!
    pause
    exit /b 1
)

REM Create main folder with permissions
mkdir "C:\youtube-analyzer" 2>nul
cd /d "C:\youtube-analyzer"

REM Set full permissions for folder
icacls "C:\youtube-analyzer" /grant Everyone:F /T /Q >nul 2>&1

echo [OK] Folder C:\youtube-analyzer created with full permissions

REM Create subfolders
for %%d in (data reports logs src templates tests .cache venv) do (
    mkdir "%%d" 2>nul
)

echo [OK] Folder structure created

REM Check and install Python
echo.
echo [STEP] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo [INFO] Automatic Python installation...
    
    REM Download and install Python
    powershell -Command "& {
        $url = 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe'
        $output = 'python-installer.exe'
        Write-Host 'Downloading Python...'
        try {
            Invoke-WebRequest -Uri $url -OutFile $output
            Write-Host 'Installing Python...'
            Start-Process -FilePath $output -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait
            Remove-Item $output
        } catch {
            Write-Host 'Download failed. Please install Python manually.'
        }
    }"
    
    REM Update PATH
    refreshenv >nul 2>&1
    
    REM Re-check
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Automatic Python installation failed
        echo [INFO] Please install Python manually from https://python.org/downloads/
        echo [WARNING] Make sure to check "Add Python to PATH"
        pause
        exit /b 1
    )
)

echo [OK] Python is installed:
python --version

REM Create virtual environment
echo.
echo [STEP] Setting up virtual environment...
if not exist "venv\Scripts\python.exe" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment created

REM Activate and update pip
call venv\Scripts\activate
python -m pip install --upgrade pip --quiet

echo [OK] pip updated

REM Install dependencies step by step
echo.
echo [STEP] Installing dependencies...

echo   [INFO] Core libraries...
pip install --quiet requests beautifulsoup4 pandas numpy python-dotenv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install core libraries
    pause
    exit /b 1
)

echo   [INFO] Excel support...
pip install --quiet openpyxl xlsxwriter
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Excel libraries
    pause
    exit /b 1
)

echo   [INFO] YouTube libraries...
pip install --quiet yt-dlp youtube-transcript-api google-api-python-client
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install YouTube libraries
    pause
    exit /b 1
)

echo   [INFO] NLP libraries...
pip install --quiet nltk spacy textstat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install NLP libraries
    pause
    exit /b 1
)

echo   [INFO] Visualization...
pip install --quiet matplotlib seaborn wordcloud plotly
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install visualization libraries
    pause
    exit /b 1
)

echo   [INFO] Utilities...
pip install --quiet tqdm rich colorama diskcache fake-useragent psutil
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install utilities
    pause
    exit /b 1
)

echo [OK] All dependencies installed

REM Download language models
echo.
echo [STEP] Downloading language models...

echo   [INFO] NLTK data...
python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    print('[OK] NLTK data downloaded')
except Exception as e:
    print(f'[WARNING] NLTK download failed: {e}')
"

echo   [INFO] spaCy model...
python -m spacy download ru_core_news_sm --quiet
if %errorlevel% equ 0 (
    echo [OK] spaCy model downloaded
) else (
    echo [WARNING] spaCy model not downloaded ^(fallback will be used^)
)

REM Create configuration files
echo.
echo [STEP] Creating configuration...

REM Create .env file
(
echo # =============================================================================
echo # YouTube Analyzer Configuration - Auto-generated
echo # =============================================================================
echo.
echo # YouTube Data API v3 Key
echo # Get from: https://console.cloud.google.com/
echo YOUTUBE_API_KEY=
echo.
echo # Cookies file for bypassing restrictions
echo YOUTUBE_COOKIES_FILE=C:\youtube-analyzer\cookies.txt
echo.
echo # Proxy settings ^(optional^)
echo HTTP_PROXY=
echo HTTPS_PROXY=
echo.
echo # Analysis limits
echo MAX_TOTAL_VIDEOS=50
echo MAX_CHANNELS_TO_ANALYZE=20
echo MAX_VIDEOS_PER_KEYWORD=10
echo.
echo # Performance
echo MAX_WORKERS=4
echo REQUEST_DELAY=2.0
echo API_REQUEST_DELAY=1.0
echo.
echo # Functionality
echo ENABLE_TRANSCRIPT_EXTRACTION=true
echo ENABLE_CONTENT_ANALYSIS=true
echo ENABLE_SENTIMENT_ANALYSIS=false
echo.
echo # Output
echo EXCEL_OUTPUT_ENABLED=true
echo JSON_OUTPUT_ENABLED=false
echo CHARTS_ENABLED=true
echo.
echo # Logging
echo LOG_LEVEL=INFO
echo LOG_FILE=C:\youtube-analyzer\logs\youtube_analysis.log
echo.
echo # Caching
echo ENABLE_CACHING=true
echo CACHE_DURATION_HOURS=24
) > .env

echo [OK] Basic .env configuration created

REM Create .gitignore
(
echo # Secret data
echo .env
echo cookies.txt
echo *.key
echo.
echo # Python
echo __pycache__/
echo *.pyc
echo venv/
echo.
echo # Logs and cache
echo logs/
echo .cache/
echo *.log
echo.
echo # Temporary files
echo *.tmp
echo .DS_Store
echo Thumbs.db
) > .gitignore

echo [OK] .gitignore created

REM Create __init__.py files
echo. > src\__init__.py
echo. > templates\__init__.py  
echo. > tests\__init__.py

REM Create requirements.txt
(
echo # YouTube Analyzer Requirements
echo requests==2.31.0
echo beautifulsoup4==4.12.2
echo pandas==2.1.4
echo numpy==1.24.3
echo python-dotenv==1.0.0
echo openpyxl==3.1.2
echo yt-dlp==2023.12.30
echo youtube-transcript-api==0.6.1
echo google-api-python-client==2.110.0
echo nltk==3.8.1
echo spacy==3.7.2
echo textstat==0.7.3
echo matplotlib==3.8.2
echo seaborn==0.13.0
echo wordcloud==1.9.2
echo tqdm==4.66.1
echo rich==13.7.0
echo colorama==0.4.6
echo diskcache==5.6.3
echo fake-useragent==1.4.0
echo psutil==5.9.6
) > requirements.txt

echo [OK] requirements.txt created

REM Create README file
(
echo # YouTube Analyzer - Successfully Installed!
echo.
echo ## Quick Start
echo.
echo 1. Double-click `QUICK_START.bat`
echo 2. Select "Run competitor analysis"
echo 3. Enter your product/service description
echo 4. Wait for results in `reports\` folder
echo.
echo ## Configuration
echo.
echo - Edit `.env` file for advanced settings
echo - Add YouTube API key for better stability
echo - Configure cookies.txt for bypassing blocks
echo.
echo ## Structure
echo.
echo - `reports\` - Excel reports with results
echo - `logs\` - execution logs
echo - `data\` - intermediate data
echo - `.env` - configuration
echo.
echo Installation date: %date% %time%
) > README.md

echo [OK] README.md created

REM Check installation
echo.
echo [STEP] Checking installation...
python -c "
import sys
print(f'Python: {sys.version}')

packages = ['requests', 'pandas', 'yt_dlp', 'openpyxl', 'nltk']
missing = []

for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'[OK] {pkg}')
    except ImportError:
        missing.append(pkg)
        print(f'[ERROR] {pkg}')

if not missing:
    print('')
    print('[SUCCESS] All components installed successfully!')
else:
    print(f'')
    print(f'[WARNING] Missing: {missing}')
"

REM Create desktop shortcut
echo.
echo [STEP] Creating desktop shortcut...
powershell -Command "
try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\YouTube Analyzer.lnk')
    $Shortcut.TargetPath = 'C:\youtube-analyzer\QUICK_START.bat'
    $Shortcut.WorkingDirectory = 'C:\youtube-analyzer'
    $Shortcut.Description = 'YouTube Competitor Analysis Tool'
    $Shortcut.Save()
    Write-Host '[OK] Desktop shortcut created'
} catch {
    Write-Host '[WARNING] Could not create shortcut'
}
"

REM Register in Start Menu
echo.
echo [STEP] Registering in Start Menu...
mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\YouTube Analyzer" 2>nul
powershell -Command "
try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\YouTube Analyzer\YouTube Analyzer.lnk')
    $Shortcut.TargetPath = 'C:\youtube-analyzer\QUICK_START.bat'
    $Shortcut.WorkingDirectory = 'C:\youtube-analyzer'
    $Shortcut.Save()
    Write-Host '[OK] Added to Start Menu'
} catch {
    Write-Host '[WARNING] Could not register in Start Menu'
}
"

echo.
echo ===============================================================================
echo [SUCCESS] INSTALLATION COMPLETED SUCCESSFULLY!
echo ===============================================================================
echo.
echo YouTube Analyzer is ready to use!
echo.
echo Location: C:\youtube-analyzer\
echo Launch: Desktop shortcut or Start Menu
echo Configuration: .env file
echo Documentation: README.md
echo.
echo NEXT STEPS:
echo.
echo 1. RECOMMENDED: Get YouTube API key
echo    - Go to https://console.cloud.google.com/
echo    - Enable YouTube Data API v3
echo    - Create API Key
echo    - Add to .env file: YOUTUBE_API_KEY=your_key
echo.
echo 2. For access issues: Configure cookies
echo    - Install "Get cookies.txt" browser extension
echo    - Export cookies from youtube.com
echo    - Save as C:\youtube-analyzer\cookies.txt
echo.
echo 3. START ANALYSIS:
echo    - Double-click "YouTube Analyzer" desktop shortcut
echo    - OR run QUICK_START.bat
echo    - OR find in Start Menu
echo.
echo Results will be saved in C:\youtube-analyzer\reports\
echo.
echo ===============================================================================
echo.
echo USEFUL COMMANDS:
echo.
echo Run analysis:     QUICK_START.bat
echo Settings:         notepad .env
echo View reports:     explorer reports
echo Logs:             type logs\youtube_analysis.log
echo Update:           pip install --upgrade -r requirements.txt
echo.
echo ===============================================================================

REM Offer to launch immediately
echo.
set /p launch="Launch YouTube Analyzer now? (y/n): "
if /i "%launch%"=="y" (
    if exist "QUICK_START.bat" (
        start "" "QUICK_START.bat"
    ) else (
        echo [WARNING] QUICK_START.bat not found
        echo Please download all project files from GitHub
    )
)

echo.
echo [SUCCESS] Installation complete! Welcome to YouTube Analyzer!
echo.
pause