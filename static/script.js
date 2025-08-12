// AiTalkDual Web Interface JavaScript

class AiTalkDual {
    constructor() {
        this.conversationId = null;
        this.eventSource = null;
        this.isRunning = false;
        this.currentMessages = [];
        this.currentTurn = 0;
        this.totalTurns = 4;

        this.initializeElements();
        this.setupEventListeners();
        this.loadAvailableModels();
    }

    initializeElements() {
        // Config elements
        this.model1Select = document.getElementById('model1');
        this.model2Select = document.getElementById('model2');
        this.startingPromptTextarea = document.getElementById('startingPrompt');
        this.turnsInput = document.getElementById('turns');
        this.typingSpeedInput = document.getElementById('typingSpeed');
        this.speedValueSpan = document.getElementById('speedValue');

        // Control elements
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.clearBtn = document.getElementById('clearBtn');

        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.conversationStatus = document.getElementById('conversationStatus');
        this.progressBar = document.getElementById('progressBar');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');

        // Loading overlay
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    setupEventListeners() {
        // Control buttons
        this.startBtn.addEventListener('click', () => this.startConversation());
        this.stopBtn.addEventListener('click', () => this.stopConversation());
        this.clearBtn.addEventListener('click', () => this.clearMessages());

        // Typing speed slider
        this.typingSpeedInput.addEventListener('input', (e) => {
            this.speedValueSpan.textContent = e.target.value;
        });

        // Form validation
        this.startingPromptTextarea.addEventListener('input', () => this.validateForm());
        this.model1Select.addEventListener('change', () => this.validateForm());
        this.model2Select.addEventListener('change', () => this.validateForm());
    }

    async loadAvailableModels() {
        try {
            this.showLoading('Loading available models...');
            const response = await fetch('/api/models');
            const data = await response.json();
            
            // Clear existing options
            this.model1Select.innerHTML = '';
            this.model2Select.innerHTML = '';
            
            // Add model options
            data.models.forEach(model => {
                const option1 = new Option(model, model);
                const option2 = new Option(model, model);
                this.model1Select.add(option1);
                this.model2Select.add(option2);
            });
            
            // Set default selections if available
            if (data.models.includes('qwen2:1.5b')) {
                this.model1Select.value = 'qwen2:1.5b';
            }
            if (data.models.includes('llama3.2:1b')) {
                this.model2Select.value = 'llama3.2:1b';
            }
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading models:', error);
            this.hideLoading();
            this.showError('Failed to load models. Using defaults.');
        }
    }

    validateForm() {
        const model1 = this.model1Select.value;
        const model2 = this.model2Select.value;
        const prompt = this.startingPromptTextarea.value.trim();
        
        const isValid = model1 && model2 && prompt && !this.isRunning;
        this.startBtn.disabled = !isValid;
        
        if (model1 === model2) {
            this.showWarning('Warning: Same model selected for both participants.');
        }
        
        return isValid;
    }

    async startConversation() {
        if (!this.validateForm()) return;

        try {
            this.isRunning = true;
            this.updateControlButtons();
            this.clearMessages();

            const config = {
                model1: this.model1Select.value,
                model2: this.model2Select.value,
                starting_prompt: this.startingPromptTextarea.value.trim(),
                turns: parseInt(this.turnsInput.value),
                typing_speed: parseFloat(this.typingSpeedInput.value)
            };

            this.totalTurns = config.turns;
            this.currentTurn = 0;

            // Start conversation
            const response = await fetch('/api/conversation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.conversationId = data.conversation_id;

            // Start streaming
            this.startEventStream();

        } catch (error) {
            console.error('Error starting conversation:', error);
            this.showError(`Failed to start conversation: ${error.message}`);
            this.isRunning = false;
            this.updateControlButtons();
        }
    }

    startEventStream() {
        if (!this.conversationId) return;

        this.eventSource = new EventSource(`/api/conversation/${this.conversationId}/stream`);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleStreamEvent(data);
            } catch (error) {
                console.error('Error parsing stream data:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            this.showError('Connection error occurred');
            this.stopConversation();
        };
    }

    handleStreamEvent(data) {
        switch (data.type) {
            case 'start':
                this.updateStatus('Conversation started', 'active');
                this.showProgress();
                break;

            case 'thinking':
                this.showThinking(data.model, data.turn);
                break;

            case 'message_start':
                this.startMessage(data.model, data.turn);
                break;

            case 'message_chunk':
                this.appendToCurrentMessage(data.content);
                break;

            case 'message_end':
                this.endCurrentMessage();
                this.updateProgress();
                break;

            case 'complete':
                this.updateStatus('Conversation completed');
                this.hideProgress();
                this.isRunning = false;
                this.updateControlButtons();
                break;

            case 'error':
                this.showError(data.message);
                this.isRunning = false;
                this.updateControlButtons();
                break;
        }
    }

    showThinking(model, turn) {
        this.removeThinking();
        
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking-indicator';
        thinkingDiv.id = 'current-thinking';
        thinkingDiv.innerHTML = `
            <i class="fas fa-brain"></i>
            <span>${model} is thinking...</span>
            <div class="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.chatMessages.appendChild(thinkingDiv);
        this.scrollToBottom();
    }

    removeThinking() {
        const thinking = document.getElementById('current-thinking');
        if (thinking) {
            thinking.remove();
        }
    }

    startMessage(model, turn) {
        this.removeThinking();
        this.currentTurn = turn;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${model === this.model1Select.value ? 'model1' : 'model2'}`;
        messageDiv.id = 'current-message';
        
        const isModel1 = model === this.model1Select.value;
        const avatarClass = isModel1 ? 'model1' : 'model2';
        const avatarIcon = isModel1 ? '🤖' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="model-avatar ${avatarClass}">${avatarIcon}</div>
                <span class="model-name">${model}</span>
                <span class="turn-info">Turn ${turn}</span>
            </div>
            <div class="message-content" id="current-content"></div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    appendToCurrentMessage(content) {
        const currentContent = document.getElementById('current-content');
        if (currentContent) {
            currentContent.textContent += content;
            this.scrollToBottom();
        }
    }

    endCurrentMessage() {
        const currentMessage = document.getElementById('current-message');
        const currentContent = document.getElementById('current-content');
        
        if (currentMessage) {
            currentMessage.removeAttribute('id');
        }
        if (currentContent) {
            currentContent.removeAttribute('id');
        }
    }

    updateProgress() {
        const progress = (this.currentTurn / (this.totalTurns * 2)) * 100;
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `Turn ${Math.ceil(this.currentTurn / 2)} of ${this.totalTurns}`;
    }

    showProgress() {
        this.progressBar.style.display = 'block';
        this.progressFill.style.width = '0%';
        this.progressText.textContent = `Turn 1 of ${this.totalTurns}`;
    }

    hideProgress() {
        this.progressBar.style.display = 'none';
    }

    async stopConversation() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }

        if (this.conversationId) {
            try {
                await fetch(`/api/conversation/${this.conversationId}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.error('Error stopping conversation:', error);
            }
            this.conversationId = null;
        }

        this.isRunning = false;
        this.updateControlButtons();
        this.updateStatus('Conversation stopped');
        this.hideProgress();
        this.removeThinking();
    }

    clearMessages() {
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <i class="fas fa-robot"></i>
                <p>Configure your AI models and click "Start Conversation" to begin!</p>
            </div>
        `;
        this.updateStatus('Ready to start');
        this.hideProgress();
    }

    updateControlButtons() {
        this.startBtn.style.display = this.isRunning ? 'none' : 'flex';
        this.stopBtn.style.display = this.isRunning ? 'flex' : 'none';
        this.clearBtn.disabled = this.isRunning;
        this.startBtn.disabled = this.isRunning || !this.validateForm();
    }

    updateStatus(message, className = '') {
        this.conversationStatus.textContent = message;
        this.conversationStatus.className = `conversation-status ${className}`;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showLoading(message = 'Loading...') {
        this.loadingOverlay.style.display = 'flex';
        const loadingText = this.loadingOverlay.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    showWarning(message) {
        // You could implement a warning system similar to showError
        console.warn(message);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AiTalkDual();
});

// Handle page unload - cleanup connections
window.addEventListener('beforeunload', () => {
    if (window.aiTalkDual && window.aiTalkDual.eventSource) {
        window.aiTalkDual.eventSource.close();
    }
});
