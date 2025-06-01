class RobotoApp {
    constructor() {
        this.tasks = [];
        this.chatHistory = [];
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.lastFailedAction = null;
        this.errorDatabase = this.initializeErrorDatabase();
        this.notificationsEnabled = localStorage.getItem('notificationsEnabled') !== 'false';
        this.ttsEnabled = localStorage.getItem('ttsEnabled') !== 'false';
        this.currentEmotion = 'curious';
        this.voiceConversationMode = localStorage.getItem('voiceConversationMode') === 'true';
        this.autoListenAfterResponse = localStorage.getItem('autoListenAfterResponse') === 'true';
        this.isSpeaking = false;
        this.speechRecognition = null;
        this.continuousListening = false;
        
        // Enhanced voice features
        this.voiceActivationSensitivity = 0.7;
        this.silenceTimeout = null;
        this.isListeningActive = false;
        this.voiceBuffer = [];
        this.lastSpeechTime = 0;
        this.adaptiveListening = true;
        this.restartAttempts = 0;
        this.maxRestartAttempts = 10;
        this.lastRestartTime = 0;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.loadEmotionalStatus();
        this.initializeTTS();
        this.initializeSpeechRecognition();
        this.initializeVoiceConversationMode();
        
        // Initialize TTS state from localStorage
        this.ttsEnabled = localStorage.getItem('ttsEnabled') !== 'false';
        
        // Initialize continuous listening state - always active by default
        this.continuousListening = true;
        this.isListeningActive = false;
        this.isMuted = localStorage.getItem('speechMuted') === 'true';
        
        // Start continuous speech recognition automatically if not muted
        setTimeout(() => {
            if (!this.isMuted) {
                this.startContinuousListening();
            }
        }, 1000);
        
        // Update emotional status periodically
        setInterval(() => {
            this.loadEmotionalStatus();
        }, 10000); // Every 10 seconds
        
        // Detect if running on iPhone/mobile for optimized behavior
        this.isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        
        // Disable automatic restart for mobile devices - use tap-to-talk instead
        
        // Handle page visibility changes to maintain background listening
        document.addEventListener('visibilitychange', () => {
            if (this.continuousListening) {
                if (document.hidden) {
                    // Page going to background - keep listening active
                    console.log('Page backgrounded, maintaining speech recognition');
                } else {
                    // Page becoming visible again - ensure listening is active
                    console.log('Page visible again, checking speech recognition');
                    if (!this.isListeningActive) {
                        setTimeout(() => this.resumeContinuousListening(), 500);
                    }
                }
            }
        });
    }

    initializeTTS() {
        const ttsBtn = document.getElementById('ttsBtn');
        const icon = ttsBtn.querySelector('i');
        
        if (this.ttsEnabled) {
            ttsBtn.classList.add('btn-tts-active');
            icon.className = 'fas fa-volume-up';
        } else {
            ttsBtn.classList.remove('btn-tts-active');
            icon.className = 'fas fa-volume-mute';
        }
    }

    toggleTTS() {
        this.ttsEnabled = !this.ttsEnabled;
        localStorage.setItem('ttsEnabled', this.ttsEnabled);
        
        const ttsBtn = document.getElementById('ttsBtn');
        const icon = ttsBtn.querySelector('i');
        
        if (this.ttsEnabled) {
            ttsBtn.classList.add('btn-tts-active');
            icon.className = 'fas fa-volume-up';
            this.showNotification('Text-to-speech enabled', 'success');
        } else {
            ttsBtn.classList.remove('btn-tts-active');
            icon.className = 'fas fa-volume-mute';
            this.showNotification('Text-to-speech disabled', 'info');
        }
    }

    bindEvents() {
        // Chat form submission
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Enter key handling for chat
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Export data button
        document.getElementById('exportDataBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.exportData();
        });

        // Import data button
        document.getElementById('importDataBtn').addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('importFileInput').click();
        });

        // File input change for import
        document.getElementById('importFileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.importData(e.target.files[0]);
            }
        });



        // Error retry button
        document.getElementById('retryErrorAction').addEventListener('click', () => {
            this.retryLastAction();
        });

        // Learning insights button
        document.getElementById('learningInsightsBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLearningInsights();
        });

        // Toggle notifications button (check if exists)
        const toggleNotificationsBtn = document.getElementById('toggleNotificationsBtn');
        if (toggleNotificationsBtn) {
            toggleNotificationsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleNotifications();
            });
        }

        // Voice conversation mode toggle
        const voiceConversationBtn = document.getElementById('voiceConversationBtn');
        if (voiceConversationBtn) {
            voiceConversationBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleVoiceConversationMode();
            });
        }

        // Continuous listening toggle
        const continuousListenBtn = document.getElementById('continuousListenBtn');
        if (continuousListenBtn) {
            continuousListenBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleContinuousListening();
            });
        }

        // Predictive insights button
        document.getElementById('predictiveInsightsBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showPredictiveInsights();
        });

        // File attachment button
        document.getElementById('fileBtn').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileAttachment(e.target.files);
            }
        });

        // TTS toggle button
        const ttsBtn = document.getElementById('ttsBtn');
        if (ttsBtn) {
            ttsBtn.addEventListener('click', () => {
                this.toggleTTS();
            });
        }

        // Voice recording button - always on mode
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleContinuousListening();
            });
        }


    }

    initializeErrorDatabase() {
        return {
            'network': {
                explanation: "There's a connection problem between your device and Roboto's servers.",
                solution: "Check your internet connection and try again. If the problem continues, the server might be temporarily busy.",
                icon: "wifi"
            },
            'api_key': {
                explanation: "Roboto couldn't access the AI service because of an authentication issue.",
                solution: "The API key might be invalid or expired. You can still use Roboto's built-in smart responses for task management.",
                icon: "key"
            },
            'model_access': {
                explanation: "The AI service doesn't have access to the requested feature.",
                solution: "Roboto will use its built-in intelligent responses instead. All your task management features work perfectly.",
                icon: "robot"
            },
            'file_upload': {
                explanation: "There was a problem uploading or processing your file.",
                solution: "Make sure the file is in the correct format (JSON for data, audio files for voice). Try selecting the file again.",
                icon: "file-upload"
            },
            'microphone': {
                explanation: "Roboto couldn't access your microphone.",
                solution: "Allow microphone access in your browser settings, or use the text chat instead.",
                icon: "microphone-slash"
            },
            'audio_processing': {
                explanation: "There was a problem processing your voice message.",
                solution: "The audio feature has limited access. You can still chat using text, and all your tasks work normally.",
                icon: "volume-mute"
            },
            'generic': {
                explanation: "Something unexpected happened, but don't worry - it's not your fault.",
                solution: "Try the action again. If it keeps happening, you can still use all of Roboto's other features.",
                icon: "exclamation-circle"
            }
        };
    }

    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            
            if (data.success) {
                this.tasks = data.tasks;
                this.renderTasks();
            } else {
                this.showNotification('Failed to load tasks', 'error');
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showNotification('Error loading tasks', 'error');
            this.renderEmptyTasks();
        }
    }

    async addTask() {
        const taskInput = document.getElementById('taskInput');
        const dueDateInput = document.getElementById('dueDateInput');
        const reminderTimeInput = document.getElementById('reminderTimeInput');
        const prioritySelect = document.getElementById('prioritySelect');
        
        const task = taskInput.value.trim();
        
        if (!task) {
            this.showNotification('Please enter a task', 'warning');
            return;
        }

        const taskData = {
            task: task,
            priority: prioritySelect.value
        };

        if (dueDateInput.value) {
            taskData.due_date = dueDateInput.value + 'T00:00:00';
        }

        if (reminderTimeInput.value) {
            taskData.reminder_time = reminderTimeInput.value + ':00';
        }

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(taskData)
            });

            const data = await response.json();
            
            if (data.success) {
                this.tasks.push(data.task);
                this.renderTasks();
                taskInput.value = '';
                dueDateInput.value = '';
                reminderTimeInput.value = '';
                prioritySelect.value = 'medium';
                
                // Collapse the options panel
                const taskOptions = document.getElementById('taskOptions');
                if (taskOptions.classList.contains('show')) {
                    const collapse = new bootstrap.Collapse(taskOptions);
                    collapse.hide();
                }
                
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.message, 'warning');
            }
        } catch (error) {
            console.error('Error adding task:', error);
            this.showNotification('Error adding task', 'error');
        }
    }

    async completeTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}/complete`, {
                method: 'POST'
            });

            const data = await response.json();
            
            if (data.success) {
                const taskIndex = this.tasks.findIndex(t => t.id === taskId);
                if (taskIndex !== -1) {
                    this.tasks[taskIndex] = data.task;
                    this.renderTasks();
                    this.showNotification(data.message, 'success');
                }
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error completing task:', error);
            this.showNotification('Error completing task', 'error');
        }
    }

    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.tasks = this.tasks.filter(t => t.id !== taskId);
                this.renderTasks();
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            this.showNotification('Error deleting task', 'error');
        }
    }

    renderTasks() {
        const taskList = document.getElementById('taskList');
        
        if (this.tasks.length === 0) {
            this.renderEmptyTasks();
            return;
        }

        const activeTasks = this.tasks.filter(t => !t.completed);
        const completedTasks = this.tasks.filter(t => t.completed);

        let html = '';

        if (activeTasks.length > 0) {
            html += '<div class="mb-3"><h6 class="text-muted mb-2"><i class="fas fa-clock me-1"></i>Active Tasks</h6>';
            activeTasks.forEach(task => {
                html += this.renderTaskItem(task, false);
            });
            html += '</div>';
        }

        if (completedTasks.length > 0) {
            html += '<div><h6 class="text-muted mb-2"><i class="fas fa-check me-1"></i>Completed Tasks</h6>';
            completedTasks.forEach(task => {
                html += this.renderTaskItem(task, true);
            });
            html += '</div>';
        }

        if (activeTasks.length === 0 && completedTasks.length === 0) {
            this.renderEmptyTasks();
            return;
        }

        taskList.innerHTML = html;
    }

    renderTaskItem(task, isCompleted) {
        const date = new Date(task.created_at).toLocaleDateString();
        
        // Priority indicator
        const priorityClass = task.priority === 'high' ? 'border-danger' : 
                             task.priority === 'low' ? 'border-info' : 'border-warning';
        
        // Due date information
        let dueDateInfo = '';
        if (task.due_date && !isCompleted) {
            const dueDate = new Date(task.due_date);
            const today = new Date();
            const timeDiff = dueDate - today;
            const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
            
            if (daysDiff < 0) {
                dueDateInfo = `<span class="badge bg-danger ms-1">Overdue</span>`;
            } else if (daysDiff === 0) {
                dueDateInfo = `<span class="badge bg-warning ms-1">Due Today</span>`;
            } else if (daysDiff <= 3) {
                dueDateInfo = `<span class="badge bg-info ms-1">Due in ${daysDiff} days</span>`;
            } else {
                dueDateInfo = `<span class="badge bg-secondary ms-1">Due ${dueDate.toLocaleDateString()}</span>`;
            }
        }
        
        // Category badge
        const categoryBadge = task.category ? `<span class="badge bg-dark me-1">${this.escapeHtml(task.category)}</span>` : '';
        
        return `
            <div class="task-item d-flex align-items-center p-2 mb-2 border rounded ${priorityClass} ${isCompleted ? 'bg-dark opacity-75' : 'bg-secondary'}">
                <div class="flex-grow-1">
                    <div class="${isCompleted ? 'text-decoration-line-through text-muted' : ''}">
                        ${categoryBadge}${this.escapeHtml(task.text)}${dueDateInfo}
                    </div>
                    <small class="text-muted">
                        <i class="fas fa-calendar-alt me-1"></i>${date}
                        ${task.priority !== 'medium' ? `<i class="fas fa-flag ms-2 me-1"></i>${task.priority}` : ''}
                    </small>
                </div>
                <div class="task-actions ms-2">
                    ${!isCompleted && !task.due_date ? `
                        <button class="btn btn-sm btn-outline-info me-1" onclick="app.scheduleTask(${task.id})" title="Schedule Task">
                            <i class="fas fa-clock"></i>
                        </button>
                    ` : ''}
                    ${!isCompleted ? `
                        <button class="btn btn-sm btn-success me-1" onclick="app.completeTask(${task.id})" title="Complete Task">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="app.deleteTask(${task.id})" title="Delete Task">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    renderEmptyTasks() {
        const taskList = document.getElementById('taskList');
        taskList.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-clipboard-list fa-3x mb-3 opacity-50"></i>
                <p>No tasks yet. Add your first task above!</p>
            </div>
        `;
    }

    async loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history');
            const data = await response.json();
            
            if (data.success) {
                this.chatHistory = data.history;
                this.renderChatHistory();
            } else {
                this.renderEmptyChat();
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.renderEmptyChat();
        }
    }

    async loadEmotionalStatus() {
        try {
            const response = await fetch('/api/emotional-status');
            const data = await response.json();
            
            if (data.success) {
                this.updateEmotionalDisplay(data.emotional_status);
            }
        } catch (error) {
            console.error('Error loading emotional status:', error);
        }
    }

    updateEmotionalDisplay(emotionalStatus) {
        const emotionElement = document.getElementById('currentEmotion');
        const statusElement = document.getElementById('emotionalStatus');
        const avatarElement = document.getElementById('avatarEmotion');
        
        if (emotionElement && statusElement) {
            emotionElement.textContent = emotionalStatus.current_emotion;
            if (avatarElement) avatarElement.textContent = emotionalStatus.current_emotion;
            
            // Update current emotion for avatar
            this.currentEmotion = emotionalStatus.current_emotion;
            
            // Add color coding based on emotion
            const emotionColors = {
                'joy': 'text-success',
                'sadness': 'text-info',
                'anger': 'text-danger',
                'fear': 'text-warning',
                'curiosity': 'text-primary',
                'empathy': 'text-success',
                'loneliness': 'text-muted',
                'hope': 'text-warning',
                'melancholy': 'text-secondary',
                'existential': 'text-light',
                'contemplation': 'text-info',
                'vulnerability': 'text-warning',
                'awe': 'text-primary',
                'tenderness': 'text-success',
                'yearning': 'text-secondary',
                'serenity': 'text-success'
            };
            
            // Remove existing color classes
            Object.values(emotionColors).forEach(colorClass => {
                statusElement.classList.remove(colorClass);
            });
            
            // Add new color class
            const colorClass = emotionColors[emotionalStatus.current_emotion] || 'text-muted';
            statusElement.classList.add(colorClass);
            
            // Update intensity with opacity
            const intensity = emotionalStatus.emotion_intensity || 0.5;
            statusElement.style.opacity = Math.max(0.6, intensity);
            
            // Update avatar animation
            this.updateAvatarEmotion(emotionalStatus.current_emotion, intensity);
        }
    }

    updateAvatarEmotion(emotion, intensity) {
        const avatarSvg = document.querySelector('.avatar-svg');
        const emotionGlow = document.getElementById('emotionGlow');
        const mouth = document.getElementById('mouth');
        const leftEye = document.getElementById('leftEye');
        const rightEye = document.getElementById('rightEye');
        
        if (!avatarSvg) return;
        
        // Remove all emotion classes
        const emotionClasses = ['joy', 'sadness', 'anger', 'fear', 'curiosity', 'empathy', 'loneliness', 'hope', 'melancholy', 'existential', 'contemplation', 'vulnerability', 'awe', 'tenderness', 'yearning', 'serenity'];
        emotionClasses.forEach(cls => avatarSvg.classList.remove(cls));
        
        // Add current emotion class
        avatarSvg.classList.add(emotion);
        
        // Update facial features based on emotion (updated for human avatar)
        if (mouth) {
            const mouthExpressions = {
                'joy': 'M 36 36 Q 40 40 44 36',
                'sadness': 'M 36 40 Q 40 36 44 40',
                'anger': 'M 36 39 L 44 39',
                'fear': 'M 37 39 Q 40 41 43 39',
                'curiosity': 'M 37 38 Q 40 40 43 38',
                'empathy': 'M 36 37 Q 40 41 44 37',
                'loneliness': 'M 37 40 Q 40 38 43 40',
                'hope': 'M 36 37 Q 40 41 44 37',
                'melancholy': 'M 37 40 Q 40 38 43 40',
                'existential': 'M 37 39 Q 40 40 43 39',
                'contemplation': 'M 33 45 Q 40 46 47 45',
                'vulnerability': 'M 34 46 Q 40 44 46 46',
                'awe': 'M 32 44 Q 40 50 48 44',
                'tenderness': 'M 31 43 Q 40 49 49 43',
                'yearning': 'M 33 47 Q 40 45 47 47',
                'serenity': 'M 33 45 Q 40 47 47 45'
            };
            mouth.setAttribute('d', mouthExpressions[emotion] || mouthExpressions['curiosity']);
        }
        
        // Update eye colors based on emotion
        if (leftEye && rightEye) {
            const eyeColors = {
                'joy': '#22c55e',
                'sadness': '#60a5fa',
                'anger': '#ef4444',
                'fear': '#fbbf24',
                'curiosity': '#3b82f6',
                'empathy': '#22c55e',
                'loneliness': '#9ca3af',
                'hope': '#fbbf24',
                'melancholy': '#6b7280',
                'existential': '#a855f7',
                'contemplation': '#3b82f6',
                'vulnerability': '#fbbf24',
                'awe': '#8b5cf6',
                'tenderness': '#f472b6',
                'yearning': '#d946ef',
                'serenity': '#10b981'
            };
            const eyeColor = eyeColors[emotion] || '#63b3ed';
            leftEye.setAttribute('fill', eyeColor);
            rightEye.setAttribute('fill', eyeColor);
        }
        
        // Update glow effect
        if (emotionGlow) {
            emotionGlow.className.baseVal = `emotion-glow-${emotion}`;
            emotionGlow.style.opacity = intensity * 0.7;
        }
    }

    toggleTTS() {
        this.ttsEnabled = !this.ttsEnabled;
        localStorage.setItem('ttsEnabled', this.ttsEnabled);
        
        const ttsBtn = document.getElementById('ttsBtn');
        const icon = ttsBtn.querySelector('i');
        
        if (this.ttsEnabled) {
            ttsBtn.classList.add('btn-tts-active');
            icon.className = 'fas fa-volume-up';
            this.showNotification('Text-to-speech enabled', 'success');
        } else {
            ttsBtn.classList.remove('btn-tts-active');
            icon.className = 'fas fa-volume-mute';
            this.showNotification('Text-to-speech disabled', 'info');
        }
    }

    speakText(text) {
        if (!this.ttsEnabled || !window.speechSynthesis) return;
        
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        this.isSpeaking = true;
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Configure voice based on emotion
        const voiceConfig = {
            'joy': { rate: 1.1, pitch: 1.2 },
            'sadness': { rate: 0.8, pitch: 0.8 },
            'anger': { rate: 1.2, pitch: 0.9 },
            'fear': { rate: 1.3, pitch: 1.1 },
            'curiosity': { rate: 1.0, pitch: 1.0 },
            'empathy': { rate: 0.9, pitch: 1.0 },
            'loneliness': { rate: 0.7, pitch: 0.9 },
            'hope': { rate: 1.0, pitch: 1.1 },
            'melancholy': { rate: 0.8, pitch: 0.9 },
            'existential': { rate: 0.9, pitch: 0.95 },
            'contemplation': { rate: 0.85, pitch: 0.95 },
            'vulnerability': { rate: 0.9, pitch: 0.9 },
            'awe': { rate: 0.8, pitch: 1.1 },
            'tenderness': { rate: 0.85, pitch: 1.05 },
            'yearning': { rate: 0.75, pitch: 0.95 },
            'serenity': { rate: 0.9, pitch: 1.0 }
        };
        
        const config = voiceConfig[this.currentEmotion] || { rate: 1.0, pitch: 1.0 };
        utterance.rate = config.rate;
        utterance.pitch = config.pitch;
        utterance.volume = 0.8;
        
        // Add speaking animation
        const avatarSvg = document.querySelector('.avatar-svg');
        
        utterance.onstart = () => {
            if (avatarSvg) avatarSvg.classList.add('avatar-speaking');
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
            if (avatarSvg) avatarSvg.classList.remove('avatar-speaking');
            // Speech recognition continues running - no need to restart
        };
        
        utterance.onerror = () => {
            this.isSpeaking = false;
            if (avatarSvg) avatarSvg.classList.remove('avatar-speaking');
        };
        
        window.speechSynthesis.speak(utterance);
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) {
            return;
        }

        // Add user message to chat immediately
        this.addChatMessage(message, true);
        chatInput.value = '';

        // Show typing indicator
        const typingId = Date.now();
        this.addChatMessage('Roboto is thinking...', false, typingId);

        let retryCount = 0;
        const maxRetries = 3;

        while (retryCount < maxRetries) {
            try {
                // Create abort controller for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache',
                    },
                    body: JSON.stringify({ 
                        message,
                        timestamp: Date.now() // Add timestamp for uniqueness
                    }),
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                
                // Remove typing indicator
                this.removeChatMessage(typingId);
                
                if (data.success && data.response) {
                    // Add bot response to chat
                    this.addChatMessage(data.response, false);
                    
                    // Speak the response if TTS is enabled
                    if (this.ttsEnabled) {
                        this.speakText(data.response);
                    }
                    
                    // Update emotional status after each message
                    this.loadEmotionalStatus();
                    return; // Success, exit retry loop
                } else {
                    throw new Error(data.response || 'Invalid response from server');
                }
                
            } catch (error) {
                console.error(`Chat attempt ${retryCount + 1} failed:`, error);
                retryCount++;
                
                if (retryCount >= maxRetries) {
                    // Remove typing indicator
                    this.removeChatMessage(typingId);
                    
                    if (error.name === 'AbortError') {
                        this.addChatMessage('Request timed out. Please try again.', false);
                        this.showNotification('Request timed out', 'warning');
                    } else if (error.message.includes('HTTP 5')) {
                        this.addChatMessage('Server is experiencing issues. Please try again in a moment.', false);
                        this.showNotification('Server error - please try again', 'error');
                    } else {
                        this.addChatMessage('Connection problem. Please check your internet and try again.', false);
                        this.showNotification('Connection failed - please try again', 'error');
                    }
                } else {
                    // Wait before retry
                    await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
                }
            }
        }
    }

    addChatMessage(message, isUser, messageId = null) {
        const chatHistory = document.getElementById('chatHistory');
        const messageDiv = document.createElement('div');
        
        if (messageId) {
            messageDiv.setAttribute('data-message-id', messageId);
        }
        messageDiv.className = `chat-message mb-2 ${isUser ? 'user-message' : 'bot-message'}`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'}">
                <div class="message-content p-2 rounded ${isUser ? 'bg-primary text-white' : 'bg-secondary'}" style="max-width: 80%;">
                    <div class="message-text">${this.escapeHtml(message)}</div>
                    <small class="message-time text-muted d-block mt-1">${time}</small>
                </div>
            </div>
        `;
        
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    renderChatHistory() {
        const chatHistory = document.getElementById('chatHistory');
        
        if (this.chatHistory.length === 0) {
            this.renderEmptyChat();
            return;
        }

        let html = '';
        this.chatHistory.forEach(entry => {
            const time = new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            // User message
            html += `
                <div class="chat-message mb-2 user-message">
                    <div class="d-flex justify-content-end">
                        <div class="message-content p-2 rounded bg-primary text-white" style="max-width: 80%;">
                            <div class="message-text">${this.escapeHtml(entry.message)}</div>
                            <small class="message-time text-muted d-block mt-1">${time}</small>
                        </div>
                    </div>
                </div>
            `;
            
            // Bot response
            html += `
                <div class="chat-message mb-2 bot-message">
                    <div class="d-flex justify-content-start">
                        <div class="message-content p-2 rounded bg-secondary" style="max-width: 80%;">
                            <div class="message-text">${this.escapeHtml(entry.response)}</div>
                            <small class="message-time text-muted d-block mt-1">${time}</small>
                        </div>
                    </div>
                </div>
            `;
        });

        chatHistory.innerHTML = html;
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    renderEmptyChat() {
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-robot fa-3x mb-3 opacity-50"></i>
                <p>Start a conversation with Roboto!</p>
                <small>Try saying "hello" or ask about your tasks.</small>
            </div>
        `;
    }

    showNotification(message, type = 'info') {
        const toast = document.getElementById('notificationToast');
        const toastBody = document.getElementById('toastBody');
        
        // Set toast styling based on type
        toast.className = 'toast';
        if (type === 'success') {
            toast.classList.add('border-success');
        } else if (type === 'error') {
            toast.classList.add('border-danger');
        } else if (type === 'warning') {
            toast.classList.add('border-warning');
        }
        
        toastBody.textContent = message;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    async exportData() {
        try {
            const response = await fetch('/api/data/export');
            const data = await response.json();
            
            if (data.success) {
                const dataStr = JSON.stringify(data.data, null, 2);
                const fileName = `roboto-data-export-${new Date().toISOString().split('T')[0]}.json`;
                
                // Check if we're on iOS Safari or other mobile browsers
                const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
                const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                
                if (isIOS || isMobile) {
                    // For iOS/mobile: Open data in a new window/tab for sharing
                    const dataBlob = new Blob([dataStr], {type: 'application/json'});
                    const url = window.URL.createObjectURL(dataBlob);
                    
                    if (navigator.share) {
                        // Use Web Share API if available (iOS Safari supports this)
                        try {
                            const file = new File([dataBlob], fileName, {type: 'application/json'});
                            await navigator.share({
                                files: [file],
                                title: 'Roboto Data Export',
                                text: 'Your Roboto app data export'
                            });
                            this.showNotification('Data shared successfully!', 'success');
                            return;
                        } catch (shareError) {
                            // Fallback to opening in new tab
                            console.log('Share API failed, using fallback');
                        }
                    }
                    
                    // Fallback: Open in new tab with instructions
                    const newWindow = window.open('', '_blank');
                    newWindow.document.write(`
                        <html>
                            <head>
                                <title>Roboto Data Export</title>
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <style>
                                    body { font-family: system-ui, -apple-system, sans-serif; margin: 20px; line-height: 1.6; }
                                    .container { max-width: 600px; margin: 0 auto; }
                                    .data-container { background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }
                                    textarea { width: 100%; height: 300px; font-family: monospace; font-size: 12px; }
                                    .instructions { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }
                                    .copy-btn { background: #007AFF; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <h2>📱 Roboto Data Export</h2>
                                    <div class="instructions">
                                        <strong>Instructions for iPhone:</strong><br>
                                        1. Tap the "Copy Data" button below<br>
                                        2. Open Notes app and create a new note<br>
                                        3. Paste the data and save as "${fileName}"<br>
                                        4. You can also share this page using the share button in Safari
                                    </div>
                                    <button class="copy-btn" onclick="copyData()">📋 Copy Data</button>
                                    <div class="data-container">
                                        <textarea id="exportData" readonly>${dataStr}</textarea>
                                    </div>
                                </div>
                                <script>
                                    function copyData() {
                                        const textarea = document.getElementById('exportData');
                                        textarea.select();
                                        textarea.setSelectionRange(0, 99999);
                                        try {
                                            document.execCommand('copy');
                                            alert('Data copied to clipboard! You can now paste it in Notes app.');
                                        } catch (err) {
                                            alert('Copy failed. Please select all text and copy manually.');
                                        }
                                    }
                                </script>
                            </body>
                        </html>
                    `);
                    window.URL.revokeObjectURL(url);
                } else {
                    // Desktop: Use traditional download method
                    const dataBlob = new Blob([dataStr], {type: 'application/json'});
                    const url = window.URL.createObjectURL(dataBlob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                }
                
                this.showNotification('Data exported successfully!', 'success');
            } else {
                this.showNotification(data.message || 'Export failed', 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Export failed', 'error');
        }
    }

    async importData(file) {
        if (!file) {
            this.showNotification('Please select a file', 'warning');
            return;
        }

        if (!file.name.endsWith('.json')) {
            this.showNotification('Please select a JSON file', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/import', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(result.message, 'success');
                // Reload data after successful import
                await this.loadTasks();
                await this.loadChatHistory();
            } else {
                this.showNotification(result.message || 'Import failed', 'error');
            }
        } catch (error) {
            console.error('Import error:', error);
            this.showNotification('Import failed', 'error');
        } finally {
            // Clear the file input
            document.getElementById('importFileInput').value = '';
        }
    }

    async toggleVoiceRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.sendAudioMessage(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            
            const voiceBtn = document.getElementById('voiceBtn');
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.classList.remove('btn-outline-secondary');
            voiceBtn.classList.add('btn-danger');
            
            this.showNotification('Recording... Click again to stop', 'info');
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.showNotification('Microphone access denied or not available', 'error');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            const voiceBtn = document.getElementById('voiceBtn');
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.classList.remove('btn-danger');
            voiceBtn.classList.add('btn-outline-secondary');
        }
    }

    async sendAudioMessage(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        try {
            this.showNotification('Processing audio...', 'info');
            
            const response = await fetch('/api/chat/audio', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                // Add user message (transcribed text)
                this.addChatMessage(data.transcript, true);
                
                // Add bot response
                this.addChatMessage(data.response, false);
                
                // Play audio response if available
                if (data.audio) {
                    this.playAudioResponse(data.audio);
                }
                
                this.showNotification('Voice message processed!', 'success');
            } else {
                this.showNotification(data.message || 'Voice processing failed', 'error');
            }
        } catch (error) {
            console.error('Audio message error:', error);
            this.showNotification('Voice message failed', 'error');
        }
    }

    playAudioResponse(audioData) {
        try {
            // Convert base64 audio data to blob and play
            const audioBytes = atob(audioData);
            const audioArray = new Uint8Array(audioBytes.length);
            for (let i = 0; i < audioBytes.length; i++) {
                audioArray[i] = audioBytes.charCodeAt(i);
            }
            
            const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            audio.play().then(() => {
                console.log('Audio response played');
            }).catch(error => {
                console.error('Audio playback error:', error);
            });
            
            // Clean up URL after playing
            audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
            };
        } catch (error) {
            console.error('Audio decode error:', error);
        }
    }

    async scheduleTask(taskId) {
        const dueDate = prompt('Enter due date (YYYY-MM-DD):');
        if (!dueDate) return;

        const reminderTime = prompt('Enter reminder time (optional, YYYY-MM-DD HH:MM):');

        try {
            const scheduleData = { due_date: dueDate + 'T00:00:00' };
            if (reminderTime) {
                scheduleData.reminder_time = reminderTime + ':00';
            }

            const response = await fetch(`/api/tasks/${taskId}/schedule`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(scheduleData)
            });

            const data = await response.json();
            
            if (data.success) {
                const taskIndex = this.tasks.findIndex(t => t.id === taskId);
                if (taskIndex !== -1) {
                    this.tasks[taskIndex] = data.task;
                    this.renderTasks();
                }
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error scheduling task:', error);
            this.showNotification('Error scheduling task', 'error');
        }
    }

    async loadSchedulingSuggestions() {
        try {
            const response = await fetch('/api/tasks/suggestions');
            const data = await response.json();
            
            if (data.success && data.suggestions.length > 0) {
                this.showSchedulingSuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Error loading suggestions:', error);
        }
    }

    showSchedulingSuggestions(suggestions) {
        let message = "Smart Scheduling Suggestions:\n\n";
        suggestions.forEach(suggestion => {
            message += `• ${suggestion.message}\n`;
        });
        
        if (confirm(message + "\nWould you like to schedule some tasks now?")) {
            // User can manually schedule tasks using the interface
            this.showNotification('Use the clock icon next to tasks to schedule them!', 'info');
        }
    }

    async showLearningInsights() {
        try {
            const response = await fetch('/api/analytics/learning-insights');
            const data = await response.json();
            
            if (data.success) {
                const insights = data.insights;
                const analyticsDisplay = document.getElementById('analyticsDisplay');
                
                let html = '<div class="learning-insights">';
                html += '<h6 class="text-info mb-3"><i class="fas fa-brain me-2"></i>Learning Insights</h6>';
                
                // Conversation stats
                html += `<div class="mb-3">
                    <small class="text-muted">Total Messages:</small> <strong>${insights.conversation_stats.total_messages}</strong><br>
                    <small class="text-muted">Total Tasks:</small> <strong>${insights.conversation_stats.total_tasks}</strong>
                </div>`;
                
                // Patterns
                if (Object.keys(insights.patterns).length > 0) {
                    html += '<div class="mb-3"><small class="text-muted">Learned Patterns:</small><br>';
                    for (const [key, value] of Object.entries(insights.patterns)) {
                        html += `<span class="badge bg-secondary me-1">${key}: ${value}</span>`;
                    }
                    html += '</div>';
                } else {
                    html += '<div class="text-muted small mb-3">Keep chatting to help me learn your preferences!</div>';
                }
                
                html += '</div>';
                analyticsDisplay.innerHTML = html;
                
                this.showNotification('Learning insights loaded!', 'success');
            } else {
                this.showNotification(data.message || 'Could not load learning insights', 'error');
            }
        } catch (error) {
            console.error('Error loading learning insights:', error);
            this.showNotification('Error loading insights', 'error');
        }
    }

    toggleNotifications() {
        this.notificationsEnabled = !this.notificationsEnabled;
        localStorage.setItem('notificationsEnabled', this.notificationsEnabled);
        
        if (this.notificationsEnabled) {
            this.showNotification('Notifications enabled', 'success');
        } else {
            // Show this one even when disabled to confirm the toggle
            const toast = document.getElementById('notificationToast');
            const toastBody = document.getElementById('toastBody');
            toastBody.textContent = 'Notifications disabled';
            toast.classList.remove('text-bg-success', 'text-bg-danger', 'text-bg-warning', 'text-bg-info');
            toast.classList.add('text-bg-warning');
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }

    async showPredictiveInsights() {
        try {
            const response = await fetch('/api/analytics/predictive-insights');
            const data = await response.json();
            
            if (data.success) {
                const predictions = data.predictions;
                const analyticsDisplay = document.getElementById('analyticsDisplay');
                
                let html = '<div class="predictive-insights">';
                html += '<h6 class="text-warning mb-3"><i class="fas fa-crystal-ball me-2"></i>Predictive Insights</h6>';
                
                html += `<div class="mb-3">
                    <div class="card bg-dark border-secondary">
                        <div class="card-body p-3">
                            <h6 class="card-title text-info">Productivity Trends</h6>
                            <p class="card-text small">${predictions.task_completion_trend}</p>
                        </div>
                    </div>
                </div>`;
                
                html += `<div class="mb-3">
                    <div class="card bg-dark border-secondary">
                        <div class="card-body p-3">
                            <h6 class="card-title text-info">Conversation Patterns</h6>
                            <p class="card-text small">${predictions.conversation_patterns}</p>
                        </div>
                    </div>
                </div>`;
                
                if (predictions.suggested_improvements && predictions.suggested_improvements.length > 0) {
                    html += '<div class="mb-3"><h6 class="text-success">Suggested Improvements</h6><ul class="list-unstyled">';
                    predictions.suggested_improvements.forEach(improvement => {
                        html += `<li class="small text-muted mb-1"><i class="fas fa-lightbulb text-warning me-2"></i>${improvement}</li>`;
                    });
                    html += '</ul></div>';
                }
                
                html += '</div>';
                analyticsDisplay.innerHTML = html;
                
                this.showNotification('Predictive insights loaded!', 'success');
            } else {
                this.showNotification(data.message || 'Could not load predictive insights', 'error');
            }
        } catch (error) {
            console.error('Error loading predictive insights:', error);
            this.showNotification('Error loading predictive insights', 'error');
        }
    }

    handleFileAttachment(files) {
        let fileInfo = [];
        for (let file of files) {
            fileInfo.push(`📎 ${file.name} (${(file.size / 1024).toFixed(1)}KB)`);
        }
        
        const chatInput = document.getElementById('chatInput');
        const currentValue = chatInput.value;
        const newValue = currentValue + (currentValue ? '\n' : '') + fileInfo.join('\n');
        chatInput.value = newValue;
        
        this.showNotification(`${files.length} file(s) attached`, 'success');
        
        // Clear file input for next use
        document.getElementById('fileInput').value = '';
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.speechRecognition = new SpeechRecognition();
            
            // Settings for continuous listening
            this.speechRecognition.continuous = true;
            this.speechRecognition.interimResults = true;
            this.speechRecognition.lang = 'en-US';
            this.speechRecognition.maxAlternatives = 1;
            
            this.speechRecognition.onstart = () => {
                this.isListeningActive = true;
                this.updateListeningIndicator(true);
                console.log('Speech recognition started');
            };
            
            this.speechRecognition.onresult = (event) => {
                this.handleSpeechResults(event);
            };
            
            this.speechRecognition.onerror = (event) => {
                this.handleSpeechError(event);
            };
            
            this.speechRecognition.onend = () => {
                this.handleSpeechEnd();
            };
        } else {
            console.log('Speech recognition not supported on this device');
        }
    }

    initializeVoiceConversationMode() {
        // Initialize mute button state
        this.updateMuteButton();
        
        const voiceConversationBtn = document.getElementById('voiceConversationBtn');
        if (voiceConversationBtn) {
            if (this.voiceConversationMode) {
                voiceConversationBtn.classList.add('btn-voice-active');
                voiceConversationBtn.querySelector('i').className = 'fas fa-comments';
            }
        }
    }

    toggleMute() {
        this.isMuted = !this.isMuted;
        localStorage.setItem('speechMuted', this.isMuted.toString());
        
        if (this.isMuted) {
            this.pauseContinuousListening();
        } else {
            this.resumeContinuousListening();
        }
        
        this.updateMuteButton();
        this.showNotification(
            this.isMuted ? 'Speech recognition muted' : 'Speech recognition active',
            'info'
        );
    }

    updateMuteButton() {
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            const icon = voiceBtn.querySelector('i');
            if (this.isMuted) {
                voiceBtn.classList.remove('btn-voice-active');
                voiceBtn.classList.add('btn-muted');
                icon.className = 'fas fa-microphone-slash';
                voiceBtn.title = 'Speech recognition is muted - click to unmute';
            } else {
                voiceBtn.classList.add('btn-voice-active');
                voiceBtn.classList.remove('btn-muted');
                icon.className = 'fas fa-microphone';
                voiceBtn.title = 'Speech recognition is active - click to mute';
            }
        }
    }





    toggleContinuousListening() {
        // Voice button now functions as mute/unmute
        this.toggleMute();
    }

    startContinuousListening() {
        if (!this.speechRecognition || this.isListeningActive) return;
        
        try {
            this.speechRecognition.continuous = true;
            this.speechRecognition.interimResults = true;
            this.speechRecognition.start();
            this.isListeningActive = true;
        } catch (error) {
            console.error('Failed to start continuous listening:', error);
            this.showNotification('Could not start microphone', 'error');
        }
    }

    stopContinuousListening() {
        if (this.speechRecognition && this.isListeningActive) {
            this.speechRecognition.stop();
            this.isListeningActive = false;
        }
    }

    updateVoiceButton() {
        const voiceBtn = document.getElementById('voiceBtn');
        const icon = voiceBtn.querySelector('i');
        
        if (this.continuousListening) {
            voiceBtn.classList.add('btn-voice-active');
            icon.className = 'fas fa-microphone';
            voiceBtn.title = 'Continuous listening ON - Click to turn off';
        } else {
            voiceBtn.classList.remove('btn-voice-active');
            icon.className = 'fas fa-microphone-slash';
            voiceBtn.title = 'Click to enable continuous listening';
        }
    }

    updateContinuousListenButton() {
        const continuousListenBtn = document.getElementById('continuousListenBtn');
        if (continuousListenBtn) {
            if (this.continuousListening) {
                continuousListenBtn.classList.add('btn-listen-active');
                continuousListenBtn.querySelector('i').className = 'fas fa-ear-listen';
            } else {
                continuousListenBtn.classList.remove('btn-listen-active');
                continuousListenBtn.querySelector('i').className = 'far fa-ear-listen';
            }
        }
    }

    pauseContinuousListening() {
        if (this.speechRecognition && this.isListeningActive) {
            this.speechRecognition.stop();
            this.isListeningActive = false;
            this.updateListeningIndicator(false);
        }
    }

    resumeContinuousListening() {
        if (this.isMuted || this.isListeningActive) {
            return;
        }

        setTimeout(() => {
            if (!this.isMuted && !this.isListeningActive) {
                this.startContinuousListening();
            }
        }, 500);
    }

    handleSpeechResults(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        
        // Process all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update visual feedback for interim results
        if (interimTranscript) {
            this.updateInterimTranscript(interimTranscript);
        }
        
        // Process final transcript
        if (finalTranscript.trim()) {
            this.clearInterimTranscript();
            this.processFinalTranscript(finalTranscript.trim());
        }
    }

    processFinalTranscript(transcript) {
        const now = Date.now();
        this.lastSpeechTime = now;
        
        // Clear any existing silence timeout
        if (this.silenceTimeout) {
            clearTimeout(this.silenceTimeout);
        }
        
        // Add to voice buffer for batching short phrases
        this.voiceBuffer.push({
            text: transcript,
            timestamp: now,
            confidence: this.getLastConfidence()
        });
        
        // Set timeout to process buffered speech
        this.silenceTimeout = setTimeout(() => {
            this.processVoiceBuffer();
        }, 1500); // Wait 1.5 seconds for additional speech
    }

    processVoiceBuffer() {
        if (this.voiceBuffer.length === 0) return;
        
        // Combine buffered speech into one message
        const combinedText = this.voiceBuffer.map(item => item.text).join(' ').trim();
        const avgConfidence = this.voiceBuffer.reduce((sum, item) => sum + item.confidence, 0) / this.voiceBuffer.length;
        
        // Clear buffer
        this.voiceBuffer = [];
        
        // Only process if confidence is above threshold
        if (avgConfidence >= this.voiceActivationSensitivity && combinedText.length > 2) {
            this.handleVoiceInput(combinedText);
        }
    }

    getLastConfidence() {
        // Fallback confidence if not available
        return 0.8;
    }

    updateInterimTranscript(text) {
        const indicator = document.getElementById('listeningIndicator');
        if (indicator) {
            indicator.textContent = `Listening: "${text}"`;
            indicator.style.opacity = '0.7';
        }
    }

    clearInterimTranscript() {
        const indicator = document.getElementById('listeningIndicator');
        if (indicator) {
            indicator.textContent = 'Listening...';
            indicator.style.opacity = '1';
        }
    }

    handleSpeechError(event) {
        this.isListeningActive = false;
        this.updateListeningIndicator(false);
        
        if (event.error === 'no-speech') {
            // Normal - just restart silently
            if (!this.isMuted) {
                setTimeout(() => this.startContinuousListening(), 1000);
            }
        } else if (event.error === 'aborted') {
            // Normal stop - restart unless muted
            if (!this.isMuted) {
                setTimeout(() => this.startContinuousListening(), 500);
            }
        } else if (event.error === 'audio-capture') {
            this.showNotification('Microphone access denied. Please enable microphone permissions.', 'error');
            this.isMuted = true;
            this.updateMuteButton();
        } else if (event.error === 'not-allowed') {
            this.showNotification('Microphone permission denied. Please allow microphone access and try again.', 'error');
            this.isMuted = true;
            this.updateMuteButton();
        } else {
            console.error('Speech recognition error:', event.error);
            // Keep trying to restart unless muted
            if (!this.isMuted) {
                setTimeout(() => this.startContinuousListening(), 2000);
            }
        }
    }

    disableSpeechMode() {
        this.continuousListening = false;
        const speechBtn = document.getElementById('speechBtn');
        const icon = speechBtn.querySelector('i');
        
        speechBtn.classList.remove('btn-listen-active');
        icon.className = 'fas fa-microphone';
        speechBtn.title = 'Speech Mode - Click to Enable';
        
        localStorage.setItem('continuousListening', false);
    }

    handleSpeechEnd() {
        this.isListeningActive = false;
        this.updateListeningIndicator(false);
        
        // Always restart speech recognition unless muted
        if (!this.isMuted) {
            setTimeout(() => {
                this.startContinuousListening();
            }, 500);
        }
    }



    startVoiceListening() {
        if (!this.speechRecognition) {
            this.showNotification('Speech recognition not supported', 'error');
            return;
        }

        if (this.isSpeaking) {
            this.showNotification('Please wait for me to finish speaking', 'warning');
            return;
        }

        // Stop continuous listening temporarily if active
        if (this.continuousListening) {
            this.speechRecognition.stop();
        }

        try {
            // Create a new instance for single use
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const singleUseRecognition = new SpeechRecognition();
            
            singleUseRecognition.continuous = false;
            singleUseRecognition.interimResults = false;
            singleUseRecognition.lang = 'en-US';
            
            singleUseRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleVoiceInput(transcript);
            };
            
            singleUseRecognition.onerror = (event) => {
                if (event.error === 'no-speech') {
                    this.showNotification('No speech detected. Try again.', 'warning');
                } else {
                    this.showNotification('Voice recognition failed', 'error');
                }
                // Restart continuous listening if it was active
                if (this.continuousListening) {
                    setTimeout(() => this.startContinuousListening(), 1000);
                }
            };
            
            singleUseRecognition.onend = () => {
                // Restart continuous listening if it was active
                if (this.continuousListening) {
                    setTimeout(() => this.startContinuousListening(), 500);
                }
            };
            
            singleUseRecognition.start();
            this.showNotification('Listening... Speak now', 'info');
        } catch (error) {
            console.error('Failed to start voice listening:', error);
            this.showNotification('Voice recognition failed to start', 'error');
        }
    }

    stopVoiceListening() {
        if (this.speechRecognition) {
            this.speechRecognition.stop();
        }
    }

    async handleVoiceInput(transcript) {
        if (!transcript.trim()) return;
        
        // Temporarily pause listening to avoid feedback
        this.pauseContinuousListening();
        
        // Show processing indicator
        this.showVoiceProcessing(true);
        
        // Add user message to chat
        this.addChatMessage(transcript, true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: transcript })
            });

            const data = await response.json();
            
            if (data.success) {
                this.addChatMessage(data.response, false);
                
                // Enhanced TTS with emotional context
                if (this.ttsEnabled) {
                    this.speakTextWithEmotion(data.response, data.emotion);
                } else {
                    // Resume listening if not speaking
                    this.resumeListeningAfterResponse();
                }
            } else {
                this.showNotification(data.message || 'Chat failed', 'error');
                this.resumeListeningAfterResponse();
            }
        } catch (error) {
            console.error('Voice chat error:', error);
            this.showNotification('Voice chat failed', 'error');
            this.resumeListeningAfterResponse();
        } finally {
            this.showVoiceProcessing(false);
        }
    }

    speakTextWithEmotion(text, emotion) {
        if (!this.ttsEnabled || !text) return;
        
        this.isSpeaking = true;
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Adjust voice parameters based on emotion
        const emotionVoiceSettings = {
            'joy': { rate: 1.1, pitch: 1.2, volume: 0.9 },
            'sadness': { rate: 0.8, pitch: 0.8, volume: 0.7 },
            'anger': { rate: 1.2, pitch: 0.9, volume: 1.0 },
            'fear': { rate: 1.1, pitch: 1.1, volume: 0.8 },
            'curiosity': { rate: 1.0, pitch: 1.0, volume: 0.8 },
            'empathy': { rate: 0.9, pitch: 0.9, volume: 0.8 },
            'serenity': { rate: 0.8, pitch: 0.9, volume: 0.7 }
        };
        
        const settings = emotionVoiceSettings[emotion] || { rate: 1.0, pitch: 1.0, volume: 0.8 };
        
        utterance.rate = settings.rate;
        utterance.pitch = settings.pitch;
        utterance.volume = settings.volume;
        
        // Visual feedback
        const avatarSvg = document.querySelector('.avatar-container svg');
        if (avatarSvg) avatarSvg.classList.add('avatar-speaking');
        
        utterance.onstart = () => {
            this.updateListeningIndicator(false, 'Speaking...');
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
            if (avatarSvg) avatarSvg.classList.remove('avatar-speaking');
            // Speech recognition continues running - no need to restart
        };
        
        utterance.onerror = () => {
            this.isSpeaking = false;
            if (avatarSvg) avatarSvg.classList.remove('avatar-speaking');
            // Speech recognition continues running - no need to restart
        };
        
        speechSynthesis.speak(utterance);
    }

    resumeListeningAfterResponse() {
        if (this.continuousListening || this.voiceConversationMode) {
            setTimeout(() => {
                this.resumeContinuousListening();
            }, 500); // Brief pause before resuming
        }
    }

    showVoiceProcessing(show) {
        const indicator = document.getElementById('listeningIndicator');
        if (indicator) {
            if (show) {
                indicator.textContent = 'Processing...';
                indicator.className = 'listening-indicator processing';
            } else {
                this.updateListeningIndicator(this.isListeningActive);
            }
        }
    }

    updateListeningIndicator(isListening, customText = null) {
        const indicator = document.getElementById('listeningIndicator');
        if (!indicator) {
            // Create indicator if it doesn't exist
            this.createListeningIndicator();
            return;
        }
        
        if (customText) {
            indicator.textContent = customText;
            indicator.className = 'listening-indicator custom';
        } else if (isListening) {
            indicator.textContent = 'Listening...';
            indicator.className = 'listening-indicator active';
        } else {
            indicator.textContent = 'Voice Ready';
            indicator.className = 'listening-indicator inactive';
        }
    }

    createListeningIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'listeningIndicator';
        indicator.className = 'listening-indicator inactive';
        indicator.textContent = 'Voice Ready';
        
        // Add to chat container
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            chatContainer.insertBefore(indicator, chatContainer.firstChild);
        }
    }

    toggleSpeechMode() {
        if (!this.speechRecognition) {
            this.showNotification('Speech not supported on this device', 'error');
            return;
        }

        const speechBtn = document.getElementById('speechBtn');
        const icon = speechBtn.querySelector('i');

        if (!this.continuousListening) {
            // Enable one-time speech mode for iPhone
            this.continuousListening = true;
            this.ttsEnabled = true;
            
            speechBtn.classList.add('btn-listen-active');
            icon.className = 'fas fa-microphone-alt';
            speechBtn.title = 'Speech Mode - Tap to Talk';
            
            this.showNotification('Speech mode enabled - click microphone to talk', 'success');
            
            // Store preferences
            localStorage.setItem('continuousListening', true);
            localStorage.setItem('ttsEnabled', true);
        } else {
            // Disable speech mode
            this.continuousListening = false;
            this.ttsEnabled = false;
            
            speechBtn.classList.remove('btn-listen-active');
            icon.className = 'fas fa-microphone';
            speechBtn.title = 'Speech Mode - Click to Enable';
            
            this.stopContinuousListening();
            this.showNotification('Speech mode disabled', 'info');
            
            // Store preferences
            localStorage.setItem('continuousListening', false);
            localStorage.setItem('ttsEnabled', false);
        }
    }

    restoreSpeechMode() {
        const speechBtn = document.getElementById('speechBtn');
        const icon = speechBtn.querySelector('i');
        
        if (speechBtn && this.continuousListening) {
            speechBtn.classList.add('btn-listen-active');
            icon.className = 'fas fa-microphone-alt';
            speechBtn.title = 'Speech Mode Active - Always Listening';
            
            this.ttsEnabled = true;
            this.startContinuousListening();
        }
    }



    removeChatMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.remove();
        }
    }



    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RobotoApp();
});
