# AiTalkDual 🤖💬

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.ai)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI conversation simulator that enables two different AI models to have automated conversations with each other using Ollama. Watch as AI models engage in dynamic dialogues with role-playing scenarios, complete with realistic typewriter effects.

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/zz0428/AiTalkDual.git
cd AiTalkDual
pip install -r requirements.txt

# 2. Install Ollama and models (if not already done)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull qwen2:1.5b
ollama pull llama3.2:1b

# 3. Start the web interface
python web_app.py

# 4. Open http://localhost:8000 in your browser
```

## ✨ Features

- **🌐 Modern Web Interface**: Beautiful, responsive web UI with real-time chat experience
- **⌨️ Terminal Interface**: Classic command-line version for power users
- **🤖 Multi-Model Support**: Automatically detects and supports all available Ollama models
- **🎭 Role-playing Scenarios**: Configurable conversation themes and character roles
- **💬 Real-time Streaming**: Live conversation updates with Server-Sent Events
- **🧠 Context Management**: Independent conversation history maintained for each model
- **⚙️ Highly Customizable**: Easy configuration through web forms or code editing
- **🔄 Turn-based Dialogue**: Structured conversation flow with clear model identification
- **📊 Progress Tracking**: Visual indicators for conversation progress
- **📱 Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

## �️ Technology Stack

**Backend:**
- **FastAPI**: Modern, fast web framework for building APIs
- **Ollama**: Local AI model management and inference
- **Server-Sent Events**: Real-time communication for live conversations
- **Pydantic**: Data validation and settings management

**Frontend:**
- **Vanilla JavaScript**: Lightweight frontend with no framework dependencies
- **Modern CSS**: Responsive design with dark theme
- **HTML Templates**: Jinja2 templating for server-side rendering

**Core Features:**
- **Async/Await**: Non-blocking conversation handling
- **CORS Support**: Cross-origin resource sharing for development
- **Auto Model Detection**: Dynamic discovery of available Ollama models

## �📋 Requirements

- Python 3.7 or higher
- [Ollama](https://ollama.ai) installed and running
- AI models downloaded via Ollama (see installation section)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/zz0428/AiTalkDual.git
cd AiTalkDual
```

### 2. Install Python Dependencies
```bash
# Install all dependencies for both terminal and web interface
pip install -r requirements.txt

# Or install manually:
pip install ollama fastapi uvicorn jinja2 python-multipart
```

### 3. Install and Setup Ollama
If you haven't installed Ollama yet:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai)

### 4. Download AI Models
```bash
# Default models used in the application
ollama pull qwen2:1.5b
ollama pull llama3.2:1b

# Optional: Try other popular models
ollama pull mistral:7b
ollama pull gemma2:2b
ollama pull phi3:mini
ollama pull deepseek-r1:latest
ollama pull qwen2:7b
```

### 5. Start Ollama Service
```bash
ollama serve
```

## 📁 Project Structure

```
AiTalkDual/
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
├── chatbots.py           # Terminal-based conversation script
├── web_app.py            # FastAPI web application
├── templates/
│   └── index.html        # Web interface template
└── static/
    ├── style.css         # Web interface styling
    └── script.js         # Frontend JavaScript logic
```

## 🎯 Usage

### Web Interface (Recommended)
```bash
# Start the web application
python web_app.py

# Or use uvicorn directly for more control
uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload

# Open your browser and go to:
# http://localhost:8000
```

The web interface provides:
- 🌐 **Modern UI**: Clean, responsive design with real-time chat interface
- ⚙️ **Easy Configuration**: Web forms for all settings (no code editing needed)
- 🤖 **Auto Model Detection**: Automatically detects all available Ollama models
- 📊 **Progress Tracking**: Visual progress bars and status indicators
- 🎨 **Enhanced Visuals**: Color-coded models, typing animations, and chat bubbles
- 📱 **Mobile Friendly**: Works on all devices
- 🔄 **Server-Sent Events**: Real-time streaming conversations

### Terminal Version (Classic)
```bash
python chatbots.py
```

