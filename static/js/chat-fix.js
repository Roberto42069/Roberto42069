// Simple chat functionality to fix the loading issue
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatHistory = document.getElementById('chatHistory');
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceActivateBtn = document.getElementById('voiceActivateBtn');

    // Initialize chat
    loadChatHistory();
    loadEmotionalStatus();
    loadPersonalProfile();
    loadVoiceInsights();
    loadMemoryInsights();

    // Enhanced cross-browser text-to-speech functionality
    let ttsEnabled = localStorage.getItem('ttsEnabled') !== 'false';
    let speechSynthesis = window.speechSynthesis;
    let availableVoices = [];
    const ttsBtn = document.getElementById('ttsBtn');

    // Initialize speech synthesis for cross-browser compatibility
    function initializeTTS() {
        if ('speechSynthesis' in window) {
            // Load available voices
            function loadVoices() {
                availableVoices = speechSynthesis.getVoices();
                console.log('Available TTS voices:', availableVoices.length);
            }

            // Load voices immediately and on voiceschanged event
            loadVoices();
            speechSynthesis.onvoiceschanged = loadVoices;

            // Test TTS capability
            if (availableVoices.length === 0) {
                setTimeout(loadVoices, 100);
            }
        } else {
            console.warn('Text-to-speech not supported in this browser');
        }
    }

    // Enhanced speak function with cross-browser support
    function speakText(text) {
        if (!ttsEnabled || !text || !('speechSynthesis' in window)) {
            return;
        }

        try {
            // Cancel any ongoing speech
            speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);

            // Configure voice settings for better compatibility
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;

            // Select best available voice
            if (availableVoices.length > 0) {
                // Prefer English voices
                const englishVoice = availableVoices.find(voice => 
                    voice.lang.startsWith('en') && voice.localService
                ) || availableVoices.find(voice => 
                    voice.lang.startsWith('en')
                ) || availableVoices[0];

                if (englishVoice) {
                    utterance.voice = englishVoice;
                }
            }

            utterance.onstart = function() {
                console.log('TTS started');
            };

            utterance.onend = function() {
                console.log('TTS completed');
            };

            utterance.onerror = function(event) {
                console.error('TTS error:', event.error);
                // Retry with default settings if error occurs
                if (event.error === 'voice-unavailable') {
                    const simpleUtterance = new SpeechSynthesisUtterance(text);
                    speechSynthesis.speak(simpleUtterance);
                }
            };

            speechSynthesis.speak(utterance);
        } catch (error) {
            console.error('TTS error:', error);
        }
    }

    // Initialize TTS on page load
    initializeTTS();

    if (ttsBtn) {
        updateTTSButton();
        ttsBtn.addEventListener('click', function() {
            ttsEnabled = !ttsEnabled;
            localStorage.setItem('ttsEnabled', ttsEnabled);
            updateTTSButton();

            // Test TTS when enabled
            if (ttsEnabled) {
                speakText('Text to speech enabled');
            }
        });
    }

    // Chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            // Add user message
            addChatMessage(message, true);
            chatInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();

                if (data.success && data.response) {
                    addChatMessage(data.response, false);

                    // Add text-to-speech functionality if enabled
                    if (ttsEnabled && window.speechSynthesis) {
                        // Stop any current speech
                        window.speechSynthesis.cancel();

                        // Create new utterance
                        const utterance = new SpeechSynthesisUtterance(data.response);
                        utterance.rate = 0.9;
                        utterance.pitch = 1.1;
                        utterance.volume = 0.9;
                        utterance.lang = 'en-US';

                        // Speak the message
                        window.speechSynthesis.speak(utterance);
                    }

                    // Update all insights after each interaction
                    setTimeout(() => {
                        loadPersonalProfile();
                        loadVoiceInsights();
                        loadMemoryInsights();
                        loadEmotionalStatus();
                    }, 1000);
                } else {
                    addChatMessage('Sorry, I had trouble processing that message.', false);
                }
            } catch (error) {
                console.error('Chat error:', error);
                addChatMessage('Connection error. Please try again.', false);
            }
        });
    }

    // Combined voice button functionality with security
    let isListening = false;
    let recognition = null;

    if (voiceBtn) {
        voiceBtn.addEventListener('click', function() {
            if (!isListening) {
                startSecureSpeechRecognition();
            } else {
                stopSpeechRecognition();
            }
        });
    }



    function addChatMessage(message, isUser) {
        const chatHistory = document.getElementById('chatHistory') || document.getElementById('chat-history');
        if (!chatHistory) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message mb-2 ${isUser ? 'user-message' : 'bot-message'}`;

        const time = new Date().toLocaleTimeString();
        const avatarHtml = !isUser ? '<img src="/static/roboto-avatar.jpeg" alt="Roboto" class="rounded-circle me-2" style="width: 32px; height: 32px; object-fit: cover; border: 2px solid #dc3545;">' : '';

        messageDiv.innerHTML = `
            <div class="d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'} align-items-start">
                ${!isUser ? avatarHtml : ''}
                <div class="message-content p-2 rounded ${isUser ? 'bg-primary text-white' : 'bg-secondary'}" style="max-width: 80%;">
                    <div class="message-text">${escapeHtml(message)}</div>
                    <small class="message-time text-muted d-block mt-1">${time}</small>
                </div>
            </div>
        `;

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function loadChatHistory() {
        try {
            const response = await fetch('/api/history');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.success && data.history && Array.isArray(data.history)) {
                const chatHistoryElement = document.getElementById('chatHistory') || document.getElementById('chat-history');
                if (chatHistoryElement) {
                    // Keep the creator introduction, only remove loading indicator
                    const loadingIndicator = chatHistoryElement.querySelector('#loading-indicator');
                    if (loadingIndicator) {
                        loadingIndicator.remove();
                    }

                    console.log(`Loading ${data.history.length} conversations`);
                    data.history.forEach(entry => {
                        if (entry.message) {
                            addChatMessage(entry.message, true);
                        }
                        if (entry.response) {
                            addChatMessage(entry.response, false);
                        }
                    });

                    // Scroll to bottom
                    setTimeout(() => {
                        chatHistoryElement.scrollTop = chatHistoryElement.scrollHeight;
                    }, 100);
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            // Hide loading indicator and show error message
            const chatHistoryElement = document.getElementById('chatHistory') || document.getElementById('chat-history');
            if (chatHistoryElement) {
                const loadingIndicator = chatHistoryElement.querySelector('#loading-indicator');
                if (loadingIndicator) {
                    loadingIndicator.innerHTML = '<div class="text-center text-muted p-3">Your conversations are saved but temporarily unavailable. Try refreshing the page.</div>';
                }
            }
        }
    }

    async function loadEmotionalStatus() {
        try {
            const response = await fetch('/api/emotional_status');
            const data = await response.json();

            if (data.success) {
                const emotionElement = document.getElementById('currentEmotion');
                const avatarElement = document.getElementById('avatarEmotion');

                if (emotionElement) {
                    emotionElement.textContent = data.emotion;
                }
                if (avatarElement) {
                    avatarElement.textContent = data.emotion;
                }
            }
        } catch (error) {
            console.error('Error loading emotional status:', error);
        }
    }

    async function startSecureSpeechRecognition() {
        // Check for speech recognition support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Speech recognition not supported in this browser');
            return;
        }

        try {
            // Request secure microphone access with explicit permissions
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                } 
            });

            // Verify the stream is active and secure
            if (!stream.active) {
                throw new Error('Microphone access denied');
            }

            // Stop the stream immediately after permission check
            stream.getTracks().forEach(track => track.stop());

            // Initialize speech recognition with security measures
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 1;

            // Secure event handlers
            recognition.onstart = function() {
                isListening = true;
                updateVoiceButtonState(true);
                console.log('Secure speech recognition started');
            };

            recognition.onend = function() {
                console.log('Speech recognition ended');
                // Restart automatically if still supposed to be listening
                if (isListening) {
                    setTimeout(() => {
                        if (isListening && recognition) {
                            try {
                                recognition.start();
                            } catch (error) {
                                console.error('Error restarting recognition:', error);
                            }
                        }
                    }, 100);
                } else {
                    updateVoiceButtonState(false);
                }
            };

            recognition.onresult = function(event) {
                let finalTranscript = '';
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }

                // Show interim results in input field
                chatInput.value = finalTranscript + interimTranscript;

                // Submit when final result is received and learn from voice input
                if (finalTranscript) {
                    // Track voice recognition confidence for learning
                    const confidence = event.results[event.results.length - 1][0].confidence || 0.5;
                    console.log(`Voice recognition confidence: ${confidence}`);

                    setTimeout(() => {
                        chatForm.dispatchEvent(new Event('submit'));
                        // After submission, update voice insights
                        setTimeout(updateVoiceInsights, 1000);
                    }, 500);
                }
            };

            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                isListening = false;
                updateVoiceButtonState(false);

                if (event.error === 'not-allowed') {
                    alert('Microphone access denied. Please allow microphone access and try again.');
                } else if (event.error === 'no-speech') {
                    alert('No speech detected. Please try again.');
                } else {
                    alert('Speech recognition error: ' + event.error);
                }
            };

            // Start recognition
            recognition.start();

        } catch (error) {
            console.error('Microphone access error:', error);
            alert('Unable to access microphone. Please check your browser settings and try again.');
        }
    }

    function stopSpeechRecognition() {
        if (recognition && isListening) {
            recognition.stop();
            isListening = false;
            updateVoiceButtonState(false);
        }
    }

    function updateVoiceButtonState(listening) {
        if (!voiceBtn) return;

        if (listening) {
            voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
            voiceBtn.classList.remove('btn-outline-secondary');
            voiceBtn.classList.add('btn-danger');
            voiceBtn.title = 'Stop continuous listening';
        } else {
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.classList.remove('btn-danger');
            voiceBtn.classList.add('btn-outline-secondary');
            voiceBtn.title = 'Start continuous listening';
        }
    }

    function updateTTSButton() {
        if (!ttsBtn) return;

        if (ttsEnabled) {
            ttsBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            ttsBtn.classList.remove('btn-outline-info');
            ttsBtn.classList.add('btn-info');
            ttsBtn.title = 'Text-to-Speech: ON';
        } else {
            ttsBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
            ttsBtn.classList.remove('btn-info');
            ttsBtn.classList.add('btn-outline-info');
            ttsBtn.title = 'Text-to-Speech: OFF';
        }
    }

    async function loadVoiceInsights() {
        try {
            const response = await fetch('/api/voice-insights');
            const data = await response.json();

            const voiceElement = document.getElementById('voiceInsights');
            if (voiceElement && data.success) {
                voiceElement.textContent = data.insights;
            }
        } catch (error) {
            console.log('Voice insights update in progress...');
        }
    }

    async function optimizeVoiceRecognition(recognizedText, confidence, actualText = null) {
        try {
            const response = await fetch('/api/voice-optimization', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recognized_text: recognizedText,
                    confidence: confidence,
                    actual_text: actualText
                })
            });

            const data = await response.json();

            if (data.success && data.suggestions) {
                // Show optimization suggestions if needed
                if (confidence < 0.8) {
                    showVoiceOptimizationTip(data.suggestions[0]);
                }
            }
        } catch (error) {
            console.log('Voice optimization analysis in progress...');
        }
    }

    function showVoiceConfidenceIndicator(confidence) {
        const indicator = document.createElement('div');
        indicator.className = 'voice-confidence-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 123, 255, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            transition: opacity 0.3s;
        `;
        indicator.textContent = `Voice confidence: ${Math.round(confidence * 100)}%`;

        document.body.appendChild(indicator);

        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }, 2000);
    }

    function showVoiceOptimizationTip(suggestion) {
        const tip = document.createElement('div');
        tip.className = 'voice-optimization-tip';
        tip.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: rgba(40, 167, 69, 0.9);
            color: white;
            padding: 12px;
            border-radius: 6px;
            font-size: 14px;
            z-index: 1000;
            max-width: 400px;
            margin: 0 auto;
            text-align: center;
        `;
        tip.innerHTML = `
            <strong>Voice Tip:</strong> ${escapeHtml(suggestion)}
            <button onclick="this.parentNode.remove()" style="
                background: none;
                border: none;
                color: white;
                float: right;
                cursor: pointer;
                font-size: 16px;
                margin-top: -2px;
            ">&times;</button>
        `;

        document.body.appendChild(tip);

        setTimeout(() => {
            if (tip.parentNode) {
                tip.parentNode.removeChild(tip);
            }
        }, 5000);
    }

    async function loadMemoryInsights() {
        try {
            const response = await fetch('/api/memory-insights');
            const data = await response.json();

            const memoryElement = document.getElementById('memoryInsights');
            if (memoryElement && data.success) {
                memoryElement.textContent = data.insights;
            }
        } catch (error) {
            console.log('Memory insights update in progress...');
        }
    }

    async function updateVoiceInsights() {
        loadVoiceInsights();
    }

    async function loadPersonalProfile() {
        try {
            const response = await fetch('/api/personal-profile');
            const data = await response.json();

            const profileElement = document.getElementById('personalProfile');
            if (profileElement && data.success) {
                profileElement.textContent = data.profile;
            }
        } catch (error) {
            console.log('Personal profile update in progress...');
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async function loadConversationSummaries() {
        try {
            const response = await fetch('/api/history');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.success && data.history && Array.isArray(data.history)) {
                const summariesContainer = document.getElementById('conversationSummaries');
                if (summariesContainer) {
                    summariesContainer.innerHTML = '';

                    // Group conversations by date
                    const grouped = {};
                    data.history.forEach(entry => {
                        const date = entry.timestamp ? new Date(entry.timestamp).toDateString() : 'Recent';
                        if (!grouped[date]) {
                            grouped[date] = [];
                        }
                        grouped[date].push(entry);
                    });

                    // Show last 5 dates
                    Object.keys(grouped).slice(-5).forEach(date => {
                        const conversations = grouped[date];
                        const summaryDiv = document.createElement('div');
                        summaryDiv.className = 'conversation-summary mb-2 p-2 bg-secondary rounded';

                        const preview = conversations.slice(0, 2).map(c => 
                            c.message ? c.message.substring(0, 40) + '...' : ''
                        ).filter(p => p).join(' | ');

                        summaryDiv.innerHTML = `
                            <div class="fw-bold small">${escapeHtml(date)}</div>
                            <div class="text-muted small">${conversations.length} conversations</div>
                            <div class="small">${escapeHtml(preview)}</div>
                        `;

                        summariesContainer.appendChild(summaryDiv);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading conversation summaries:', error);
        }
    }

    function groupConversationsByDate(history) {
        const groups = {};
        history.forEach(entry => {
            const date = entry.timestamp ? new Date(entry.timestamp).toDateString() : 'Unknown Date';
            if (!groups[date]) {
                groups[date] = [];
            }
            groups[date].push(entry);
        });
        return groups;
    }

    function createSummaryCard(date, conversations) {
        const card = document.createElement('div');
        card.className = 'col-md-6 mb-2';

        const preview = conversations.slice(0, 3).map(c => 
            c.message ? c.message.substring(0, 50) + '...' : ''
        ).filter(p => p).join(' | ');

        card.innerHTML = `
            <div class="card bg-secondary">
                <div class="card-body p-2">
                    <h6 class="card-title mb-1">${escapeHtml(date)}</h6>
                    <p class="card-text small mb-1">${conversations.length} conversations</p>
                    <p class="card-text small text-muted">${escapeHtml(preview)}</p>
                    <button class="btn btn-sm btn-outline-primary date-conversation-btn">
                        <i class="fas fa-eye me-1"></i>View
                    </button>
                </div>
            </div>
        `;

        // Safely attach event listener without XSS risk
        const button = card.querySelector('.date-conversation-btn');
        button.addEventListener('click', () => loadDateConversations(date));

        return card;
    }

    window.loadDateConversations = function(date) {
        // This function will load conversations for a specific date
        fetch('/api/history')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.history) {
                    const chatHistory = document.getElementById('chat-history');
                    if (chatHistory) {
                        chatHistory.innerHTML = '';

                        const dateConversations = data.history.filter(entry => {
                            const entryDate = entry.timestamp ? new Date(entry.timestamp).toDateString() : 'Unknown Date';
                            return entryDate === date;
                        });

                        dateConversations.forEach(entry => {
                            if (entry.message) {
                                addChatMessage(entry.message, true);
                            }
                            if (entry.response) {
                                addChatMessage(entry.response, false);
                            }
                        });

                        // Hide history panel
                        document.getElementById('historyPanel').style.display = 'none';
                    }
                }
            })
            .catch(error => console.error('Error loading date conversations:', error));
    };

    // History panel functionality - set up after DOM loads
    setTimeout(() => {
        const historyToggle = document.getElementById('historyToggle');
        const historyPanel = document.getElementById('historyPanel');
        const closeHistory = document.getElementById('closeHistory');

        if (historyToggle && historyPanel) {
            historyToggle.addEventListener('click', function() {
                if (historyPanel.style.display === 'none' || !historyPanel.style.display) {
                    historyPanel.style.display = 'block';
                    loadConversationSummaries();
                } else {
                    historyPanel.style.display = 'none';
                }
            });
        }

        if (closeHistory && historyPanel) {
            closeHistory.addEventListener('click', function() {
                historyPanel.style.display = 'none';
            });
        }
    }, 1000);

    // Data Management Functions
    window.initializeDataManagement = function() {
        // Wait a bit for DOM to fully load
        setTimeout(() => {
            console.log('Initializing data management...');
            const exportBtn = document.querySelector('#export-data-btn');
            const importBtn = document.querySelector('#import-data-btn');
            const importInput = document.querySelector('#import-file-input');

            console.log('Export button found:', !!exportBtn);
            console.log('Import button found:', !!importBtn);
            console.log('Import input found:', !!importInput);

            if (exportBtn) {
                // Remove any existing listeners
                exportBtn.removeEventListener('click', exportData);
                exportBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Export button clicked');
                    exportData();
                });
                console.log('Export button listener added');
            }

            if (importBtn && importInput) {
                // Remove any existing listeners
                importBtn.removeEventListener('click', triggerImport);
                importBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Import button clicked');
                    console.log('About to trigger file picker');

                    // Clear any previous value
                    importInput.value = '';

                    // Trigger the file picker
                    importInput.click();

                    console.log('File picker triggered');
                });
                console.log('Import button listener added');
            }

            if (importInput) {
                importInput.removeEventListener('change', handleImportFile);
                importInput.addEventListener('change', function(e) {
                    console.log('File input change event triggered');
                    console.log('Files selected:', e.target.files.length);
                    handleImportFile(e);
                });

                // Also add input event as backup for mobile
                importInput.addEventListener('input', function(e) {
                    console.log('File input event triggered');
                    if (e.target.files.length > 0) {
                        handleImportFile(e);
                    }
                });
                console.log('Import input listeners added');
            }
        }, 500);
    }

    function triggerImport() {
        const importInput = document.querySelector('#import-file-input');
        if (importInput) {
            importInput.click();
        }
    }

    async function exportData() {
        console.log('Export function called');
        const statusDiv = document.querySelector('#data-status');

        try {
            if (statusDiv) {
                statusDiv.textContent = 'Exporting data...';
                statusDiv.className = 'small text-info text-center';
            }

            const response = await fetch('/api/export');
            const data = await response.json();

            if (data.success) {
                // Create download with mobile-friendly approach
                const blob = new Blob([JSON.stringify(data.data, null, 2)], {
                    type: 'application/json'
                });

                const fileName = `roboto-data-${new Date().toISOString().split('T')[0]}.json`;

                // Check if on mobile device
                if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
                    // For mobile, try to use share API or fallback to data URL
                    if (navigator.share) {
                        try {
                            const file = new File([blob], fileName, {
                                type: 'application/json'
                            });
                            await navigator.share({
                                files: [file],
                                title: 'Roboto Data Export'
                            });
                            if (statusDiv) {
                                statusDiv.textContent = 'Data shared successfully!';
                                statusDiv.className = 'small text-success text-center';
                            }
                            return;
                        } catch (shareError) {
                            console.log('Share failed, using fallback');
                        }
                    }

                    // Fallback for mobile: create a data URL
                    const dataUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = dataUrl;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(dataUrl);
                } else {
                    // Desktop download
                    const dataUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = dataUrl;
                    a.download = fileName;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(dataUrl);
                }

                if (statusDiv) {
                                statusDiv.textContent = 'Data shared successfully!';
                                statusDiv.className = 'small text-success text-center';
                            }
                            return;
                        } catch (shareError) {
                            console.log('Share failed, falling back to download');
                        }
                    }

                    // Fallback for mobile
                    const dataUrl = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = dataUrl;
                    a.download = `roboto-data-${new Date().toISOString().split('T')[0]}.json`;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(dataUrl);
                } else {
                    // Desktop download
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `roboto-data-${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }

                if (statusDiv) {
                    statusDiv.textContent = 'Data exported successfully!';
                    statusDiv.className = 'small text-success text-center';
                }
            } else {
                if (statusDiv) {
                    statusDiv.textContent = 'Export failed: ' + data.message;
                    statusDiv.className = 'small text-danger text-center';
                }
            }
        } catch (error) {
            console.error('Export error:', error);
            if (statusDiv) {
                statusDiv.textContent = 'Export failed. Please try again.';
                statusDiv.className = 'small text-danger text-center';
            }
        }

        // Reset status after 3 seconds
        setTimeout(() => {
            if (statusDiv) {
                statusDiv.textContent = 'Export your conversations and memories, or import previous data';
                statusDiv.className = 'small text-muted text-center';
            }
        }, 3000);
    }

    async function handleImportFile(event) {
        console.log('Import file handler called');
        const file = event.target.files[0];
        const statusDiv = document.querySelector('#data-status');

        console.log('Selected file:', file);

        if (!file) {
            console.log('No file selected');
            return;
        }

        try {
            if (statusDiv) {
                statusDiv.textContent = 'Importing data...';
                statusDiv.className = 'small text-info text-center';
            }

            console.log('Reading file...');
            const text = await file.text();
            console.log('File content length:', text.length);

            const importData = JSON.parse(text);
            console.log('Parsed data:', importData);

            // Validate import data structure
            if (!importData.chat_history && !importData.emotional_history && !importData.learned_patterns) {
                throw new Error('Invalid data format - missing required fields');
            }

            const formData = new FormData();
            formData.append('import_data', JSON.stringify(importData));

            console.log('Sending import request...');
            const response = await fetch('/api/import', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Import result:', result);

            if (result.success) {
                if (statusDiv) {
                    statusDiv.textContent = 'Data imported successfully! Refreshing...';
                    statusDiv.className = 'small text-success text-center';
                }

                // Refresh the page to load new data
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                if (statusDiv) {
                    statusDiv.textContent = 'Import failed: ' + result.message;
                    statusDiv.className = 'small text-danger text-center';
                }
            }
        } catch (error) {
            console.error('Import error:', error);
            if (statusDiv) {
                statusDiv.textContent = 'Import failed. Please check your file format.';
                statusDiv.className = 'small text-danger text-center';
            }
        }

        // Reset file input
        event.target.value = '';

        // Reset status after 3 seconds (if not successful)
        setTimeout(() => {
            if (statusDiv && !statusDiv.textContent.includes('successfully')) {
                statusDiv.textContent = 'Export your conversations and memories, or import previous data';
                statusDiv.className = 'small text-muted text-center';
            }
        }, 3000);
    }

    // Initialize data management when DOM is loaded
    initializeDataManagement();
});