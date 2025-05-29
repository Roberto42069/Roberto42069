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
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        
        // Initialize analytics display
        this.initializeAnalytics();
    }

    bindEvents() {
        // Task form submission
        document.getElementById('addTaskForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTask();
        });

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

        // Toggle notifications button
        document.getElementById('toggleNotificationsBtn').addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleNotifications();
        });

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
        const categoryBadge = task.category ? `<span class="badge bg-dark me-1">${task.category}</span>` : '';
        
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

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) {
            return;
        }

        // Add user message to chat immediately
        this.addChatMessage(message, true);
        chatInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            if (data.success) {
                // Add bot response to chat
                this.addChatMessage(data.response, false);
            } else {
                this.addChatMessage(data.response || 'Sorry, I encountered an error.', false);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addChatMessage('Sorry, I\'m having trouble connecting right now.', false);
        }
    }

    addChatMessage(message, isUser) {
        const chatHistory = document.getElementById('chatHistory');
        const messageDiv = document.createElement('div');
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
            const response = await fetch('/api/export');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = response.headers.get('Content-Disposition').split('filename=')[1];
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showNotification('Data exported successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.message || 'Export failed', 'error');
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
            const response = await fetch('/api/learning/insights');
            const data = await response.json();
            
            if (data.success) {
                const insights = data.insights;
                let message = `🧠 Roboto's Learning Progress\n\n`;
                message += `Conversations: ${insights.conversation_count}\n\n`;
                
                if (insights.insights.length > 0) {
                    message += "What I've learned about you:\n";
                    insights.insights.forEach(insight => {
                        message += `• ${insight}\n`;
                    });
                } else {
                    message += "Keep chatting with me to help me learn your preferences!";
                }
                
                if (insights.learned_patterns && Object.keys(insights.learned_patterns).length > 0) {
                    message += "\nDetailed patterns:\n";
                    if (insights.learned_patterns.favorite_topics) {
                        const topics = Object.entries(insights.learned_patterns.favorite_topics)
                            .sort(([,a], [,b]) => b - a)
                            .slice(0, 3);
                        if (topics.length > 0) {
                            message += `Most discussed topics: ${topics.map(([topic, count]) => 
                                `${topic.replace('_', ' ')} (${count})`).join(', ')}\n`;
                        }
                    }
                }
                
                alert(message);
            } else {
                this.showNotification('Could not load learning insights', 'error');
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
            const response = await fetch('/api/predictive_insights');
            const data = await response.json();
            
            if (data.success) {
                let message = "🔮 Predictive Insights:\n\n";
                data.insights.forEach(insight => {
                    message += `✨ ${insight}\n`;
                });
                
                alert(message);
            } else {
                this.showNotification('Could not load predictive insights', 'error');
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
