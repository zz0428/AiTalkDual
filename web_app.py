"""
AiTalkDual Web Interface
A modern web UI for the AI conversation simulator using FastAPI and Server-Sent Events.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import ollama
import json
import asyncio
import uuid
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AiTalkDual", description="AI Conversation Simulator")

# Add CORS headers manually since fastapi.middleware.cors might not be available
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Store active conversations
active_conversations: Dict[str, dict] = {}

class ConversationConfig(BaseModel):
    model1: str = "qwen2:1.5b"
    model2: str = "llama3.2:1b"
    starting_prompt: str = "你好，我们来玩一个角色扮演游戏。你是一个经验丰富的宇航员，我是一个对太空充满好奇的高中生。请你先开始，向我介绍一下你第一次进入太空时的感受。"
    turns: int = 4
    typing_speed: float = 50.0  # chars per second

class ChatMessage(BaseModel):
    role: str  # 'model1', 'model2', 'system'
    content: str
    model_name: str
    timestamp: float
    turn: int

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/models")
async def get_available_models():
    """Get list of available Ollama models"""
    try:
        # Get models from Ollama
        models_response = ollama.list()
        
        # Check if we got a valid response
        if not models_response:
            return {"models": [], "error": "No models found. Please install models with 'ollama pull model-name'"}
        
        # Handle Pydantic response object - it has a 'models' attribute
        if hasattr(models_response, 'models'):
            models_array = models_response.models
        elif isinstance(models_response, dict) and 'models' in models_response:
            models_array = models_response['models']
        else:
            return {"models": [], "error": "No models found. Please install models with 'ollama pull model-name'"}
        
        model_list = []
        
        for model in models_array:
            # Handle Pydantic model objects and dicts
            if hasattr(model, 'model'):
                # Pydantic object with 'model' attribute
                name = model.model
            elif isinstance(model, dict):
                # Dictionary object
                name = (model.get('model') or 
                       model.get('name') or 
                       model.get('id') or 
                       'Unknown')
            elif isinstance(model, str):
                # String object
                name = model
            else:
                continue
            
            model_info = {
                "name": name,
                "size": getattr(model, 'size', 0) if hasattr(model, 'size') else (model.get('size', 0) if isinstance(model, dict) else 0),
                "modified_at": str(getattr(model, 'modified_at', '')) if hasattr(model, 'modified_at') else (model.get('modified_at', '') if isinstance(model, dict) else '')
            }
                
            model_list.append(model_info)
        
        # Sort models alphabetically by name
        model_list.sort(key=lambda x: x['name'])
        
        # Extract just the names for the frontend
        model_names = [model['name'] for model in model_list if model['name'] != 'Unknown']
        
        if not model_names:
            return {"models": [], "error": "No valid models found. Please install models with 'ollama pull model-name'"}
        
        return {
            "models": model_names,
            "model_details": model_list
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error getting models: {error_msg}")
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return {"models": [], "error": "Cannot connect to Ollama service. Please start Ollama with 'ollama serve'"}
        else:
            return {"models": [], "error": f"Ollama error: {error_msg}"}

@app.post("/api/conversation/start")
async def start_conversation(config: ConversationConfig):
    """Start a new conversation"""
    conversation_id = str(uuid.uuid4())
    
    # Validate models exist
    try:
        available_models = ollama.list()
        available_names = [model['name'] for model in available_models['models']]
        
        if config.model1 not in available_names:
            raise HTTPException(status_code=400, detail=f"Model {config.model1} not found")
        if config.model2 not in available_names:
            raise HTTPException(status_code=400, detail=f"Model {config.model2} not found")
    except Exception as e:
        logger.error(f"Error validating models: {e}")
        # Continue anyway, let Ollama handle the error
    
    # Store conversation state
    active_conversations[conversation_id] = {
        "config": config.dict(),
        "model1_messages": [],
        "model2_messages": [],
        "current_turn": 0,
        "current_prompt": config.starting_prompt,
        "is_running": False
    }
    
    return {"conversation_id": conversation_id}

@app.get("/api/conversation/{conversation_id}/stream")
async def stream_conversation(conversation_id: str):
    """Stream the conversation using Server-Sent Events"""
    logger.info(f"Starting stream for conversation {conversation_id}")
    
    if conversation_id not in active_conversations:
        logger.error(f"Conversation {conversation_id} not found")
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = active_conversations[conversation_id]
    
    if conversation["is_running"]:
        logger.warning(f"Conversation {conversation_id} already running")
        raise HTTPException(status_code=409, detail="Conversation already running")
    
    conversation["is_running"] = True
    
    async def generate_conversation():
        try:
            config = ConversationConfig(**conversation["config"])
            current_prompt = conversation["current_prompt"]
            
            yield f"data: {json.dumps({'type': 'start', 'message': 'Conversation started'})}\n\n"
            
            for turn in range(config.turns):
                conversation["current_turn"] = turn + 1
                
                # Model 1's turn
                yield f"data: {json.dumps({'type': 'thinking', 'model': config.model1, 'turn': turn + 1})}\n\n"
                
                try:
                    # Add to model 1's history
                    conversation["model1_messages"].append({'role': 'user', 'content': current_prompt})
                    
                    # Get response from model 1
                    response_1 = ollama.chat(model=config.model1, messages=conversation["model1_messages"])
                    response_1_content = response_1['message']['content']
                    
                    # Add model 1's response to its history
                    conversation["model1_messages"].append({'role': 'assistant', 'content': response_1_content})
                    
                    # Stream the response with typing effect
                    yield f"data: {json.dumps({'type': 'message_start', 'model': config.model1, 'turn': turn + 1})}\n\n"
                    
                    # Simulate typing by sending chunks
                    chunk_size = max(1, int(config.typing_speed / 10))  # Adjust chunk size based on speed
                    for i in range(0, len(response_1_content), chunk_size):
                        chunk = response_1_content[i:i+chunk_size]
                        yield f"data: {json.dumps({'type': 'message_chunk', 'content': chunk, 'model': config.model1})}\n\n"
                        await asyncio.sleep(chunk_size / config.typing_speed)
                    
                    yield f"data: {json.dumps({'type': 'message_end', 'model': config.model1})}\n\n"
                    
                    current_prompt = response_1_content
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error with model 1: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Error with {config.model1}: {str(e)}'})}\n\n"
                    break
                
                # Model 2's turn
                yield f"data: {json.dumps({'type': 'thinking', 'model': config.model2, 'turn': turn + 1})}\n\n"
                
                try:
                    # Add to model 2's history
                    conversation["model2_messages"].append({'role': 'user', 'content': current_prompt})
                    
                    # Get response from model 2
                    response_2 = ollama.chat(model=config.model2, messages=conversation["model2_messages"])
                    response_2_content = response_2['message']['content']
                    
                    # Add model 2's response to its history
                    conversation["model2_messages"].append({'role': 'assistant', 'content': response_2_content})
                    
                    # Stream the response with typing effect
                    yield f"data: {json.dumps({'type': 'message_start', 'model': config.model2, 'turn': turn + 1})}\n\n"
                    
                    # Simulate typing by sending chunks
                    chunk_size = max(1, int(config.typing_speed / 10))
                    for i in range(0, len(response_2_content), chunk_size):
                        chunk = response_2_content[i:i+chunk_size]
                        yield f"data: {json.dumps({'type': 'message_chunk', 'content': chunk, 'model': config.model2})}\n\n"
                        await asyncio.sleep(chunk_size / config.typing_speed)
                    
                    yield f"data: {json.dumps({'type': 'message_end', 'model': config.model2})}\n\n"
                    
                    current_prompt = response_2_content
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error with model 2: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Error with {config.model2}: {str(e)}'})}\n\n"
                    break
            
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Conversation completed'})}\n\n"
            
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            conversation["is_running"] = False
    
    return StreamingResponse(generate_conversation(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Cache-Control"
    })

@app.delete("/api/conversation/{conversation_id}")
async def stop_conversation(conversation_id: str):
    """Stop and delete a conversation"""
    if conversation_id in active_conversations:
        active_conversations[conversation_id]["is_running"] = False
        del active_conversations[conversation_id]
        return {"message": "Conversation stopped"}
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/api/conversation/{conversation_id}/status")
async def get_conversation_status(conversation_id: str):
    """Get the current status of a conversation"""
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = active_conversations[conversation_id]
    return {
        "is_running": conversation["is_running"],
        "current_turn": conversation["current_turn"],
        "total_turns": conversation["config"]["turns"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
