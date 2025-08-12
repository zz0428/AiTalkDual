#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot AiTalkDual connection issues
"""

import sys
import subprocess
import platform

def check_ollama_installation():
    """Check if Ollama is installed"""
    print("🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Ollama installed: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ Ollama command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Ollama command not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Ollama command timed out")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama: {e}")
        return False

def check_ollama_service():
    """Check if Ollama service is running"""
    print("\n🔍 Checking Ollama service...")
    
    try:
        # Try to list models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Ollama service is running")
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Header + models
                print(f"✓ Found {len(lines)-1} model(s):")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        print(f"  - {line.split()[0]}")
            else:
                print("⚠️  No models installed")
                print("  Install models with: ollama pull model-name")
            return True
        else:
            print(f"✗ Ollama service not responding: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Ollama command not found")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Ollama service timeout - may not be running")
        return False
    except Exception as e:
        print(f"✗ Error checking Ollama service: {e}")
        return False

def check_python_ollama():
    """Check if Python ollama package can connect"""
    print("\n🔍 Checking Python ollama package...")
    
    try:
        import ollama
        print("✓ Python ollama package imported")
        
        # Try to connect
        models = ollama.list()
        print("✓ Connected to Ollama via Python")
        
        if models and 'models' in models:
            model_list = models['models']
            print(f"✓ Found {len(model_list)} model(s) via Python:")
            for model in model_list:
                name = model.get('name', 'Unknown')
                print(f"  - {name}")
        else:
            print("⚠️  No models found via Python")
        
        return True
        
    except ImportError:
        print("✗ Python ollama package not installed")
        print("  Install with: pip install ollama")
        return False
    except Exception as e:
        print(f"✗ Python ollama connection failed: {e}")
        print("  This usually means Ollama service is not running")
        return False

def check_web_server():
    """Check if web server dependencies are available"""
    print("\n🔍 Checking web server dependencies...")
    
    try:
        import fastapi
        print("✓ FastAPI available")
    except ImportError:
        print("✗ FastAPI not installed")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn available")
    except ImportError:
        print("✗ Uvicorn not installed")
        return False
    
    try:
        import jinja2
        print("✓ Jinja2 available")
    except ImportError:
        print("✗ Jinja2 not installed")
        return False
    
    return True

def provide_solutions():
    """Provide solutions based on what's missing"""
    print("\n🔧 SOLUTIONS:")
    print("=" * 50)
    
    print("\n1. Install Ollama (if not installed):")
    if platform.system() == "Darwin":  # macOS
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   # OR download from: https://ollama.ai")
    else:
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
    
    print("\n2. Start Ollama service:")
    print("   ollama serve")
    print("   # Run this in a separate terminal and keep it running")
    
    print("\n3. Install some models:")
    print("   ollama pull qwen2:1.5b")
    print("   ollama pull llama3.2:1b")
    print("   ollama pull mistral")
    
    print("\n4. Install Python dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n5. Test the setup:")
    print("   python3 check_models.py")

def main():
    print("🤖 AiTalkDual Connection Diagnostic")
    print("=" * 50)
    
    ollama_installed = check_ollama_installation()
    ollama_running = check_ollama_service() if ollama_installed else False
    python_works = check_python_ollama()
    web_deps = check_web_server()
    
    print("\n📊 SUMMARY:")
    print("=" * 50)
    print(f"Ollama installed: {'✓' if ollama_installed else '✗'}")
    print(f"Ollama service running: {'✓' if ollama_running else '✗'}")
    print(f"Python ollama works: {'✓' if python_works else '✗'}")
    print(f"Web dependencies: {'✓' if web_deps else '✗'}")
    
    if all([ollama_installed, ollama_running, python_works, web_deps]):
        print("\n🎉 Everything looks good! AiTalkDual should work.")
    else:
        provide_solutions()

if __name__ == "__main__":
    main()
