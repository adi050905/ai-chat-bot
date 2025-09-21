// Advanced AI Chatbot JavaScript

class AdvancedChatBot {
    constructor() {
        // Elements
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButtonText = document.getElementById('sendButtonText');
        this.sendButtonSpinner = document.getElementById('sendButtonSpinner');
        this.aiServiceSelect = document.getElementById('aiService');
        
        // New advanced elements
        this.themeToggle = document.getElementById('themeToggle');
        this.menuBtn = document.getElementById('menuBtn');
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.charCount = document.getElementById('charCount');
        this.aiStatus = document.getElementById('aiStatus');
        this.inputSuggestions = document.getElementById('inputSuggestions');
        this.attachBtn = document.getElementById('attachBtn');
        this.emojiBtn = document.getElementById('emojiBtn');
        this.fab = document.getElementById('fab');
        
        // State
        this.currentTheme = 'light';
        this.isTyping = false;
        this.chatHistory = [];
        this.currentChatId = this.generateChatId();
        this.currentSessionId = null; // Track current session ID
        this.soundEnabled = true;
        this.animationSpeed = 1;
        this.connectionState = 'online';
        this.lastActivity = Date.now();
        
        // Settings
        this.settings = {
            theme: 'auto',
            soundEffects: true,
            animationSpeed: 1,
            autoScroll: true,
            showTimestamps: true,
            showTypingIndicator: true
        };
        
        this.initialize();
        const headerNew = document.getElementById('headerNewChatBtn');
        headerNew?.addEventListener('click', () => this.createNewSession());
    }
    
    initialize() {
        this.loadSettings();
        this.initializeTheme();
        this.initializeEventListeners();
        this.initializeParticles();
        this.setInitialTime();
        this.startHealthCheck();
        this.updateConnectionStatus('online');
        
        // Initialize sessions and chat
        this.initializeChat();
        
        // Auto-resize textarea
        this.autoResizeTextarea();
        
        // Check for mobile
        this.checkMobile();
        
        console.log('🤖 Advanced AI Chatbot initialized successfully');
    }
    
    async initializeChat() {
        await this.loadUserSessions();
        await this.loadChatHistory();
        await this.loadDatabaseStats();
        if (this.chatHistory.length === 0) {
            this.showWelcomeMessage();
        }
    }

    // Theme Management
    initializeTheme() {
        const savedTheme = localStorage.getItem('chatbot-theme') || 'light';
        this.applyTheme(savedTheme);
    }
    
    applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update theme toggle icon
        if (this.themeToggle) {
            const icon = this.themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
        
        localStorage.setItem('chatbot-theme', theme);
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.playSound('theme-switch');
    }
    
    // Event Listeners
    initializeEventListeners() {
        // Send message events
        this.sendButton?.addEventListener('click', () => this.sendMessage());
        
        // Enter key handling
        this.messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                if (e.shiftKey) {
                    // Allow new line
                    return;
                } else {
                    e.preventDefault();
                    this.sendMessage();
                }
            }
            
