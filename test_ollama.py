#!/usr/bin/env python3

print("Testing Ollama connection...")

try:
    import ollama
    print("SUCCESS: ollama package imported")
    
    models = ollama.list()
    print("SUCCESS: Connected to Ollama service")
    print(f"Models found: {len(models.get('models', []))}")
    
    for model in models.get('models', []):
        print(f"  - {model.get('name', 'Unknown')}")
        
except ImportError as e:
    print(f"ERROR: ollama package not found: {e}")
except Exception as e:
    print(f"ERROR: Cannot connect to Ollama: {e}")
    print("SOLUTION: Start Ollama service with: ollama serve")
