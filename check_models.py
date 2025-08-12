#!/usr/bin/env python3
"""
Test script to check Ollama installation and available models
"""

import sys

def test_ollama_connection():
    """Test if we can connect to Ollama and list models"""
    try:
        import ollama
        print("✓ Ollama Python package found")
        
        # Try to connect to Ollama service
        models = ollama.list()
        print(f"✓ Connected to Ollama service")
        
        if models and 'models' in models:
            model_list = models['models']
            print(f"✓ Found {len(model_list)} models:")
            for model in model_list:
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                size_gb = size / (1024**3) if size > 0 else 0
                print(f"  - {name} ({size_gb:.1f}GB)")
        else:
            print("⚠️  No models found")
            print("You can download models with: ollama pull model-name")
            print("Popular models: qwen2:1.5b, llama3.2:1b, mistral")
        
        return True
        
    except ImportError:
        print("✗ Ollama Python package not found")
        print("Install with: pip install ollama")
        return False
        
    except Exception as e:
        print(f"✗ Cannot connect to Ollama service: {e}")
        print("\nTroubleshooting:")
        print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Start Ollama service: ollama serve")
        print("3. Download a model: ollama pull qwen2:1.5b")
        return False

def main():
    print("🤖 AiTalkDual - Ollama Model Check")
    print("=" * 40)
    
    success = test_ollama_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Ready to use AiTalkDual!")
        print("Your existing models will be available in the web interface.")
    else:
        print("❌ Setup needed before using AiTalkDual")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