            // Keyboard shortcuts
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'k':
                        e.preventDefault();
                        this.clearChat();
                        break;
                    case 'n':
                        e.preventDefault();
                        this.newChat();
                        break;
                    case '/':
                        e.preventDefault();
                        this.focusInput();
                        break;
                }
            }
        });
        
        // Input events
        this.messageInput?.addEventListener('input', () => {
            this.updateCharCount();
            this.updateSendButton();
            this.autoResizeTextarea();
            this.updateActivity();
        });
        
        // Theme toggle
        this.themeToggle?.addEventListener('click', () => this.toggleTheme());
        
        // Sidebar
        this.menuBtn?.addEventListener('click', () => this.toggleSidebar());
        this.sidebarToggle?.addEventListener('click', () => this.toggleSidebar());
        
        // New chat
        this.newChatBtn?.addEventListener('click', () => this.createNewSession());
        
        // AI service change
        this.aiServiceSelect?.addEventListener('change', () => this.updateAIService());
        
        // Suggestion chips
        this.inputSuggestions?.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-chip')) {
                const text = e.target.textContent.trim().replace(/^[^\\s]+\\s/, ''); // Remove icon
                this.insertSuggestion(text);
            }
        });
        
        // Attachment and emoji buttons
        this.attachBtn?.addEventListener('click', () => this.handleAttachment());
        this.emojiBtn?.addEventListener('click', () => this.showEmojiPicker());
        
        // FAB for mobile
        this.fab?.addEventListener('click', () => this.scrollToBottom());
        
        // Window events
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('beforeunload', () => this.saveChatHistory());
        
        // Visibility change for activity tracking
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handleInactive();
            } else {
                this.handleActive();
            }
        });
        
        // Click outside sidebar to close
        document.addEventListener('click', (e) => {
            if (this.sidebar?.classList.contains('open') && 
                !this.sidebar.contains(e.target) && 
                !this.menuBtn?.contains(e.target)) {
                this.toggleSidebar();
            }
        });
    }
    
    // Particles Animation
    initializeParticles() {
        const particlesContainer = document.getElementById('particles');
        if (!particlesContainer) return;
        
        const particleCount = window.innerWidth < 768 ? 20 : 50;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random size and position
            const size = Math.random() * 4 + 2;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.animationDelay = `${Math.random() * 6}s`;
            particle.style.animationDuration = `${6 + Math.random() * 4}s`;
            
            particlesContainer.appendChild(particle);
        }
    }
    
    // Message Functions
    async sendMessage() {
        const message = this.messageInput?.value.trim();
        if (!message || this.isTyping) return;
        
        this.updateActivity();
        const isFirstUserMessage = this.chatHistory.length === 0;
        this.addMessage(message, 'user');
        if (isFirstUserMessage) {
            this.autoRenameCurrentSessionFromText(message);
        }
        this.messageInput.value = '';
        this.updateCharCount();
        this.updateSendButton();
        this.autoResizeTextarea();
        this.playSound('send');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Update status
            this.updateAIStatus('Thinking...', 'thinking');
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    preferred_service: this.aiServiceSelect?.value || 'auto'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add AI response
            this.addMessage(data.response, 'bot', data.service);
            this.updateAIStatus('Ready', 'ready');
            this.playSound('receive');
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage(
                'Sorry, I encountered an error while processing your message. Please try again.',
                'bot',
                'error'
            );
            this.updateAIStatus('Error', 'error');
            this.playSound('error');
            this.updateConnectionStatus('offline');
        }
    }
    
    addMessage(text, sender, aiService = null, saveToLocalHistory = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.setAttribute('data-animation', 'slide-in');
        
        const timestamp = this.getCurrentTime();
        const messageId = this.generateMessageId();
        
        // Create avatar
        const avatarIcon = sender === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        // Create AI service tag if applicable
        const serviceTag = aiService && sender === 'bot' ? 
            `<div class="ai-service-tag">
                <i class="fas fa-brain"></i>
                ${this.getServiceDisplayName(aiService)}
            </div>` : '';
        
        // Create status indicator
        const statusIcon = sender === 'user' ? 
            '<i class="fas fa-check-double delivered"></i>' : '';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-avatar">
                    ${avatarIcon}
                </div>
                <div class="message-bubble">
                    ${serviceTag}
                    <div class="message-text">${this.formatMessage(text)}</div>
                    <div class="message-footer">
                        <div class="message-time">${timestamp}</div>
                        <div class="message-status">
                            ${statusIcon}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages?.appendChild(messageDiv);
        
        // Only save to local history if specified (not when loading from database)
        if (saveToLocalHistory) {
            this.chatHistory.push({
                id: messageId,
                text: text,
                sender: sender,
                timestamp: Date.now(),
                aiService: aiService
            });
        }
        
        // Auto scroll
        this.scrollToBottom();
        
        // Update chat preview in sidebar
        this.updateChatPreview();
    }
    
    formatMessage(text) {
        // Basic formatting for links and line breaks
        return text
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    // Typing Indicator
    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
            this.isTyping = true;
            this.scrollToBottom();
        }
    }
    
    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
            this.isTyping = false;
        }
    }
    
    // UI Updates
    updateCharCount() {
        if (this.charCount && this.messageInput) {
            const current = this.messageInput.value.length;
            const max = parseInt(this.messageInput.getAttribute('maxlength')) || 2000;
            this.charCount.textContent = `${current}/${max}`;
            
            // Color coding
            if (current > max * 0.9) {
                this.charCount.style.color = '#ef4444';
            } else if (current > max * 0.7) {
                this.charCount.style.color = '#f59e0b';
            } else {
                this.charCount.style.color = 'var(--text-muted)';
            }
        }
    }
    
    updateSendButton() {
        if (this.sendButton && this.messageInput) {
            const hasText = this.messageInput.value.trim().length > 0;
            this.sendButton.disabled = !hasText || this.isTyping;
        }
    }
    
    updateAIService() {
        const service = this.aiServiceSelect?.value;
        console.log('AI service changed to:', service);
        this.playSound('click');
    }
    
    updateAIStatus(status, state = 'ready') {
        if (this.aiStatus) {
            const statusText = this.aiStatus.querySelector('span');
            const statusIcon = this.aiStatus.querySelector('i');
            
            if (statusText) statusText.textContent = status;
            if (statusIcon) {
                statusIcon.className = state === 'thinking' ? 'fas fa-spinner fa-spin' : 
                                     state === 'error' ? 'fas fa-exclamation-circle' : 
                                     'fas fa-circle';
                statusIcon.style.color = state === 'error' ? '#ef4444' : '#10b981';
            }
        }
    }
    
    updateConnectionStatus(status) {
        this.connectionState = status;
        if (this.connectionStatus) {
            const dot = this.connectionStatus.querySelector('.status-dot');
            const text = this.connectionStatus.querySelector('span');
            
            if (dot) {
                dot.className = `status-dot ${status}`;
            }
            
            if (text) {
                text.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            }
        }
    }
    
    // Sidebar Management
    toggleSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('open');
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.classList.toggle('sidebar-open');
            }
            this.playSound('click');
        }
    }
    
    // Chat Management
    newChat() {
        this.currentChatId = this.generateChatId();
        this.chatHistory = [];
        
        // Clear messages
        if (this.chatMessages) {
            this.chatMessages.innerHTML = `
                <div class="message bot-message" data-animation="slide-in">
                    <div class="message-content">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-bubble">
                            <div class="message-text">
                                Welcome to the Advanced AI Chatbot! I'm here to help you with any questions or tasks. Choose your preferred AI service from the dropdown above, or let me automatically select the best available option for you.
                            </div>
                            <div class="message-footer">
                                <div class="message-time">${this.getCurrentTime()}</div>
                                <div class="message-status">
                                    <i class="fas fa-check-double delivered"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        this.playSound('new-chat');
        this.updateChatPreview();
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.newChat();
        }
    }
    
    clearChatSilent() {
        // Clear chat without confirmation - used for switching sessions
        this.chatHistory = [];
        
        // Clear messages
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
        }
    }
    
    showWelcomeMessage() {
        // Add welcome message for new sessions
        if (this.chatMessages) {
            this.chatMessages.innerHTML = `
                <div class="message bot-message" data-animation="slide-in">
                    <div class="message-content">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-bubble">
                            <div class="message-text">
                                Welcome to your new chat session! I'm here to help you with any questions or tasks. Choose your preferred AI service from the dropdown above, or let me automatically select the best available option for you.
                            </div>
                            <div class="message-footer">
                                <div class="message-time">${this.getCurrentTime()}</div>
                                <div class="message-status">
                                    <i class="fas fa-check-double delivered"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    // Utility Functions
    autoResizeTextarea() {
        if (this.messageInput) {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        }
    }
    
    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }
    
    focusInput() {
        this.messageInput?.focus();
    }
    
    getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    setInitialTime() {
        const initialTimeElement = document.getElementById('initial-time');
        if (initialTimeElement) {
            initialTimeElement.textContent = this.getCurrentTime();
        }
    }
    
    generateChatId() {
        return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    getServiceDisplayName(service) {
        const serviceNames = {
            'gemini': 'Gemini AI',
            'deepseek': 'Free Backup AI',
            'auto': 'Auto Select',
            'error': 'Error'
        };
        return serviceNames[service] || service;
    }
    
    // Suggestions
    insertSuggestion(text) {
        if (this.messageInput) {
            this.messageInput.value = text;
            this.updateCharCount();
            this.updateSendButton();
            this.autoResizeTextarea();
            this.focusInput();
            this.playSound('click');
        }
    }
    
    // Mobile and Responsive
    checkMobile() {
        const isMobile = window.innerWidth <= 768;
        if (isMobile && this.fab) {
            this.fab.style.display = 'flex';
        }
    }
    
    handleResize() {
        this.checkMobile();
        
        // Reinitialize particles on significant resize
        if (Math.abs(window.innerWidth - this.lastWidth) > 200) {
            const particlesContainer = document.getElementById('particles');
            if (particlesContainer) {
                particlesContainer.innerHTML = '';
                this.initializeParticles();
            }
            this.lastWidth = window.innerWidth;
        }
    }
    
    // Activity Tracking
    updateActivity() {
        this.lastActivity = Date.now();
        if (this.connectionState === 'offline') {
            this.updateConnectionStatus('online');
        }
    }
    
    handleActive() {
        this.updateActivity();
        this.startHealthCheck();
    }
    
    handleInactive() {
        // Could implement away status here
    }
    
    // Health Check
    startHealthCheck() {
        if (this.healthCheckInterval) {
            clearInterval(this.healthCheckInterval);
        }
        
        this.healthCheckInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/health');
                if (response.ok) {
                    this.updateConnectionStatus('online');
                } else {
                    this.updateConnectionStatus('offline');
                }
            } catch (error) {
                this.updateConnectionStatus('offline');
            }
        }, 30000); // Check every 30 seconds
    }
    
    // Sound Effects
    playSound(type) {
        if (!this.soundEnabled) return;
        
        // Create audio context for web audio API sounds
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        try {
            const sounds = {
                'send': { frequency: 800, duration: 0.1 },
                'receive': { frequency: 600, duration: 0.15 },
                'error': { frequency: 300, duration: 0.3 },
                'click': { frequency: 1000, duration: 0.05 },
                'theme-switch': { frequency: 700, duration: 0.1 },
                'new-chat': { frequency: 900, duration: 0.2 }
            };
            
            const sound = sounds[type];
            if (sound) {
                this.beep(sound.frequency, sound.duration);
            }
        } catch (error) {
            console.log('Sound not available:', error);
        }
    }
    
    beep(frequency, duration) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }
    
    // Settings Management
    loadSettings() {
        const saved = localStorage.getItem('chatbot-settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
        this.applySettings();
    }
    
    saveSettings() {
        localStorage.setItem('chatbot-settings', JSON.stringify(this.settings));
    }
    
    applySettings() {
        this.soundEnabled = this.settings.soundEffects;
        this.animationSpeed = this.settings.animationSpeed;
        
        // Apply animation speed
        document.documentElement.style.setProperty('--animation-speed', this.animationSpeed);
    }
    
    // Chat History (Database Integration)
    async loadChatHistory() {
        try {
            console.log('Loading chat history for session:', this.currentSessionId);
            const response = await fetch('/api/history');
            if (response.ok) {
                const data = await response.json();
                this.chatHistory = data.history || [];
                console.log('Loaded chat history:', this.chatHistory.length, 'messages');
                this.renderChatHistory();
            } else {
                console.error('Failed to load chat history, status:', response.status);
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
            // Fallback to localStorage
            const saved = localStorage.getItem(`chatbot-history-${this.currentChatId}`);
            if (saved) {
                this.chatHistory = JSON.parse(saved);
                this.renderChatHistory();
            }
        }
    }
    
    async saveChatHistory() {
        // Database saves automatically, but keep localStorage as backup
        localStorage.setItem(`chatbot-history-${this.currentChatId}`, JSON.stringify(this.chatHistory));
    }
    
    renderChatHistory() {
        console.log('Rendering chat history:', this.chatHistory.length, 'messages');
        // Clear current messages
        this.chatMessages.innerHTML = '';
        
        // Render messages from database
        this.chatHistory.forEach(message => {
            if (message.type === 'user') {
                this.addMessage(message.content, 'user', null, false);
            } else {
                // Use 'bot' for AI messages to match CSS classes
                this.addMessage(message.content, 'bot', null, false);
            }
        });
        
        this.updateChatPreview();
    }
    
    updateChatPreview() {
        // Update sidebar chat history preview
        const historyItem = document.querySelector('.history-item.active .history-preview');
        if (historyItem && this.chatHistory.length > 0) {
            const lastMessage = this.chatHistory[this.chatHistory.length - 1];
            const text = (lastMessage.content || lastMessage.text || '').toString();
            if (text) historyItem.textContent = text.substring(0, 50) + '...';
        }
    }
    
    // Session Management
    async getCurrentSession() {
        try {
            const response = await fetch('/api/current-session');
            if (response.ok) {
                const data = await response.json();
                this.currentSessionId = data.session_id;
                return data.session_id;
            }
        } catch (error) {
            console.error('Failed to get current session:', error);
        }
        return null;
    }
    
    async loadUserSessions() {
        try {
            // Get current session first
            await this.getCurrentSession();
            
            const response = await fetch('/api/sessions');
            if (response.ok) {
                const data = await response.json();
                this.renderSessionList(data.sessions);
            }
        } catch (error) {
            console.error('Failed to load sessions:', error);
        }
    }
    
    async createNewSession(name = null) {
        if (!name) {
            name = 'New Chat';
        }
        try {
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            if (response.ok) {
                const data = await response.json();
                // This is the critical part: switch to the new session ID
                await this.switchSession(data.session_id); 
                this.showNotification('New chat created!', 'success');
            } else {
                this.showNotification('Failed to create new chat.', 'error');
            }
        } catch (error) {
            console.error('Error creating new session:', error);
            this.showNotification('Error creating new chat.', 'error');
        }
    }

    async autoRenameCurrentSessionFromText(text) {
        try {
            if (!this.currentSessionId || !text) return;
            // Clean and shorten text for title
            const clean = text
                .replace(/```[\s\S]*?```/g, '')
                .replace(/`[^`]*`/g, '')
                .replace(/\s+/g, ' ')
                .trim();
            if (!clean) return;
            let title = clean.slice(0, 40);
            if (clean.length > 40) title += '…';
            const response = await fetch(`/api/sessions/${this.currentSessionId}/rename`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: title })
            });
            if (response.ok) {
                await this.loadUserSessions();
            }
        } catch (e) {
            console.warn('Auto-rename failed:', e);
        }
    }
    
    async switchSession(sessionId) {
        console.log(`Switching to session: ${sessionId}`);
        try {
            const response = await fetch(`/api/sessions/${sessionId}/switch`, {
                method: 'POST'
            });
            if (response.ok) {
                this.currentSessionId = sessionId;
                await this.loadChatHistory(); // Load history for the NEW session
                await this.loadUserSessions(); // Reload session list to update the 'active' class
                // Scroll to active item and flash it for clarity
                const active = document.querySelector(`.history-item[data-session-id="${sessionId}"]`);
                if (active) {
                    active.classList.add('active', 'flash');
                    active.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    setTimeout(() => active.classList.remove('flash'), 800);
                }
                if (this.chatHistory.length === 0) {
                    this.showWelcomeMessage();
                }
            } else {
                this.showNotification('Failed to switch session.', 'error');
            }
        } catch (error) {
            console.error('Error switching session:', error);
            this.showNotification('Error switching session.', 'error');
        }
    }
    
    async deleteSession(sessionId) {
        if (!confirm('Are you sure you want to delete this chat session?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/sessions/${sessionId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                await this.loadUserSessions();
                await this.loadChatHistory();
                this.showNotification('Session deleted', 'success');
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
            this.showNotification('Failed to delete session', 'error');
        }
    }
    
    async renameSession(sessionId, newName) {
        try {
            const response = await fetch(`/api/sessions/${sessionId}/rename`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName })
            });
            
            if (response.ok) {
                await this.loadUserSessions();
                this.showNotification('Session renamed', 'success');
            }
        } catch (error) {
            console.error('Failed to rename session:', error);
            this.showNotification('Failed to rename session', 'error');
        }
    }
    
    renderSessionList(sessions) {
        const historyContainer = document.querySelector('.chat-history');
        if (!historyContainer) return;
        
        if (sessions.length === 0) {
            historyContainer.innerHTML = `
                <div class="no-sessions">
                    <i class="fas fa-comments"></i>
                    <p>No chat sessions yet</p>
                    <p>Click "New Chat" to start!</p>
                </div>
            `;
            return;
        }
        
        historyContainer.innerHTML = sessions.map(session => `
            <div class="history-item ${session.id === this.currentSessionId ? 'active' : ''}" data-session-id="${session.id}">
                <div class="history-header">
                    <h4 class="history-title" contenteditable="false">${this.escapeHtml(session.name)}</h4>
                    <div class="history-actions">
                        <button class="btn-icon rename-session" title="Rename">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-icon delete-session" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="history-preview">${session.message_count} messages</div>
                <div class="history-time">${this.formatDate(session.updated_at)}</div>
            </div>
        `).join('');
        
        // Add event listeners
        historyContainer.querySelectorAll('.history-item').forEach(item => {
            const sessionId = parseInt(item.dataset.sessionId);
            
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.history-actions')) {
                    this.switchSession(sessionId);
                }
            });
            
            item.querySelector('.rename-session').addEventListener('click', (e) => {
                e.stopPropagation();
                this.enableSessionRename(item, sessionId);
            });
            
            item.querySelector('.delete-session').addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteSession(sessionId);
            });
        });
    }
    
    enableSessionRename(item, sessionId) {
        const titleElement = item.querySelector('.history-title');
        const originalName = titleElement.textContent;
        
        titleElement.contentEditable = true;
        titleElement.focus();
        
        const saveRename = () => {
            const newName = titleElement.textContent.trim();
            titleElement.contentEditable = false;
            
            if (newName && newName !== originalName) {
                this.renameSession(sessionId, newName);
            } else {
                titleElement.textContent = originalName;
            }
        };
        
        titleElement.addEventListener('blur', saveRename, { once: true });
        titleElement.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                titleElement.blur();
            }
        });
    }
    
    // Database Statistics
    async loadDatabaseStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const stats = await response.json();
                this.displayDatabaseStats(stats);
            }
        } catch (error) {
            console.error('Failed to load database stats:', error);
        }
    }
    
    displayDatabaseStats(stats) {
        const statsContainer = document.querySelector('.database-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Total Users:</span>
                    <span class="stat-value">${stats.users}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Your Sessions:</span>
                    <span class="stat-value">${stats.user_sessions}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Your Messages:</span>
                    <span class="stat-value">${stats.user_messages}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Messages:</span>
                    <span class="stat-value">${stats.messages}</span>
                </div>
            `;
        }
    }
    
    // Utility Functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            return 'Today';
        } else if (diffDays === 2) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Hide notification
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // File Attachment (placeholder)
    handleAttachment() {
        // Placeholder for file attachment functionality
        alert('File attachment feature coming soon!');
        this.playSound('click');
    }
    
    // Emoji Picker (placeholder)
    showEmojiPicker() {
        // Placeholder for emoji picker
        const emojis = ['😊', '😂', '❤️', '👍', '🎉', '🤔', '😢', '😮'];
        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        if (this.messageInput) {
            this.messageInput.value += randomEmoji;
            this.updateCharCount();
            this.updateSendButton();
            this.playSound('click');
        }
    }
}

// Global functions for backwards compatibility
function sendMessage() {
    if (window.chatBot) {
        window.chatBot.sendMessage();
    }
}

function updateAIService() {
    if (window.chatBot) {
        window.chatBot.updateAIService();
    }
}

function insertSuggestion(text) {
    if (window.chatBot) {
        window.chatBot.insertSuggestion(text);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatBot = new AdvancedChatBot();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedChatBot;
}