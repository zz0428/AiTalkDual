#!/bin/bash

echo "🔍 Quick Ollama Test"
echo "==================="

# Test 1: Check if ollama command exists
if command -v ollama &> /dev/null; then
    echo "✓ Ollama command found"
    
    # Test 2: Check Ollama version
    echo "Version: $(ollama --version)"
    
    # Test 3: Check if service is running
    if ollama list &> /dev/null; then
        echo "✓ Ollama service is running"
        echo "Models installed:"
        ollama list
    else
        echo "✗ Ollama service not running"
        echo "Start with: ollama serve"
    fi
else
    echo "✗ Ollama not found"
    echo "Install from: https://ollama.ai"
fi

echo ""
echo "After fixing Ollama, refresh your web browser and try again."
