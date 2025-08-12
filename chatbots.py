import ollama
import time
import sys

# --- Improved Configuration ---
# Separate context prompts for each model - they don't know about each other!

# Model 1: Gets a natural conversation starter without knowing it's talking to AI
MODEL_1_NAME = 'qwen2:1.5b'
MODEL_1_CONTEXT = """You are an experienced astronaut who has just returned from a mission to the International Space Station. You're feeling excited and want to share your experiences with someone. Start by telling them about the most amazing moment during your recent space mission."""

# Model 2: Gets a different context that makes them seem like a curious person
MODEL_2_NAME = 'llama3.2:1b'
MODEL_2_CONTEXT = """You are a curious high school student who is fascinated by space and science. You just met someone who seems to have interesting stories about space. You're eager to learn and ask thoughtful questions about their experiences."""

# Conversation settings
CONVERSATION_TURNS = 4
TYPEWRITER_SPEED = 0.05
# --- Configuration End ---


def stream_to_terminal(text, speed):
    """以打字机效果将文本逐字输出到终端"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def initialize_model_context(model_name, context_prompt):
    """Initialize a model with its own private context without revealing the conversation structure"""
    messages = [{'role': 'system', 'content': context_prompt}]
    
    # Get the model's natural opening based on their context
    response = ollama.chat(model=model_name, messages=messages)
    opening_message = response['message']['content']
    
    # Update history to include the opening
    messages.append({'role': 'assistant', 'content': opening_message})
    
    return messages, opening_message


def main():
    """运行改进的双AI对话，不让模型知道对方是AI"""
    print("="*50)
    print(f"🤖 模型1: {MODEL_1_NAME} (Astronaut)")
    print(f"🤖 模型2: {MODEL_2_NAME} (Student)")
    print("💬 Independent contexts - models don't know they're talking to AI!")
    print("="*50)
    print("\n初始化模型上下文...\n")
    
    try:
        # Initialize each model with their own private context
        print("Setting up Model 1 context...")
        model_1_messages, model_1_opening = initialize_model_context(MODEL_1_NAME, MODEL_1_CONTEXT)
        
        print("Setting up Model 2 context...")
        model_2_messages, _ = initialize_model_context(MODEL_2_NAME, MODEL_2_CONTEXT)
        
        print("\n对话开始...\n")
        time.sleep(2)
        
        # Start conversation with Model 1's natural opening
        print(f"--- 第 1 轮 | {MODEL_1_NAME} 开始对话 ---\n")
        stream_to_terminal(f"👨‍🚀 {MODEL_1_NAME}: {model_1_opening}", TYPEWRITER_SPEED)
        
        # This becomes the first message for Model 2 (without revealing it came from AI)
        current_prompt = model_1_opening
        
        # Continue conversation
        for i in range(CONVERSATION_TURNS):
            time.sleep(1)
            
            # --- Model 2's turn ---
            print(f"\n--- 第 {i+1} 轮 | {MODEL_2_NAME} 正在思考... ---\n")
            stream_to_terminal(f"🧑‍🎓 {MODEL_2_NAME}:", TYPEWRITER_SPEED)
            
            # Model 2 receives the message as if from a human conversation partner
            model_2_messages.append({'role': 'user', 'content': current_prompt})
            
            response_2 = ollama.chat(model=MODEL_2_NAME, messages=model_2_messages)
            response_2_content = response_2['message']['content']
            
            stream_to_terminal(response_2_content, TYPEWRITER_SPEED)
            model_2_messages.append({'role': 'assistant', 'content': response_2_content})
            
            current_prompt = response_2_content
            time.sleep(1)
            
            if i < CONVERSATION_TURNS - 1:  # Don't do Model 1's turn on the last iteration
                # --- Model 1's turn ---
                print(f"\n--- 第 {i+2} 轮 | {MODEL_1_NAME} 正在思考... ---\n")
                stream_to_terminal(f"👨‍🚀 {MODEL_1_NAME}:", TYPEWRITER_SPEED)
                
                # Model 1 receives the message as if from a human conversation partner
                model_1_messages.append({'role': 'user', 'content': current_prompt})
                
                response_1 = ollama.chat(model=MODEL_1_NAME, messages=model_1_messages)
                response_1_content = response_1['message']['content']
                
                stream_to_terminal(response_1_content, TYPEWRITER_SPEED)
                model_1_messages.append({'role': 'assistant', 'content': response_1_content})
                
                current_prompt = response_1_content

    except Exception as e:
        print(f"\n\n程序出错: {e}")
        print("请确保Ollama服务正在运行，并且模型名称正确。")

    print("\n\n" + "="*50)
    print("对话结束。")
    print("="*50)


if __name__ == "__main__":
    main()