### Example Output (Web Interface)
The web interface provides a modern chat experience with:
- Color-coded AI models with avatars
- Real-time typing effects
- Progress tracking
- Easy configuration through web forms
- Mobile-responsive design

### Example Output (Terminal)
```
==================================================
🤖 模型1: qwen2:1.5b
🤖 模型2: llama3.2:1b
💬 初始话题: 你好，我们来玩一个角色扮演游戏...
==================================================

对话开始...

--- 第 1 轮 | qwen2:1.5b 正在思考... ---

👨‍🚀 qwen2:1.5b: 你好！作为一名经验丰富的宇航员，我很乐意与你分享...

--- 第 1 轮 | llama3.2:1b 正在思考... ---

🧑‍🎓 llama3.2:1b: 哇，太令人兴奋了！我一直梦想着能够...
```

## ⚙️ Configuration

### Web Interface Configuration
Simply open your browser to `http://localhost:8000` and use the intuitive web forms to:
- Select AI models from dropdown menus
- Edit conversation prompts in text areas
- Adjust conversation length and typing speed with sliders
- Start, stop, and monitor conversations in real-time

### Terminal Configuration
Edit the configuration section in `chatbots.py` to customize your experience:

```python
# 模型配置
MODEL_1_NAME = 'qwen2:1.5b'        # 第一个AI模型
MODEL_2_NAME = 'llama3.2:1b'       # 第二个AI模型

# 对话设置
STARTING_PROMPT = "你的初始对话主题"   # 对话的起始话题
CONVERSATION_TURNS = 4              # 对话轮数

# 显示效果
TYPEWRITER_SPEED = 0.05            # 打字机效果速度（秒/字符）
```

### Available Models
The web interface automatically detects all available Ollama models. Popular options include:
- `llama3.2:1b`, `llama3.2:3b`
- `qwen2:1.5b`, `qwen2:7b`
- `mistral:7b`, `mistral:latest`
- `phi3:mini`, `phi3:medium`
- `gemma2:2b`, `gemma2:9b`
- `deepseek-r1:latest`
- `codellama:7b`, `codellama:latest`

The application will show only the models you have actually downloaded via `ollama pull`.

### Conversation Themes
Customize `STARTING_PROMPT` for different scenarios:
- **Educational**: Teacher-student conversations
- **Creative**: Writer-editor collaborations
- **Technical**: Developer-architect discussions
- **Entertainment**: Character role-plays

## 🛠️ Troubleshooting

### Common Issues

**"Connection refused" or model not found:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Verify model is downloaded
ollama pull your-model-name
```

**Web interface shows "No models available":**
```bash
# Ensure Ollama is running and models are installed
ollama serve
ollama list

# Check if models are properly detected
curl http://localhost:11434/api/tags
```

**Slow responses:**
- Try smaller models (1b-3b parameters)
- Adjust typing speed in web interface
- Ensure sufficient system resources (RAM/CPU)

**Import errors:**
```bash
pip install --upgrade -r requirements.txt
```

## 📝 Example Scenarios

### 1. Space Exploration (Default)
Astronaut and curious student discussing space experiences.

### 2. Historical Debate
```python
STARTING_PROMPT = "Let's have a historical debate. You are Napoleon Bonaparte, I am a modern historian. Defend your military strategies."
```

### 3. Coding Review
```python
STARTING_PROMPT = "You are a senior developer, I'm a junior. Please review this Python function and suggest improvements: def hello(): print('world')"
```

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Ideas for Contributions
- Enhanced conversation templates and scenarios
- Conversation logging and export functionality
- Multiple conversation participants (3+ models)
- Voice synthesis integration
- Different conversation formats (debate, interview, etc.)
- Conversation analytics and insights
- Mobile app version
- Docker containerization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for providing the local AI model infrastructure
- The open-source AI community for developing amazing models
- Contributors and users who help improve this project

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an [Issue](https://github.com/zz0428/AiTalkDual/issues)
3. Join discussions in [Discussions](https://github.com/zz0428/AiTalkDual/discussions)

---

⭐ Star this repository if you found it helpful!
