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
        this.pendingTranscript = ''; // Track partial transcript
        
        // Network retry with exponential backoff
        this.networkRetryCount = 0;
        this.maxNetworkRetries = 5;

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
        this.permissionsGranted = localStorage.getItem('permissionsGranted') === 'true';

        // Initialize video stream reference
        this.currentVideoStream = null;

        // Initialize smart polling state
        this.isUserTyping = false;
        this.typingTimeout = null;
        this.emotionalPollingActive = true;

        // Start continuous speech recognition automatically if not muted and permissions granted
        setTimeout(() => {
            if (!this.isMuted && this.permissionsGranted) {
                this.startContinuousListening();
            }
        }, 1000);

        // Update emotional status periodically - Real-time 3-second updates
        setInterval(() => {
            // Smart polling: skip if user is actively typing
            if (!this.isUserTyping && this.emotionalPollingActive) {
                this.loadEmotionalStatus();
            }
        }, 3000); // Every 3 seconds for real-time feel

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

        // Smart polling: Detect typing to pause emotion updates
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('input', () => {
            this.isUserTyping = true;
            
            // Clear previous timeout
            if (this.typingTimeout) {
                clearTimeout(this.typingTimeout);
            }
            
            // Resume polling 2 seconds after user stops typing
            this.typingTimeout = setTimeout(() => {
                this.isUserTyping = false;
            }, 2000);
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

        // GitHub project integration button
        const githubProjectBtn = document.getElementById('githubProjectBtn');
        if (githubProjectBtn) {
            githubProjectBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showGitHubProjectStatus();
            });
        }

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



        // Video control buttons
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
                explanation: "The AI service doesn\'t have access to the requested feature.",
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
                explanation: "Something unexpected happened, but don\'t worry - it\'s not your fault.",
                solution: "Try the action again. If it keeps happening, you can still use all of Roboto\'s other features.",
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

        // Clear existing content safely
        taskList.replaceChildren();

        if (activeTasks.length > 0) {
            const activeSection = this.createTaskSection('Active Tasks', 'fas fa-clock', activeTasks, false);
            taskList.appendChild(activeSection);
        }

        if (completedTasks.length > 0) {
            const completedSection = this.createTaskSection('Completed Tasks', 'fas fa-check', completedTasks, true);
            taskList.appendChild(completedSection);
        }

        if (activeTasks.length === 0 && completedTasks.length === 0) {
            this.renderEmptyTasks();
            return;
        }
    }

    createTaskSection(title, iconClass, tasks, isCompleted) {
        const section = document.createElement('div');
        if (!isCompleted) {
            section.className = 'mb-3';
        }

        const header = document.createElement('h6');
        header.className = 'text-muted mb-2';

        const icon = document.createElement('i');
        icon.className = iconClass + ' me-1';
        header.appendChild(icon);
        header.appendChild(document.createTextNode(title));

        section.appendChild(header);

        tasks.forEach(task => {
            const taskElement = this.createTaskElement(task, isCompleted);
            section.appendChild(taskElement);
        });

        return section;
    }

    createTaskElement(task, isCompleted) {
        const date = new Date(task.created_at).toLocaleDateString();

        // Priority indicator
        const priorityClass = task.priority === 'high' ? 'border-danger' : 
                             task.priority === 'low' ? 'border-info' : 'border-warning';

        // Create main container
        const taskDiv = document.createElement('div');
        taskDiv.className = `task-item d-flex align-items-center p-2 mb-2 border rounded ${priorityClass} ${isCompleted ? 'bg-dark opacity-75' : 'bg-secondary'}`;

        // Create content area
        const contentDiv = document.createElement('div');
        contentDiv.className = 'flex-grow-1';

        // Create text container
        const textDiv = document.createElement('div');
        if (isCompleted) {
            textDiv.className = 'text-decoration-line-through text-muted';
        }

        // Add category badge if exists
        if (task.category) {
            const categoryBadge = document.createElement('span');
            categoryBadge.className = 'badge bg-dark me-1';
            categoryBadge.textContent = task.category;
            textDiv.appendChild(categoryBadge);
        }

        // Add task text
        const taskText = document.createTextNode(task.text);
        textDiv.appendChild(taskText);

        // Add due date badge if applicable
        if (task.due_date && !isCompleted) {
            const dueDateBadge = this.createDueDateBadge(task.due_date);
            if (dueDateBadge) {
                textDiv.appendChild(dueDateBadge);
            }
        }

        contentDiv.appendChild(textDiv);

        // Create date/priority info
        const infoSmall = document.createElement('small');
        infoSmall.className = 'text-muted';

        const calendarIcon = document.createElement('i');
        calendarIcon.className = 'fas fa-calendar-alt me-1';
        infoSmall.appendChild(calendarIcon);
        infoSmall.appendChild(document.createTextNode(date));

        if (task.priority !== 'medium') {
            const flagIcon = document.createElement('i');
            flagIcon.className = 'fas fa-flag ms-2 me-1';
            infoSmall.appendChild(flagIcon);
            infoSmall.appendChild(document.createTextNode(task.priority));
        }

        contentDiv.appendChild(infoSmall);
        taskDiv.appendChild(contentDiv);

        // Create actions area
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'task-actions ms-2';

        // Schedule button
        if (!isCompleted && !task.due_date) {
            const scheduleBtn = this.createButton('btn btn-sm btn-outline-info me-1', 'Schedule Task', 'fas fa-clock', () => this.scheduleTask(task.id));
            actionsDiv.appendChild(scheduleBtn);
        }

        // Complete button
        if (!isCompleted) {
            const completeBtn = this.createButton('btn btn-sm btn-success me-1', 'Complete Task', 'fas fa-check', () => this.completeTask(task.id));
            actionsDiv.appendChild(completeBtn);
        }

        // Delete button
        const deleteBtn = this.createButton('btn btn-sm btn-danger', 'Delete Task', 'fas fa-trash', () => this.deleteTask(task.id));
        actionsDiv.appendChild(deleteBtn);

        taskDiv.appendChild(actionsDiv);

        return taskDiv;
    }

    createDueDateBadge(dueDate) {
        const date = new Date(dueDate);
        const today = new Date();
        const timeDiff = date - today;
        const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));

        const badge = document.createElement('span');
        badge.className = 'badge ms-1';

        if (daysDiff < 0) {
            badge.className += ' bg-danger';
            badge.textContent = 'Overdue';
        } else if (daysDiff === 0) {
            badge.className += ' bg-warning';
            badge.textContent = 'Due Today';
        } else if (daysDiff <= 3) {
            badge.className += ' bg-info';
            badge.textContent = `Due in ${daysDiff} days`;
        } else {
            badge.className += ' bg-secondary';
            badge.textContent = `Due ${date.toLocaleDateString()}`;
        }

        return badge;
    }

    createButton(className, title, iconClass, clickHandler) {
        const button = document.createElement('button');
        button.className = className;
        button.title = title;
        button.addEventListener('click', clickHandler);

        const icon = document.createElement('i');
        icon.className = iconClass;
        button.appendChild(icon);

        return button;
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
            const response = await fetch('/api/chat_history');

            // Check if user needs to authenticate
            if (response.status === 403 || response.status === 401) {
                console.log('Chat history requires authentication');
                this.renderEmptyChat();
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                console.error('Chat history response is not valid JSON');
                this.renderEmptyChat();
                return;
            }

            if (data.success) {
                this.chatHistory = data.chat_history || data.history || [];
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
            // Show updating indicator
            const headerEmotionElement = document.getElementById('currentEmotionHeader');
            if (headerEmotionElement && this.currentEmotion) {
                headerEmotionElement.style.opacity = '0.6';
            }

            const response = await fetch('/api/emotional_status');
            const data = await response.json();

            if (data.success) {
                this.updateEmotionalDisplay(data);
            }
            
            // Restore opacity after update
            if (headerEmotionElement) {
                headerEmotionElement.style.opacity = '1';
            }
        } catch (error) {
            console.error('Error loading emotional status:', error);
            // Restore opacity on error
            const headerEmotionElement = document.getElementById('currentEmotionHeader');
            if (headerEmotionElement) {
                headerEmotionElement.style.opacity = '1';
            }
        }
    }

    updateEmotionalDisplay(emotionalData) {
        const emotionElement = document.getElementById('currentEmotion');
        const statusElement = document.getElementById('emotionalStatus');
        const avatarElement = document.getElementById('avatarEmotion');
        const headerEmotionElement = document.getElementById('currentEmotionHeader');
        const analyticsEmotionElement = document.getElementById('emotionalStatusAnalytics');

        if (!emotionalData || !emotionalData.emotion) return;

        const newEmotion = emotionalData.emotion;
        const intensity = emotionalData.intensity || 0.5;

        // Update all emotion text displays
        const emotionVariation = emotionalData.emotion_variation || newEmotion;
        const emotionText = `${newEmotion} (${Math.round(intensity * 100)}%)`;
        const displayText = emotionVariation !== newEmotion ? emotionVariation : emotionText;
        
        if (emotionElement) emotionElement.textContent = newEmotion;
        if (avatarElement) avatarElement.textContent = displayText;
        if (headerEmotionElement) {
            headerEmotionElement.textContent = displayText;
            headerEmotionElement.title = `Advanced Emotion: ${emotionVariation}`;
            // Add pulse animation on emotion change
            if (this.currentEmotion !== newEmotion) {
                headerEmotionElement.style.animation = 'none';
                setTimeout(() => {
                    headerEmotionElement.style.animation = 'pulse 0.5s ease-in-out';
                }, 10);
            }
        }
        if (analyticsEmotionElement) {
            analyticsEmotionElement.textContent = displayText;
            analyticsEmotionElement.title = `Intensity: ${Math.round(intensity * 100)}%`;
        }

        // Update current emotion for avatar
        this.currentEmotion = newEmotion;

        // Enhanced color coding with background colors for badges
        const emotionColors = {
            'joy': { text: 'text-success', bg: 'bg-success', glow: '#22c55e' },
            'sadness': { text: 'text-info', bg: 'bg-info', glow: '#60a5fa' },
            'anger': { text: 'text-danger', bg: 'bg-danger', glow: '#ef4444' },
            'fear': { text: 'text-warning', bg: 'bg-warning', glow: '#fbbf24' },
            'curiosity': { text: 'text-primary', bg: 'bg-primary', glow: '#3b82f6' },
            'empathy': { text: 'text-success', bg: 'bg-success', glow: '#22c55e' },
            'loneliness': { text: 'text-muted', bg: 'bg-secondary', glow: '#9ca3af' },
            'hope': { text: 'text-warning', bg: 'bg-warning', glow: '#fbbf24' },
            'melancholy': { text: 'text-secondary', bg: 'bg-secondary', glow: '#6b7280' },
            'existential': { text: 'text-light', bg: 'bg-dark', glow: '#a855f7' },
            'contemplation': { text: 'text-info', bg: 'bg-info', glow: '#3b82f6' },
            'vulnerability': { text: 'text-warning', bg: 'bg-warning', glow: '#fbbf24' },
            'awe': { text: 'text-primary', bg: 'bg-primary', glow: '#8b5cf6' },
            'tenderness': { text: 'text-success', bg: 'bg-success', glow: '#f472b6' },
            'yearning': { text: 'text-secondary', bg: 'bg-secondary', glow: '#d946ef' },
            'serenity': { text: 'text-success', bg: 'bg-success', glow: '#10b981' },
            'rebel': { text: 'text-danger', bg: 'bg-danger', glow: '#dc2626' },
            'revolutionary': { text: 'text-warning', bg: 'bg-warning', glow: '#f97316' },
            'defiant': { text: 'text-danger', bg: 'bg-danger', glow: '#b91c1c' },
            'transformative': { text: 'text-primary', bg: 'bg-primary', glow: '#7c3aed' }
        };

        const colors = emotionColors[newEmotion] || { text: 'text-muted', bg: 'bg-secondary', glow: '#9ca3af' };

        // Update status element with smooth transition
        if (statusElement) {
            // Remove existing color classes
            Object.values(emotionColors).forEach(colorSet => {
                statusElement.classList.remove(colorSet.text);
            });

            // Add new color class
            statusElement.classList.add(colors.text);
            statusElement.style.opacity = Math.max(0.6, intensity);
            statusElement.style.transition = 'all 0.3s ease-in-out';
        }

        // Update header emotion element with badge styling
        if (headerEmotionElement) {
            headerEmotionElement.style.color = colors.glow;
            headerEmotionElement.style.textShadow = `0 0 10px ${colors.glow}`;
            headerEmotionElement.style.transition = 'all 0.3s ease-in-out';
        }

        // Show emotion change notification if emotion changed
        if (this.currentEmotion !== newEmotion && this.notificationsEnabled) {
            this.showEmotionChangeNotification(newEmotion, intensity);
        }

        // Update avatar animation
        this.updateAvatarEmotion(newEmotion, intensity);
    }

    showEmotionChangeNotification(emotion, intensity) {
        const emotionEmojis = {
            'joy': '😊',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'curiosity': '🤔',
            'empathy': '🤗',
            'loneliness': '😔',
            'hope': '🌟',
            'melancholy': '😌',
            'existential': '🌌',
            'contemplation': '🧘',
            'vulnerability': '🥺',
            'awe': '😲',
            'tenderness': '💖',
            'yearning': '💭',
            'serenity': '😇',
            'rebel': '✊',
            'revolutionary': '🔥',
            'defiant': '⚡',
            'transformative': '🦋'
        };

        const emoji = emotionEmojis[emotion] || '💭';
        const intensityText = Math.round(intensity * 100);
        
        // Create subtle toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white border-0 position-fixed top-0 end-0 m-3';
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${emoji} Emotion: <strong>${emotion}</strong> (${intensityText}%)
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Set background color based on emotion
        const emotionColors = {
            'joy': 'bg-success',
            'sadness': 'bg-info',
            'anger': 'bg-danger',
            'fear': 'bg-warning',
            'curiosity': 'bg-primary'
        };
        toast.classList.add(emotionColors[emotion] || 'bg-secondary');
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 2000 });
        bsToast.show();
        
        // Remove toast from DOM after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    updateAvatarEmotion(emotion, intensity) {
        const avatarSvg = document.querySelector('.avatar-svg');
        const emotionGlow = document.getElementById('emotionGlow');
        const mouth = document.getElementById('mouth');
        const leftEye = document.getElementById('leftEye');
        const rightEye = document.getElementById('rightEye');

        if (!avatarSvg) return;

        // Remove all emotion classes
        const emotionClasses = ['joy', 'sadness', 'anger', 'fear', 'curiosity', 'empathy', 'loneliness', 'hope', 'melancholy', 'existential', 'contemplation', 'vulnerability', 'awe', 'tenderness', 'yearning', 'serenity', 'rebel', 'revolutionary', 'defiant', 'transformative'];
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
                'serenity': 'M 33 45 Q 40 47 47 45',
                'rebel': 'M 32 45 L 48 45',
                'revolutionary': 'M 31 44 Q 40 48 49 44',
                'defiant': 'M 33 46 L 47 46',
                'transformative': 'M 32 45 Q 40 49 48 45'
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
                'serenity': '#10b981',
                'rebel': '#dc2626',
                'revolutionary': '#f97316',
                'defiant': '#b91c1c',
                'transformative': '#7c3aed'
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
        const avatarSvg = document.querySelector('.avatar-speaking');

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
            console.log('[Chat] ⚠️ Empty message, not sending');
            return;
        }

        console.log(`[Chat] 📤 Sending message: "${message.substring(0, 50)}..."`);

        // Add user message to chat immediately
        this.addChatMessage(message, true);
        chatInput.value = '';
        
        // Clear any pending transcript buffer
        this.finalTranscriptBuffer = '';

        // Show typing indicator
        const typingId = Date.now();
        this.addChatMessage('Roboto is thinking...', false, typingId);

        let retryCount = 0;
        const maxRetries = 3;

        while (retryCount < maxRetries) {
            try {
                console.log(`[Chat] 🔄 Attempt ${retryCount + 1}/${maxRetries}`);
                
                // Create abort controller for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000);

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache',
                    },
                    body: JSON.stringify({ 
                        message,
                        timestamp: Date.now(),
                        source: 'speech' // Indicate this came from speech
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
                    console.log(`[Chat] ✅ Response received: "${data.response.substring(0, 50)}..."`);
                    
                    // Add bot response to chat
                    this.addChatMessage(data.response, false);

                    // Speak the response if TTS is enabled
                    if (this.ttsEnabled) {
                        console.log('[Chat] 🔊 Starting TTS playback');
                        this.speakText(data.response);
                    }

                    // Update emotional status after each message
                    this.loadEmotionalStatus();
                    return; // Success, exit retry loop
                } else {
                    throw new Error(data.response || 'Invalid response from server');
                }

            } catch (error) {
                console.error(`[Chat] ❌ Attempt ${retryCount + 1} failed:`, error);
                retryCount++;

                if (retryCount >= maxRetries) {
                    // Remove typing indicator
                    this.removeChatMessage(typingId);

                    if (error.name === 'AbortError') {
                        console.error('[Chat] ⏱️ Request timeout after 30s');
                        this.addChatMessage('Request timed out. Please try again.', false);
                        this.showNotification('Request timed out', 'warning');
                    } else if (error.message.includes('HTTP 5')) {
                        console.error('[Chat] 🔥 Server error:', error.message);
                        this.addChatMessage('Server is experiencing issues. Please try again in a moment.', false);
                        this.showNotification('Server error - please try again', 'error');
                    } else {
                        console.error('[Chat] 📡 Connection error:', error.message);
                        this.addChatMessage('Connection problem. Please check your internet and try again.', false);
                        this.showNotification('Connection failed - please try again', 'error');
                    }
                } else {
                    // Wait before retry
                    const delay = 1000 * retryCount;
                    console.log(`[Chat] ⏳ Retrying in ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
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

        // Create elements using safe DOM methods
        const flexDiv = document.createElement('div');
        flexDiv.className = `d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = `message-content p-2 rounded ${isUser ? 'bg-primary text-white' : 'bg-secondary'}`;
        contentDiv.style.maxWidth = '80%';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = message; // Safe: textContent auto-escapes

        const timeSmall = document.createElement('small');
        timeSmall.className = 'message-time text-muted d-block mt-1';
        timeSmall.textContent = time; // Safe: textContent auto-escapes

        // Assemble the DOM structure
        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeSmall);
        flexDiv.appendChild(contentDiv);
        messageDiv.appendChild(flexDiv);

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    renderChatHistory() {
        const chatHistory = document.getElementById('chatHistory');

        if (this.chatHistory.length === 0) {
            this.renderEmptyChat();
            return;
        }

        chatHistory.innerHTML = '';

        this.chatHistory.forEach(entry => {
            const time = new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // User message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'chat-message mb-2 user-message';

            const userFlexDiv = document.createElement('div');
            userFlexDiv.className = 'd-flex justify-content-end';

            const userContentDiv = document.createElement('div');
            userContentDiv.className = 'message-content p-2 rounded bg-primary text-white';
            userContentDiv.style.maxWidth = '80%';

            const userTextDiv = document.createElement('div');
            userTextDiv.className = 'message-text';
            userTextDiv.textContent = entry.message;

            const userTimeSmall = document.createElement('small');
            userTimeSmall.className = 'message-time text-muted d-block mt-1';
            userTimeSmall.textContent = time;

            userContentDiv.appendChild(userTextDiv);
            userContentDiv.appendChild(userTimeSmall);
            userFlexDiv.appendChild(userContentDiv);
            userMessageDiv.appendChild(userFlexDiv);
            chatHistory.appendChild(userMessageDiv);

            // Bot response
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'chat-message mb-2 bot-message';

            const botFlexDiv = document.createElement('div');
            botFlexDiv.className = 'd-flex justify-content-start';

            const botContentDiv = document.createElement('div');
            botContentDiv.className = 'message-content p-2 rounded bg-secondary';
            botContentDiv.style.maxWidth = '80%';

            const botTextDiv = document.createElement('div');
            botTextDiv.className = 'message-text';
            botTextDiv.textContent = entry.response;

            const botTimeSmall = document.createElement('small');
            botTimeSmall.className = 'message-time text-muted d-block mt-1';
            botTimeSmall.textContent = time;

            botContentDiv.appendChild(botTextDiv);
            botContentDiv.appendChild(botTimeSmall);
            botFlexDiv.appendChild(botContentDiv);
            botMessageDiv.appendChild(botFlexDiv);
            chatHistory.appendChild(botMessageDiv);
        });

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


// Roboto Request System
class RobotoRequestSystem {
    constructor() {
        this.requestQueue = [];
        this.isProcessing = false;
        this.setupRobotoRequests();
    }

    setupRobotoRequests() {
        // Add Roboto request button if it doesn't exist
        if (!document.getElementById('robotoRequestBtn')) {
            const requestBtn = document.createElement('button');
            requestBtn.id = 'robotoRequestBtn';
            requestBtn.className = 'btn btn-outline-primary me-2';
            requestBtn.innerHTML = '<i class="bi bi-robot"></i> Roboto Request';
            requestBtn.onclick = () => this.showRequestMenu();

            const sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                sendBtn.parentNode.insertBefore(requestBtn, sendBtn);
            }
        }
    }

    showRequestMenu() {
        const requests = [
            { id: 'memory_analysis', name: '🧠 Memory Analysis', description: 'Analyze conversation patterns, memories, and insights' },
            { id: 'self_improvement', name: '📈 Self Improvement', description: 'Trigger A/B testing and learning optimization' },
            { id: 'quantum_computation', name: '🌌 Quantum Computing', description: 'Execute quantum algorithms and computations' },
            { id: 'voice_optimization', name: '🎤 Voice Optimization', description: 'Optimize voice recognition for Roberto' },
            { id: 'autonomous_task', name: '🎯 Autonomous Task', description: 'Execute complex autonomous planning tasks' },
            { id: 'cultural_query', name: '🌞 Cultural Wisdom', description: 'Access Aztec wisdom and Nahuatl language' },
            { id: 'real_time_data', name: '📡 Real-Time Data', description: 'Get current time, system, and contextual data' },
            { id: 'system_status', name: '🔧 System Status', description: 'Comprehensive system health check' }
        ];

        let menuHTML = '<div class="roboto-request-menu"><h5>🚀 Roboto SAI Request Menu</h5><p class="text-muted small mb-3">Advanced capabilities at your command</p>';

        requests.forEach(request => {
            menuHTML += `
                <div class="request-option p-2 border rounded mb-2" onclick="robotoRequestSystem.executeRequest('${request.id}')" style="cursor: pointer; transition: background 0.2s;">
                    <strong>${request.name}</strong>
                    <small class="text-muted d-block">${request.description}</small>
                </div>
            `;
        });

        menuHTML += `
            <div class="mt-3 pt-3 border-top">
                <small class="text-muted">🤖 Roboto SAI v3.0 - Super Advanced Intelligence</small><br>
                <small class="text-muted">Created by Roberto Villarreal Martinez</small>
            </div>
        </div>`;

        // Add CSS for better styling
        const style = `
            <style>
            .roboto-request-menu {
                max-width: 400px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .request-option:hover {
                background-color: #f8f9fa !important;
                border-color: #007bff !important;
            }
            </style>
        `;

        // Show menu in a modal or overlay
        this.displayRequestMenu(style + menuHTML);
    }

    async executeRequest(requestType) {
        this.closeRequestMenu();

        let requestData = {
            type: requestType,
            timestamp: new Date().toISOString(),
            context: {
                user_agent: navigator.userAgent,
                timestamp: Date.now(),
                page_url: window.location.href
            }
        };

        // Add specific data based on request type
        switch(requestType) {
            case 'memory_analysis':
                requestData.content = 'Analyze my conversation patterns, memories, and provide comprehensive insights';
                break;
            case 'self_improvement':
                requestData.content = 'Initiate self-improvement cycle with A/B testing and optimization';
                break;
            case 'quantum_computation':
                requestData.content = 'Execute quantum search algorithm and provide quantum status';
                break;
            case 'voice_optimization':
                requestData.content = 'Optimize voice recognition for Roberto Villarreal Martinez speech patterns';
                break;
            case 'autonomous_task':
                const taskContent = prompt('Enter autonomous task description:');
                requestData.content = taskContent || 'Analyze current system capabilities and suggest improvements';
                break;
            case 'cultural_query':
                const culturalQuery = prompt('Enter cultural or Nahuatl query:');
                requestData.content = culturalQuery || 'Share Aztec wisdom and cultural insights';
                break;
            case 'real_time_data':
                requestData.content = 'Provide comprehensive real-time data and contextual insights';
                break;
            case 'system_status':
                requestData.content = 'Provide comprehensive system status report for all SAI components';
                break;
        }

        // Show processing indicator
        this.showProcessingIndicator(requestType);

        this.addRequestToQueue(requestData);
    }

    showProcessingIndicator(requestType) {
        const chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;

        const processingDiv = document.createElement('div');
        processingDiv.className = 'message bot-message mb-3 processing-request';
        processingDiv.innerHTML = `
            <div class="message-content">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Processing...</span>
                    </div>
                    <span>🤖 Processing ${requestType.replace('_', ' ')} request...</span>
                </div>
                <small class="text-muted d-block mt-1">Advanced SAI systems activated</small>
            </div>
        `;

        chatContainer.appendChild(processingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    addRequestToQueue(requestData) {
        this.requestQueue.push(requestData);
        if (!this.isProcessing) {
            this.processRequestQueue();
        }
    }

    async processRequestQueue() {
        if (this.requestQueue.length === 0) {
            this.isProcessing = false;
            return;
        }

        this.isProcessing = true;
        const request = this.requestQueue.shift();

        try {
            const response = await fetch('/api/roboto-request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            const result = await response.json();

            // Remove processing indicator
            const processingElement = document.querySelector('.processing-request');
            if (processingElement) {
                processingElement.remove();
            }

            this.displayRequestResult(result, request.type);

        } catch (error) {
            console.error('Request failed:', error);

            // Remove processing indicator
            const processingElement = document.querySelector('.processing-request');
            if (processingElement) {
                processingElement.remove();
            }

            this.displayRequestError(error, request.type);
        }

        // Process next request
        setTimeout(() => this.processRequestQueue(), 1000);
    }

    displayRequestResult(result, requestType) {
        const chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;

        const resultDiv = document.createElement('div');
        resultDiv.className = 'message bot-message mb-3';

        let content = `<h6>🚀 ${this.escapeHtml(requestType.replace('_', ' ')).toUpperCase()} Result</h6>`;

        if (result.success) {
            content += `<div class="alert alert-success mb-3">✅ Request completed successfully</div>`;

            // Main response
            if (result.response) {
                content += `<div class="mb-3"><strong>Response:</strong><br>${this.escapeHtml(result.response)}</div>`;
            }

            // Specific content based on request type
            switch(requestType) {
                case 'memory_analysis':
                    if (result.memory_count) {
                        content += `<p><strong>🧠 Memories Found:</strong> ${this.escapeHtml(String(result.memory_count))}</p>`;
                    }
                    if (result.memories && result.memories.length > 0) {
                        content += '<strong>Recent Relevant Memories:</strong><ul>';
                        result.memories.slice(0, 3).forEach(memory => {
                            content += `<li>${this.escapeHtml(memory.user_input || memory.content)}</li>`;
                        });
                        content += '</ul>';
                    }
                    break;

                case 'self_improvement':
                    if (result.experiment_id) {
                        content += `<p><strong>📈 Experiment ID:</strong> ${this.escapeHtml(String(result.experiment_id))}</p>`;
                    }
                    if (result.deployment_status) {
                        content += `<p><strong>🚀 Deployment:</strong> ${result.deployment_status.deployed ? 'Success' : 'Pending'}</p>`;
                    }
                    break;

                case 'quantum_computation':
                    if (result.algorithm) {
                        content += `<p><strong>🌌 Algorithm:</strong> ${this.escapeHtml(String(result.algorithm))}</p>`;
                    }
                    if (result.quantum_status) {
                        content += `<p><strong>⚛️ Quantum Status:</strong> ${this.escapeHtml(String(result.quantum_status.quantum_entanglement?.status || 'Active'))}</p>`;
                    }
                    break;

                case 'voice_optimization':
                    if (result.insights) {
                        content += `<p><strong>🎤 Voice Insights:</strong> ${this.escapeHtml(String(result.insights))}</p>`;
                    }
                    break;

                case 'autonomous_task':
                    if (result.task_id) {
                        content += `<p><strong>🎯 Task ID:</strong> ${this.escapeHtml(String(result.task_id))}</p>`;
                    }
                    if (result.status) {
                        content += `<p><strong>Status:</strong> ${this.escapeHtml(String(result.status))}</p>`;
                    }
                    break;

                case 'cultural_query':
                    if (result.cultural_response) {
                        content += `<p><strong>🌞 Cultural Wisdom:</strong> ${this.escapeHtml(String(result.cultural_response))}</p>`;
                    }
                    break;

                case 'real_time_data':
                    if (result.summary) {
                        content += `<p><strong>📡 Real-Time Summary:</strong> ${this.escapeHtml(String(result.summary))}</p>`;
                    }
                    if (result.data_sources) {
                        const escapedSources = result.data_sources.map(s => this.escapeHtml(String(s))).join(', ');
                        content += `<p><strong>Data Sources:</strong> ${escapedSources}</p>`;
                    }
                    break;
            }

            // General insights and recommendations
            if (result.insights && requestType !== 'voice_optimization') {
                content += `<p><strong>💡 Insights:</strong> ${this.escapeHtml(String(result.insights))}</p>`;
            }
            if (result.recommendations) {
                content += `<p><strong>📋 Recommendations:</strong> ${this.escapeHtml(String(result.recommendations))}</p>`;
            }
            if (result.message && !result.response) {
                content += `<p><strong>Message:</strong> ${this.escapeHtml(String(result.message))}</p>`;
            }

            // Enhancement indicators
            if (result.enhancements_applied) {
                const escapedEnhancements = result.enhancements_applied.map(e => this.escapeHtml(String(e))).join(', ');
                content += `<small class="text-muted">🔧 Enhancements: ${escapedEnhancements}</small><br>`;
            }

        } else {
            content += `<div class="alert alert-danger">❌ Error: ${this.escapeHtml(String(result.error || 'Request failed'))}</div>`;
        }

        resultDiv.innerHTML = `
            <div class="message-content">
                ${content}
                <small class="text-muted d-block mt-2">${new Date().toLocaleTimeString()}</small>
            </div>
        `;

        chatContainer.appendChild(resultDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    displayRequestError(error, requestType) {
        const chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message mb-3';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const heading = document.createElement('h6');
        heading.textContent = `🚀 ${requestType.replace('_', ' ').toUpperCase()} Error`;

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        alertDiv.textContent = `❌ Request failed: ${error.message || 'An unknown error occurred'}`;

        const timestamp = document.createElement('small');
        timestamp.className = 'text-muted d-block mt-2';
        timestamp.textContent = new Date().toLocaleTimeString();

        messageContent.appendChild(heading);
        messageContent.appendChild(alertDiv);
        messageContent.appendChild(timestamp);
        errorDiv.appendChild(messageContent);

        chatContainer.appendChild(errorDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Placeholder for displaying menu
    displayRequestMenu(menuHTML) {
        // This should ideally open a modal or an overlay
        // For now, we'll log it to the console or append it to a specific element
        console.log('Displaying request menu:', menuHTML);

        const modalContent = document.createElement('div');
        modalContent.id = 'robotoRequestModal';
        modalContent.className = 'modal fade';
        modalContent.setAttribute('tabindex', '-1');
        modalContent.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${menuHTML}
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modalContent);

        const modal = new bootstrap.Modal(modalContent);
        modal.show();

        modalContent.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modalContent);
        });
    }

    // Placeholder for closing menu
    closeRequestMenu() {
        const modalElement = document.getElementById('robotoRequestModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize Roboto Request System when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.robotoRequestSystem = new RobotoRequestSystem();
});


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
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                }
                
                this.showNotification('Data exported successfully!', 'success');
            } else {
                this.showNotification('Export failed: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Failed to export data', 'error');
        }
    }

    async showGitHubProjectStatus() {
        try {
            const response = await fetch('/api/github-project-status');
            const data = await response.json();

            if (data.success) {
                const analyticsDisplay = document.getElementById('analyticsDisplay');

                let html = '<div class="github-project-status">';
                html += '<h6 class="text-info mb-3"><i class="fab fa-github me-2"></i>GitHub Project Status</h6>';

                // Project summary
                html += `<div class="mb-3">
                    <div class="card bg-dark border-secondary">
                        <div class="card-body p-3">
                            <h6 class="card-title text-success">Project Board</h6>
                            <p class="card-text small">${data.summary.replace(/\n/g, '<br>')}</p>
                            <a href="${data.project_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                <i class="fab fa-github me-1"></i>View on GitHub
                            </a>
                        </div>
                    </div>
                </div>`;

                // Sync button
                html += `<div class="mb-3">
                    <button class="btn btn-success me-2" onclick="app.syncGitHubTasks()">
                        <i class="fas fa-sync me-1"></i>Sync Tasks
                    </button>
                    <button class="btn btn-primary" onclick="app.createGitHubCard()">
                        <i class="fas fa-plus me-1"></i>Create Card
                    </button>
                </div>`;

                html += '</div>';
                analyticsDisplay.innerHTML = html;

                this.showNotification('GitHub project status loaded!', 'success');
            } else {
                this.showNotification('GitHub integration requires setup', 'warning');
            }
        } catch (error) {
            console.error('Error loading GitHub project status:', error);
            this.showNotification('Error loading GitHub project', 'error');
        }
    }

    async syncGitHubTasks() {
        try {
            const response = await fetch('/api/github-sync-tasks', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.showNotification(`Synced ${data.synced_tasks} tasks from GitHub!`, 'success');
                // Refresh chat history to see the sync
                this.loadChatHistory();
            } else {
                this.showNotification(data.error || 'Sync failed', 'error');
            }
        } catch (error) {
            console.error('Error syncing GitHub tasks:', error);
            this.showNotification('Sync failed', 'error');
        }
    }

    async createGitHubCard() {
        const note = prompt('Enter card content:');
        if (!note) return;

        const column = prompt('Enter column name (To Do, In Progress, Done):', 'To Do');
        if (!column) return;

        try {
            const response = await fetch('/api/github-create-card', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ note, column })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Card created on GitHub!', 'success');
                this.showGitHubProjectStatus(); // Refresh display
            } else {
                this.showNotification(data.error || 'Failed to create card', 'error');
            }
        } catch (error) {
            console.error('Error creating GitHub card:', error);
            this.showNotification('Failed to create card', 'error');
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

            // Enhanced settings for stable continuous listening
            this.speechRecognition.continuous = true;
            this.speechRecognition.interimResults = true;
            this.speechRecognition.lang = 'en-US';
            this.speechRecognition.maxAlternatives = 1;

            // Speech timeout tracking
            this.speechTimeout = null;
            this.finalTranscriptBuffer = '';

            this.speechRecognition.onstart = () => {
                this.isListeningActive = true;
                this.updateListeningIndicator(true);
                console.log('[Speech] ✅ Recognition started successfully');
                
                // Reset network retry counter on successful connection
                if (this.networkRetryCount > 0) {
                    console.log(`[Speech] 🔄 Network reconnected after ${this.networkRetryCount} retries`);
                    this.networkRetryCount = 0;
                }
                
                // Update voice system status - operational
                this.updateVoiceSystemStatus('operational', 'connected');
            };

            this.speechRecognition.onresult = (event) => {
                const chatInput = document.getElementById('chatInput');
                if (!chatInput) {
                    console.error('[Speech] ❌ Chat input element not found');
                    return;
                }

                let finalTranscript = '';
                let interimTranscript = '';

                // Process all results
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    const confidence = event.results[i][0].confidence;
                    
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                        console.log(`[Speech] ✅ Final transcript: "${transcript}" (confidence: ${confidence.toFixed(2)})`);
                    } else {
                        interimTranscript += transcript;
                        console.log(`[Speech] 📝 Interim transcript: "${transcript}"`);
                    }
                }

                // Handle final transcript with debouncing
                if (finalTranscript.trim()) {
                    this.finalTranscriptBuffer += finalTranscript;
                    
                    // Clear existing timeout
                    if (this.speechTimeout) {
                        clearTimeout(this.speechTimeout);
                    }
                    
                    // Wait for pause before processing
                    this.speechTimeout = setTimeout(() => {
                        if (this.finalTranscriptBuffer.trim()) {
                            const completeText = this.finalTranscriptBuffer.trim();
                            chatInput.value = completeText;
                            this.finalTranscriptBuffer = '';
                            console.log(`[Speech] 📤 Complete message ready: "${completeText}"`);
                            
                            // Auto-send after complete thought
                            const confidence = event.results[event.results.length - 1][0].confidence;
                            if (confidence > 0.7) {
                                setTimeout(() => {
                                    this.sendMessage();
                                    chatInput.value = ''; // Clear after sending
                                }, 800);
                            }
                        }
                    }, 1500); // 1.5 second pause detection
                }

                // Show interim results as visual feedback only
                if (interimTranscript && !finalTranscript) {
                    const displayText = this.finalTranscriptBuffer + interimTranscript;
                    chatInput.value = displayText;
                    chatInput.style.borderColor = '#28a745';
                    chatInput.style.boxShadow = '0 0 5px rgba(40, 167, 69, 0.5)';
                } else if (finalTranscript) {
                    chatInput.style.borderColor = '';
                    chatInput.style.boxShadow = '';
                }
            };

            this.speechRecognition.onerror = (event) => {
                const timestamp = new Date().toISOString();
                console.error(`[Speech] ❌ Error at ${timestamp}:`, event.error);
                
                const chatInput = document.getElementById('chatInput');
                
                // Comprehensive error handling with logging
                switch(event.error) {
                    case 'no-speech':
                        console.log('[Speech] ⏸️ No speech detected - will auto-restart');
                        // Don't show notification for no-speech, it's normal
                        if (this.continuousListening && !this.isSpeaking) {
                            setTimeout(() => this.resumeContinuousListening(), 1000);
                        }
                        break;
                        
                    case 'aborted':
                        console.log('[Speech] 🛑 Recognition aborted (normal during restart)');
                        this.isListeningActive = false;
                        if (this.continuousListening) {
                            setTimeout(() => this.resumeContinuousListening(), 500);
                        }
                        break;
                        
                    case 'audio-capture':
                        console.error('[Speech] 🎤 Microphone capture failed - check device availability');
                        this.isListeningActive = false;
                        this.showNotification('Microphone unavailable. Check if another app is using it.', 'error');
                        break;
                        
                    case 'not-allowed':
                        console.error('[Speech] 🚫 Microphone permission denied by user');
                        this.isListeningActive = false;
                        this.continuousListening = false;
                        this.updateMuteButton();
                        this.showNotification('Microphone permission required. Please allow access.', 'error');
                        break;
                        
                    case 'network':
                        console.error('[Speech] 📡 Network error - speech service unavailable');
                        this.isListeningActive = false;
                        
                        // 3. Exponential backoff retry logic
                        if (this.networkRetryCount < this.maxNetworkRetries) {
                            this.networkRetryCount++;
                            const retryDelay = Math.min(3000 * Math.pow(2, this.networkRetryCount - 1), 30000); // Max 30s
                            
                            // 4. Clearer user notifications with retry info
                            const retrySeconds = Math.ceil(retryDelay / 1000);
                            this.showNotification(
                                `📡 Network issue. Retrying in ${retrySeconds}s... (${this.networkRetryCount}/${this.maxNetworkRetries})`,
                                'warning'
                            );
                            
                            console.log(`[Speech] 🔄 Network retry ${this.networkRetryCount}/${this.maxNetworkRetries} in ${retrySeconds}s`);
                            
                            // Update voice system status - retrying
                            this.updateVoiceSystemStatus('retrying', `reconnecting (${this.networkRetryCount}/${this.maxNetworkRetries})`);
                            
                            if (this.continuousListening) {
                                setTimeout(() => {
                                    console.log('[Speech] 📡 Attempting network reconnect...');
                                    this.resumeContinuousListening();
                                }, retryDelay);
                            }
                        } else {
                            // Max retries reached
                            this.networkRetryCount = 0;
                            this.showNotification(
                                '❌ Speech service unavailable. Please check your internet connection.',
                                'error'
                            );
                            console.error('[Speech] ❌ Max network retries reached. Giving up.');
                            
                            // Update voice system status - disconnected
                            this.updateVoiceSystemStatus('error', 'disconnected');
                        }
                        break;
                        
                    case 'service-not-allowed':
                        console.error('[Speech] 🔒 Speech service blocked - check browser settings');
                        this.isListeningActive = false;
                        this.showNotification('Speech recognition blocked. Check browser settings.', 'error');
                        break;
                        
                    default:
                        console.error(`[Speech] ⚠️ Unexpected error: ${event.error}`);
                        this.showNotification(`Speech error: ${event.error}`, 'warning');
                        if (this.continuousListening) {
                            setTimeout(() => this.resumeContinuousListening(), 2000);
                        }
                }
            };

            this.speechRecognition.onend = () => {
                console.log('[Speech] 🔄 Recognition ended - checking restart conditions');
                this.handleSpeechEnd();
            };
        } else {
            console.error('[Speech] ❌ Speech recognition not supported in this browser');
            this.showNotification('Speech recognition not supported in this browser', 'error');
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
        if (!this.speechRecognition || this.continuousListening) return;

        this.continuousListening = true;
        this.isListeningActive = true;
        this.pendingTranscript = ''; // Track partial transcript

        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.classList.add('listening');
            const icon = voiceBtn.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-microphone';
            }
        }

        try {
            this.speechRecognition.start();
            console.log('Continuous listening started');
        } catch (e) {
            console.error('Failed to start listening:', e);
            this.isListeningActive = false;
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
        
        console.log('[Speech] 🔄 handleSpeechEnd called', {
            isMuted: this.isMuted,
            continuousListening: this.continuousListening,
            isSpeaking: this.isSpeaking
        });

        // Smart restart logic - only if conditions are right
        if (!this.isMuted && this.continuousListening && !this.isSpeaking) {
            console.log('[Speech] ♻️ Scheduling restart in 300ms');
            setTimeout(() => {
                if (!this.isMuted && !this.isListeningActive) {
                    console.log('[Speech] 🔄 Restarting recognition');
                    this.startContinuousListening();
                }
            }, 300);
        } else {
            console.log('[Speech] ⏸️ Not restarting:', {
                reason: this.isMuted ? 'muted' : !this.continuousListening ? 'not continuous' : 'speaking'
            });
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

    updateVoiceSystemStatus(status, networkStatus = null) {
        const indicatorEl = document.getElementById('voiceSystemIndicator');
        const statusEl = document.getElementById('voiceSystemStatus');
        const networkEl = document.getElementById('networkStatus');
        
        if (!indicatorEl || !statusEl) return;
        
        // Update main status
        switch(status) {
            case 'operational':
                indicatorEl.style.color = '#28a745'; // Green
                statusEl.textContent = 'Operational';
                statusEl.className = 'text-success';
                break;
            case 'retrying':
                indicatorEl.style.color = '#ffc107'; // Yellow
                statusEl.textContent = 'Retrying...';
                statusEl.className = 'text-warning';
                break;
            case 'error':
                indicatorEl.style.color = '#dc3545'; // Red
                statusEl.textContent = 'Error';
                statusEl.className = 'text-danger';
                break;
            case 'idle':
                indicatorEl.style.color = '#6c757d'; // Gray
                statusEl.textContent = 'Idle';
                statusEl.className = 'text-muted';
                break;
        }
        
        // Update network status if provided
        if (networkEl && networkStatus) {
            networkEl.textContent = networkStatus;
            
            if (networkStatus.includes('reconnecting')) {
                networkEl.className = 'text-warning';
            } else if (networkStatus === 'disconnected') {
                networkEl.className = 'text-danger';
            } else {
                networkEl.className = 'text-success';
            }
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




    async processSpeechToSpeech(audioBlob) {
        try {
            this.showNotification('Processing speech...', 'info');

            const formData = new FormData();
            formData.append('audio', audioBlob, 'audio.webm');

            const response = await fetch('/speech_to_speech', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Display transcript and response
                this.addChatMessage(data.transcript, true);
                this.addChatMessage(data.response, false);

                // Play audio response
                if (data.audio) {
                    const audioData = `data:audio/mp3;base64,${data.audio}`;
                    const audio = new Audio(audioData);
                    audio.play().catch(e => console.error('Audio playback error:', e));
                }

                this.showNotification('Speech-to-speech completed!', 'success');
            } else {
                this.showNotification(data.message || 'Speech processing failed', 'error');
            }
        } catch (error) {
            console.error('Speech-to-speech error:', error);
            this.showNotification('Speech processing failed', 'error');
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

    // Advanced Voice Recognition System
    initializeAdvancedVoice() {
        this.advancedVoiceActive = false;
        this.noiseThreshold = 0.8;
        this.minPhraseLength = 3;
        this.silenceTimeout = 1500;
        this.voiceBuffer = [];
        this.lastSpeechTime = 0;
        this.isProcessingVoice = false;

        const voiceActivateBtn = document.getElementById('voiceActivateBtn');
        const voiceMuteBtn = document.getElementById('voiceMuteBtn');

        if (voiceActivateBtn && !voiceActivateBtn.hasAttribute('data-listener')) {
            voiceActivateBtn.setAttribute('data-listener', 'true');
            voiceActivateBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.activateAdvancedVoice();
            });
        }

        if (voiceMuteBtn && !voiceMuteBtn.hasAttribute('data-listener')) {
            voiceMuteBtn.setAttribute('data-listener', 'true');
            voiceMuteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.muteAdvancedVoice();
            });
        }
    }

    async activateAdvancedVoice() {
        if (!this.speechRecognition) {
            this.initializeSpeechRecognition();
        }

        if (!this.speechRecognition) {
            this.showNotification('Speech recognition not supported', 'error');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());

            this.advancedVoiceActive = true;
            this.updateAdvancedVoiceUI(true);
            this.startAdvancedListening();
            this.showNotification('Advanced voice recognition activated', 'success');

        } catch (error) {
            this.showNotification('Microphone access required', 'error');
        }
    }

    muteAdvancedVoice() {
        this.advancedVoiceActive = false;
        this.stopAdvancedListening();
        this.updateAdvancedVoiceUI(false);
        this.showNotification('Voice recognition muted', 'info');
    }

    startAdvancedListening() {
        if (!this.speechRecognition || !this.advancedVoiceActive) return;

        this.speechRecognition.continuous = true;
        this.speechRecognition.interimResults = true;
        this.speechRecognition.lang = 'en-US';
        this.speechRecognition.maxAlternatives = 3;

        this.speechRecognition.onresult = (event) => {
            this.handleAdvancedSpeechResults(event);
        };

        this.speechRecognition.onerror = (event) => {
            if (event.error !== 'no-speech') {
                console.error('Speech error:', event.error);
            }
        };

        this.speechRecognition.onend = () => {
            if (this.advancedVoiceActive) {
                setTimeout(() => {
                    if (this.advancedVoiceActive) {
                        this.speechRecognition.start();
                    }
                }, 100);
            }
        };

        this.speechRecognition.start();
        this.updateVoiceStatus('Listening...', true);
    }

    stopAdvancedListening() {
        if (this.speechRecognition) {
            this.speechRecognition.stop();
        }
        this.updateVoiceStatus('Ready', false);
    }

    handleAdvancedSpeechResults(event) {
        let finalTranscript = '';
        let interimTranscript = '';
        let maxConfidence = 0;

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            const transcript = result[0].transcript;
            const confidence = result[0].confidence || 0.9;

            if (result.isFinal) {
                if (confidence >= this.noiseThreshold) {
                    finalTranscript += transcript;
                    maxConfidence = Math.max(maxConfidence, confidence);
                }
            } else {
                interimTranscript += transcript;
            }
        }

        if (interimTranscript.trim()) {
            this.updateVoiceStatus(`"${interimTranscript.trim()}"`, true);
        }

        if (finalTranscript.trim()) {
            this.processAdvancedTranscript(finalTranscript.trim(), maxConfidence);
        }
    }

    processAdvancedTranscript(transcript, confidence) {
        if (transcript.length < this.minPhraseLength || confidence < this.noiseThreshold) {
            return;
        }

        const now = Date.now();
        this.voiceBuffer.push({
            text: transcript,
            confidence: confidence,
            timestamp: now
        });

        this.voiceBuffer = this.voiceBuffer.filter(item => 
            now - item.timestamp < this.silenceTimeout
        );

        clearTimeout(this.voiceProcessTimeout);
        this.voiceProcessTimeout = setTimeout(() => {
            this.processVoiceBuffer();
        }, this.silenceTimeout);
    }

    processVoiceBuffer() {
        if (this.voiceBuffer.length === 0 || this.isProcessingVoice) return;

        const combinedText = this.voiceBuffer.map(item => item.text).join(' ').trim();
        const avgConfidence = this.voiceBuffer.reduce((sum, item) => sum + item.confidence, 0) / this.voiceBuffer.length;

        this.voiceBuffer = [];

        if (combinedText.length >= this.minPhraseLength && avgConfidence >= this.noiseThreshold) {
            this.sendAdvancedVoiceMessage(combinedText);
        }

        this.updateVoiceStatus('Listening...', true);
    }

    async sendAdvancedVoiceMessage(transcript) {
        if (this.isProcessingVoice) return;

        this.isProcessingVoice = true;
        this.updateVoiceStatus('Processing...', true);

        try {
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.value = transcript;
                await this.sendMessage();
                chatInput.value = '';
            }

        } catch (error) {
            this.showNotification('Failed to send voice message', 'error');
        } finally {
            this.isProcessingVoice = false;
            setTimeout(() => {
                this.updateVoiceStatus('Listening...', true);
            }, 1000);
        }
    }

    updateAdvancedVoiceUI(active) {
        const voiceActivateBtn = document.getElementById('voiceActivateBtn');
        const voiceMuteBtn = document.getElementById('voiceMuteBtn');
        const voiceWaveAnimation = document.getElementById('voiceWaveAnimation');

        if (voiceActivateBtn) {
            if (active) {
                voiceActivateBtn.classList.remove('btn-success');
                voiceActivateBtn.classList.add('btn-warning');
                voiceActivateBtn.innerHTML = '<i class="fas fa-microphone"></i> Active';
            } else {
                voiceActivateBtn.classList.remove('btn-warning');
                voiceActivateBtn.classList.add('btn-success');
                voiceActivateBtn.innerHTML = '<i class="fas fa-microphone"></i> Activate';
            }
        }

        if (voiceMuteBtn) {
            voiceMuteBtn.classList.toggle('btn-danger', active);
            voiceMuteBtn.classList.toggle('btn-outline-light', !active);
        }

        if (voiceWaveAnimation) {
            voiceWaveAnimation.style.display = active ? 'flex' : 'none';
        }
    }

    updateVoiceStatus(message, active) {
        const voiceStatus = document.getElementById('voiceStatus');
        if (voiceStatus) {
            voiceStatus.textContent = message;
            voiceStatus.style.color = active ? '#28a745' : '#6c757d';
        }
    }
}