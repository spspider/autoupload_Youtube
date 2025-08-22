@echo off
echo 🎵 Starting TikTok Auto Upload...

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run setup first:
    echo    python -m venv .venv
    echo    .venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate

REM Check if cookies.txt exists
if not exist "cookies.txt" (
    echo ❌ cookies.txt not found!
    echo 📋 Please create cookies.txt file with your TikTok session cookies
    echo    1. Login to TikTok in your browser
    echo    2. Export cookies using browser extension or developer tools
    echo    3. Save as 'cookies.txt' in the project root
    pause
    exit /b 1
)

REM Run TikTok upload script
echo 🚀 Starting TikTok upload process...
python upload_tiktok.py

echo ✅ TikTok upload process completed!
pause