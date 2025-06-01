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
    
    // Text-to-speech functionality
    let ttsEnabled = localStorage.getItem('ttsEnabled') !== 'false';
    const ttsBtn = document.getElementById('ttsBtn');
    
    if (ttsBtn) {
        updateTTSButton();
        ttsBtn.addEventListener('click', function() {
            ttsEnabled = !ttsEnabled;
            localStorage.setItem('ttsEnabled', ttsEnabled);
            updateTTSButton();
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
                        const utterance = new SpeechSynthesisUtterance(data.response);
                        utterance.rate = 0.9;
                        utterance.pitch = 1;
                        utterance.volume = 0.8;
                        window.speechSynthesis.speak(utterance);
                    }
                    
                    // Update personal profile after each interaction
                    setTimeout(loadPersonalProfile, 1000);
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
        if (!chatHistory) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message mb-2 ${isUser ? 'user-message' : 'bot-message'}`;
        
        const time = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'}">
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
            const response = await fetch('/api/chat/history');
            const data = await response.json();
            
            if (data.success && data.history) {
                chatHistory.innerHTML = '';
                data.history.slice(-10).forEach(entry => {
                    if (entry.message) {
                        addChatMessage(entry.message, true);
                    }
                    if (entry.response) {
                        addChatMessage(entry.response, false);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async function loadEmotionalStatus() {
        try {
            const response = await fetch('/api/emotional-status');
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
    
    async function updateVoiceInsights() {
        try {
            const response = await fetch('/api/voice-insights');
            const data = await response.json();
            
            if (data.success && data.insights) {
                console.log('Voice Recognition Learning:', data.insights);
                // You could display this in the UI if desired
            }
        } catch (error) {
            console.log('Voice insights update in progress...');
        }
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
});