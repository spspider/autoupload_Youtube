#!/bin/bash

# TikTok Auto Upload Starter Script
echo "🎵 Starting TikTok Auto Upload..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python -m venv .venv"
    echo "   .venv\\Scripts\\activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/Scripts/activate

# Check if cookies.txt exists
if [ ! -f "cookies.txt" ]; then
    echo "❌ cookies.txt not found!"
    echo "📋 Please create cookies.txt file with your TikTok session cookies"
    echo "   1. Login to TikTok in your browser"
    echo "   2. Export cookies using browser extension or developer tools"
    echo "   3. Save as 'cookies.txt' in the project root"
    exit 1
fi

# Run TikTok upload script
echo "🚀 Starting TikTok upload process..."
python upload_tiktok.py

echo "✅ TikTok upload process completed!"