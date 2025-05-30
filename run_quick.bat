@echo off
title YouTube Analyzer - Quick Run
echo.
echo ========================================
echo YouTube Analyzer - Quick Run
echo ========================================
echo.

REM Go to project directory
cd /d "C:\youtube-analyzer"

REM Check if project files exist
if not exist "main.py" (
    echo ERROR: main.py not found!
    echo.
    echo Please download project files from GitHub:
    echo 1. Go to your GitHub repository
    echo 2. Download main.py, config.py, src\analyzer.py
    echo 3. Place them in C:\youtube-analyzer\
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run simple_install.bat first
    pause
    exit /b 1
)

echo OK: Project files found
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check .env file
if not exist ".env" (
    echo WARNING: .env file not found, creating basic one...
    (
    echo YOUTUBE_API_KEY=
    echo MAX_TOTAL_VIDEOS=50
    echo MAX_CHANNELS_TO_ANALYZE=20
    echo MAX_WORKERS=4
    echo LOG_LEVEL=INFO
    echo ENABLE_TRANSCRIPT_EXTRACTION=true
    echo ENABLE_CONTENT_ANALYSIS=true
    echo EXCEL_OUTPUT_ENABLED=true
    ) > .env
    echo OK: Basic .env file created
)

echo.
echo YOUTUBE COMPETITOR ANALYSIS
echo.

REM Get offer from user
set /p offer="Enter your offer (product/service description): "

if "%offer%"=="" (
    echo ERROR: Offer cannot be empty!
    pause
    exit /b 1
)

echo.
echo Analysis options:
echo 1. Quick (25 videos, 15 channels, no transcripts) - ~5 minutes
echo 2. Standard (50 videos, 20 channels) - ~15 minutes
echo 3. Detailed (100 videos, 30 channels) - ~30 minutes
echo 4. Custom settings
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    set params=--max-videos 25 --max-channels 15 --no-transcripts --parallel 6
    echo Selected: Quick analysis
) else if "%choice%"=="2" (
    set params=--max-videos 50 --max-channels 20 --parallel 4
    echo Selected: Standard analysis
) else if "%choice%"=="3" (
    set params=--max-videos 100 --max-channels 30 --parallel 6
    echo Selected: Detailed analysis
) else if "%choice%"=="4" (
    echo.
    set /p max_videos="Max videos (default 50): "
    set /p max_channels="Max channels (default 20): "
    set /p parallel="Parallel threads (default 4): "
    
    if "%max_videos%"=="" set max_videos=50
    if "%max_channels%"=="" set max_channels=20
    if "%parallel%"=="" set parallel=4
    
    set params=--max-videos %max_videos% --max-channels %max_channels% --parallel %parallel%
    echo Selected: Custom settings
) else (
    set params=--max-videos 50 --max-channels 20
    echo Selected: Default settings
)

REM Additional keywords
echo.
set /p keywords="Additional keywords (comma-separated, optional): "
if not "%keywords%"=="" set params=%params% --keywords "%keywords%"

echo.
echo Starting analysis...
echo Offer: %offer%
echo Parameters: %params%
echo.
echo This may take several minutes. Do not close this window!
echo.

REM Run analysis
python main.py --offer "%offer%" %params%

set result=%errorlevel%

echo.
if %result% equ 0 (
    echo ========================================
    echo ANALYSIS COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Results saved to: C:\youtube-analyzer\reports\
    echo.
    echo Created reports:
    dir reports\*.xlsx /b 2>nul
    echo.
    echo Open reports folder? (y/n): 
    set /p open_folder=""
    if /i "%open_folder%"=="y" explorer reports
) else (
    echo ========================================
    echo ANALYSIS COMPLETED WITH ERRORS
    echo ========================================
    echo.
    echo Check log file: C:\youtube-analyzer\logs\youtube_analysis.log
    echo.
    echo Common solutions:
    echo - Add YouTube API key to .env file
    echo - Add cookies.txt file for access issues
    echo - Reduce number of videos: --max-videos 25
    echo - Check internet connection
)

echo.
echo ========================================
echo USEFUL COMMANDS:
echo.
echo Run again:        run_quick.bat
echo Manual run:       python main.py --offer "Your offer"
echo View logs:        type logs\youtube_analysis.log
echo Edit settings:    notepad .env
echo Clear cache:      rmdir /s /q .cache
echo.
echo ========================================

pause