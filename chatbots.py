import ollama
import time
import sys

# --- 配置区 ---
# 你可以在这里更换你已经下载好的任何模型
MODEL_1_NAME = 'qwen2:7b'
MODEL_2_NAME = 'deepseek-r1:latest'

# 对话的初始话题
STARTING_PROMPT = "你好，我们来玩一个角色扮演游戏。你是一个经验丰富的宇航员，我是一个对太空充满好奇的高中生。请你先开始，向我介绍一下你第一次进入太空时的感受。"

# 对话进行的轮数
CONVERSATION_TURNS = 4

# 打字机效果的速度（秒/字符），数值越小速度越快
TYPEWRITER_SPEED = 0.03 
# --- 配置区结束 ---


def stream_to_terminal(text, speed):
    """
    以打字机效果将文本逐字输出到终端。
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print() # 打印换行符


def main():
    """
    主函数，运行两个模型的对话。
    """
    print("="*50)
    print(f"🤖 模型1: {MODEL_1_NAME}")
    print(f"🤖 模型2: {MODEL_2_NAME}")
    print(f"💬 初始话题: {STARTING_PROMPT}")
    print("="*50)
    print("\n对话开始...\n")
    time.sleep(2)

    # 为每个模型维护独立的对话历史，这对于保持上下文至关重要
    model_1_messages = []
    model_2_messages = []

    # 使用初始话题启动对话
    # 模型1作为对话的发起者
    current_prompt = STARTING_PROMPT
    
    try:
        # 进行指定轮数的对话
        for i in range(CONVERSATION_TURNS):
            
            # --- 模型1的回合 ---
            print(f"\n--- 第 {i+1} 轮 | {MODEL_1_NAME} 正在思考... ---\n")
            stream_to_terminal(f"👨‍🚀 {MODEL_1_NAME}:", TYPEWRITER_SPEED)
            
            # 将当前提示加入模型1的历史记录
            model_1_messages.append({'role': 'user', 'content': current_prompt})
            
            # 调用Ollama API
            response_1 = ollama.chat(model=MODEL_1_NAME, messages=model_1_messages)
            response_1_content = response_1['message']['content']
            
            # 以打字机效果显示回应
            stream_to_terminal(response_1_content, TYPEWRITER_SPEED)
            
            # 将模型1自己的回答加入其历史（作为'assistant'角色）
            model_1_messages.append({'role': 'assistant', 'content': response_1_content})
            
            # 将模型1的回应作为给模型2的新提示
            current_prompt = response_1_content
            
            time.sleep(1) # 在模型切换间稍作停顿

            # --- 模型2的回合 ---
            print(f"\n--- 第 {i+1} 轮 | {MODEL_2_NAME} 正在思考... ---\n")
            stream_to_terminal(f"🧑‍🎓 {MODEL_2_NAME}:", TYPEWRITER_SPEED)
            
            # 将当前提示加入模型2的历史记录
            model_2_messages.append({'role': 'user', 'content': current_prompt})
            
            # 调用Ollama API
            response_2 = ollama.chat(model=MODEL_2_NAME, messages=model_2_messages)
            response_2_content = response_2['message']['content']

            # 以打字机效果显示回应
            stream_to_terminal(response_2_content, TYPEWRITER_SPEED)

            # 将模型2自己的回答加入其历史
            model_2_messages.append({'role': 'assistant', 'content': response_2_content})

            # 将模型2的回应作为给模型1的新提示
            current_prompt = response_2_content
            
            time.sleep(1)

    except Exception as e:
        print(f"\n\n程序出错: {e}")
        print("请确保Ollama服务正在运行，并且模型名称正确。")

    print("\n\n" + "="*50)
    print("对话结束。")
    print("="*50)


if __name__ == "__main__":
    main()