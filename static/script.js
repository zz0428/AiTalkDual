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
            
            // Check for errors in the response
            if (data.error) {
                this.hideLoading();
                this.showError(`Model loading error: ${data.error}`);
                return;
            }
            
            // Clear existing options
            this.model1Select.innerHTML = '';
            this.model2Select.innerHTML = '';
            
            if (data.models && data.models.length > 0) {
                // Add model options with better formatting
                data.models.forEach((model) => {
                    // Create readable display name
                    const displayName = this.formatModelName(model);
                    
                    const option1 = new Option(displayName, model);
                    const option2 = new Option(displayName, model);
                    this.model1Select.add(option1);
                    this.model2Select.add(option2);
                });
                
                // Smart default selection
                this.setDefaultModels(data.models);
                
                this.showSuccess(`✅ Loaded ${data.models.length} models successfully!`);
            } else {
                // No models available
                const noModelsOption1 = new Option('No models available', '');
                const noModelsOption2 = new Option('No models available', '');
                noModelsOption1.disabled = true;
                noModelsOption2.disabled = true;
                this.model1Select.add(noModelsOption1);
                this.model2Select.add(noModelsOption2);
                this.showError('No models found. Please install models with: ollama pull model-name');
            }
            
            this.hideLoading();
        } catch (error) {
            console.error('Error loading models:', error);
            this.hideLoading();
            this.showError(`Failed to load models: ${error.message}. Make sure the web server is running and Ollama is available.`);
        }
    }

    formatModelName(model) {
        // Make model names more readable
        // Examples: "llama3.2:1b" -> "Llama 3.2 (1B)", "qwen2:7b" -> "Qwen2 (7B)"
        
        // Split on colon to separate name and size
        const parts = model.split(':');
        const name = parts[0] || model;
        const size = parts[1] || '';
        
        // Capitalize first letter and format size
        let displayName = name.charAt(0).toUpperCase() + name.slice(1);
        
        if (size) {
            displayName += ` (${size.toUpperCase()})`;
        }
        
        return displayName;
    }

    setDefaultModels(models) {
        // Smart default selection - prefer different model families
        let model1Default = null;
        let model2Default = null;
        
        // Priority order for model selection (based on your actual models)
        const preferredModels = [
            // Your actual models first
            'llama3.2:1b', 'qwen2:1.5b', 'qwen2:7b', 'gemma2:2b', 'phi3:mini', 'deepseek-r1:latest',
            // Other common models
            'qwen2:7b', 'qwen:7b', 'qwen:14b',
            'llama3.2:3b', 'llama3.1:8b', 'llama2:7b',
            'mistral:7b', 'mistral:latest',
            'phi:3b', 'phi:latest',
            'codellama:7b', 'codellama:13b',
            'gemma:2b', 'gemma:7b'
        ];
        
        // Find first available preferred model for model1
        for (const preferred of preferredModels) {
            if (models.includes(preferred)) {
                model1Default = preferred;
                break;
            }
        }
        
        // Find a different model family for model2
        for (const preferred of preferredModels) {
            if (models.includes(preferred) && preferred !== model1Default) {
                // Check if it's a different family
                const family1 = model1Default ? model1Default.split(':')[0].replace(/[0-9.]/g, '') : '';
                const family2 = preferred.split(':')[0].replace(/[0-9.]/g, '');
                
                if (family1 !== family2) {
                    model2Default = preferred;
                    break;
                }
            }
        }
        
        // Fallback: use first two different models
        if (!model1Default && models.length > 0) {
            model1Default = models[0];
        }
        if (!model2Default && models.length > 1) {
            model2Default = models[1];
        }
        
        // Set the defaults
        if (model1Default) {
            this.model1Select.value = model1Default;
        }
        if (model2Default) {
            this.model2Select.value = model2Default;
        }
        
        console.log(`Selected defaults: Model1=${model1Default}, Model2=${model2Default}`);
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

        // Use the current host instead of hardcoded address
        const baseUrl = window.location.origin;
        const streamUrl = `${baseUrl}/api/conversation/${this.conversationId}/stream`;
        
        this.eventSource = new EventSource(streamUrl);
        
        this.eventSource.onopen = (event) => {
            console.log('EventSource connection opened');
        };

        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleStreamEvent(data);
            } catch (error) {
                console.error('Error parsing stream data:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.log('EventSource error event:', error);
            console.log('EventSource readyState:', this.eventSource.readyState);
            
            // ReadyState: 0 = CONNECTING, 1 = OPEN, 2 = CLOSED
            if (this.eventSource.readyState === EventSource.CLOSED) {
                // Connection closed - this is normal when conversation ends
                console.log('EventSource connection closed (normal)');
                if (this.isRunning) {
                    // Only show error if conversation was still supposed to be running
                    this.showError('Connection closed unexpectedly. Please try again.');
                    this.stopConversation();
                }
            } else if (this.eventSource.readyState === EventSource.CONNECTING) {
                // Still trying to connect - this might be a temporary issue
                console.log('EventSource reconnecting...');
            } else {
                // Other error states
                this.showError('Connection error occurred. Check console for details.');
                this.stopConversation();
            }
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
                // Close the EventSource cleanly when conversation completes
                if (this.eventSource) {
                    this.eventSource.close();
                    this.eventSource = null;
                }
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
        // Mark as not running first to prevent error messages
        this.isRunning = false;
        
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

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
        
        this.chatMessages.appendChild(successDiv);
        this.scrollToBottom();
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.remove();
            }
        }, 3000);
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
