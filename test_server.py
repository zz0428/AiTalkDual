#!/usr/bin/env python3
"""
Simple test server to verify basic functionality
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def home():
    return HTMLResponse("""
    <html>
        <head><title>AiTalkDual Test</title></head>
        <body>
            <h1>🤖 AiTalkDual Test Server</h1>
            <p>If you can see this, the web server is working!</p>
            <button onclick="testOllama()">Test Ollama Connection</button>
            <div id="result"></div>
            
            <script>
                async function testOllama() {
                    try {
                        const response = await fetch('/test-ollama');
                        const data = await response.json();
                        document.getElementById('result').innerHTML = 
                            '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    } catch (error) {
                        document.getElementById('result').innerHTML = 
                            '<p style="color: red;">Error: ' + error.message + '</p>';
                    }
                }
            </script>
        </body>
    </html>
    """)

@app.get("/test-ollama")
async def test_ollama():
    try:
        import ollama
        models = ollama.list()
        return {
            "status": "success", 
            "models": [m['name'] for m in models.get('models', [])]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("🚀 Starting test server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
