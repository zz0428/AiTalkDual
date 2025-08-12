#!/usr/bin/env python3
"""
Quick launcher for AiTalkDual Web Interface
This script starts the web server with optimal settings.
"""

import sys
import os
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import ollama
        print("✓ All dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("pip install -r requirements.txt")
        return False

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        import ollama
        models = ollama.list()
        print(f"✓ Ollama is running with {len(models['models'])} models")
        return True
    except Exception as e:
        print(f"✗ Ollama service not available: {e}")
        print("\nPlease start Ollama service:")
        print("ollama serve")
        return False

def main():
    print("🤖 AiTalkDual Web Interface Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("web_app.py").exists():
        print("✗ web_app.py not found. Please run this script from the AiTalkDual directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama_service():
        print("\nContinuing anyway - you can start Ollama later...")
        time.sleep(2)
    
    print("\n🚀 Starting web server...")
    print("Web interface will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the server
    try:
        # Try to open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open("http://localhost:8000")
            except:
                pass
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start the server
        import uvicorn
        uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n✗ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
