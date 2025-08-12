#!/bin/bash

# AiTalkDual Web Interface Launcher Script

echo "🤖 AiTalkDual Web Interface"
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    echo "✗ web_app.py not found. Please run this script from the AiTalkDual directory."
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
python3 -c "import fastapi, uvicorn, ollama" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ Missing dependencies. Installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "✗ Failed to install dependencies. Please run: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Check if Ollama is running
echo "Checking Ollama service..."
python3 -c "import ollama; ollama.list()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Ollama service not running. Please start it with: ollama serve"
    echo "Continuing anyway..."
fi

echo ""
echo "🚀 Starting web server..."
echo "Web interface will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo "=========================="

# Start the web server (using 127.0.0.1 for security and browser compatibility)
python3 -m uvicorn web_app:app --host 127.0.0.1 --port 8000 --reload
