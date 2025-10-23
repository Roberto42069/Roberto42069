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
    let selectedVoiceIndex = parseInt(localStorage.getItem('selectedVoiceIndex') || '0');
    const ttsBtn = document.getElementById('ttsBtn');
    
    // Update TTS status in UI
    function updateTTSStatus(status) {
        const ttsStatusEl = document.getElementById('ttsStatus');
        if (ttsStatusEl) {
            ttsStatusEl.textContent = status;
            
            // Update color based on status
            if (status.includes('Ready') || status.includes('voices')) {
                ttsStatusEl.className = 'text-success';
            } else if (status.includes('Loading') || status.includes('Retrying')) {
                ttsStatusEl.className = 'text-warning';
            } else if (status.includes('Unavailable') || status.includes('Error')) {
                ttsStatusEl.className = 'text-danger';
            } else {
                ttsStatusEl.className = 'text-muted';
            }
        }
    }

    // Initialize speech synthesis for cross-browser compatibility
    function initializeTTS() {
        if ('speechSynthesis' in window) {
            // Load available voices
            function loadVoices() {
                availableVoices = speechSynthesis.getVoices();
                console.log('Available TTS voices:', availableVoices.length);
                
                // Create voice selector if voices available
                if (availableVoices.length > 0) {
                    createVoiceSelector();
                    showToast(`🎤 ${availableVoices.length} voices available for text-to-speech`, 'success');
                    updateTTSStatus(`Ready (${availableVoices.length} voices)`);
                } else {
                    updateTTSStatus('Loading...');
                }
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
            showToast('⚠️ Text-to-speech not supported in this browser', 'warning');
            updateTTSStatus('Unavailable');
        }
    }
    
    // Create voice selector dropdown
    function createVoiceSelector() {
        const existingSelector = document.getElementById('voiceSelector');
        if (existingSelector || availableVoices.length === 0) return;
        
        const voiceSelectorContainer = document.createElement('div');
        voiceSelectorContainer.className = 'd-inline-block ms-2';
        voiceSelectorContainer.innerHTML = `
            <select id="voiceSelector" class="form-select form-select-sm" style="width: auto; max-width: 200px;">
                ${availableVoices.map((voice, index) => 
                    `<option value="${index}" ${index === selectedVoiceIndex ? 'selected' : ''}>
                        ${voice.name} (${voice.lang})
                    </option>`
                ).join('')}
            </select>
        `;
        
        // Add to TTS button container if it exists
        const ttsBtn = document.getElementById('ttsBtn');
        if (ttsBtn && ttsBtn.parentElement) {
            ttsBtn.parentElement.appendChild(voiceSelectorContainer);
        }
        
        // Add change listener
        const selector = voiceSelectorContainer.querySelector('#voiceSelector');
        selector.addEventListener('change', function(e) {
            selectedVoiceIndex = parseInt(e.target.value);
            localStorage.setItem('selectedVoiceIndex', selectedVoiceIndex);
            
            // Test the selected voice
            const selectedVoice = availableVoices[selectedVoiceIndex];
            showToast(`🔊 Voice changed to: ${selectedVoice.name}`, 'info');
            speakText(`Hello! I'm now using the ${selectedVoice.name} voice.`);
        });
    }
    
    // Enhanced speak function with cross-browser support and voice selection
    function speakText(text, skipToast = false) {
        if (!ttsEnabled || !text || !('speechSynthesis' in window)) {
            return;
        }
        
        try {
            // 1. Voice Availability Check - Prevent errors before they happen
            if (availableVoices.length === 0) {
                console.warn('No voices available for TTS');
                if (!skipToast) {
                    showToast('🔄 Loading voices, please wait...', 'info');
                }
                // Retry after voices load
                setTimeout(() => {
                    if (availableVoices.length > 0) {
                        speakText(text, skipToast);
                    } else {
                        showToast('⚠️ Text-to-speech voices unavailable', 'warning');
                    }
                }, 500);
                return;
            }
            
            // Cancel any ongoing speech
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Configure voice settings for better compatibility
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            utterance.volume = 0.9;
            
            // Use selected voice or best available with validation
            let voiceToUse = null;
            if (availableVoices.length > 0) {
                const selectedVoice = availableVoices[selectedVoiceIndex];
                if (selectedVoice) {
                    voiceToUse = selectedVoice;
                } else {
                    // Fallback to first English voice or any available
                    const englishVoice = availableVoices.find(voice => 
                        voice.lang.startsWith('en')
                    ) || availableVoices[0];
                    
                    if (englishVoice) {
                        voiceToUse = englishVoice;
                    }
                }
            }
            
            // Only set voice if we found a valid one
            if (voiceToUse) {
                utterance.voice = voiceToUse;
            }
            
            utterance.onstart = function() {
                console.log('TTS started');
                if (!skipToast) {
                    showToast('🔊 Speaking...', 'info');
                }
            };
            
            utterance.onend = function() {
                console.log('TTS completed');
            };
            
            utterance.onerror = function(event) {
                console.error('TTS error:', event.error);
                
                // 4. Clearer user notifications based on error type
                let userMessage = '';
                let shouldRetry = false;
                
                switch(event.error) {
                    case 'synthesis-failed':
                        userMessage = '🔊 Speech synthesis failed. Using fallback voice...';
                        shouldRetry = true;
                        updateTTSStatus('Retrying...');
                        break;
                    case 'synthesis-unavailable':
                        userMessage = '⚠️ Speech not available right now. Check your connection.';
                        updateTTSStatus('Unavailable');
                        break;
                    case 'voice-unavailable':
                        userMessage = '🔄 Selected voice unavailable. Switching to default...';
                        shouldRetry = true;
                        updateTTSStatus('Switching voice...');
                        break;
                    case 'audio-busy':
                        userMessage = '🔇 Audio system is busy. Please try again.';
                        updateTTSStatus('Audio busy');
                        break;
                    case 'network':
                        userMessage = '📡 Network issue. Retrying speech...';
                        shouldRetry = true;
                        updateTTSStatus('Network error');
                        break;
                    default:
                        userMessage = `⚠️ Speech unavailable (${event.error})`;
                        updateTTSStatus('Error');
                }
                
                showToast(userMessage, 'warning');
                
                // Retry with fallback voice if appropriate
                if (shouldRetry && availableVoices.length > 0) {
                    console.log('Retrying TTS with fallback voice');
                    const fallbackUtterance = new SpeechSynthesisUtterance(text);
                    fallbackUtterance.voice = availableVoices[0]; // Use first available voice
                    fallbackUtterance.rate = 1.0; // Normal rate
                    
                    fallbackUtterance.onerror = function(retryEvent) {
                        console.error('Fallback TTS also failed:', retryEvent.error);
                        showToast('❌ Text-to-speech unavailable', 'error');
                        updateTTSStatus('Failed');
                    };
                    
                    fallbackUtterance.onend = function() {
                        updateTTSStatus(`Ready (${availableVoices.length} voices)`);
                    };
                    
                    speechSynthesis.speak(fallbackUtterance);
                }
            };
            
            speechSynthesis.speak(utterance);
        } catch (error) {
            console.error('TTS error:', error);
            showToast('❌ Unable to speak text', 'error');
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
                
                // Check if user needs to authenticate
                if (response.status === 403 || response.status === 401) {
                    addChatMessage('Please log in to chat with Roboto SAI. Click the login button above.', false);
                    return;
                }
                
                // Check if response is not ok
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // Try to parse JSON, handle non-JSON responses
                let data;
                try {
                    data = await response.json();
                } catch (jsonError) {
                    console.error('Response is not valid JSON:', await response.text());
                    throw new Error('Invalid server response');
                }
                
                if (data.success && data.response) {
                    addChatMessage(data.response, false);
                    
                    // Auto-speak response if TTS is enabled
                    if (ttsEnabled) {
                        speakText(data.response, true); // Skip toast for auto-speak
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
            const response = await fetch('/api/chat_history');
            
            // Check if user needs to authenticate
            if (response.status === 403 || response.status === 401) {
                console.log('Chat history requires authentication');
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
                return;
            }
            
            const history = data.chat_history || data.history || [];
            if (data.success && Array.isArray(history)) {
                const chatHistoryElement = document.getElementById('chatHistory') || document.getElementById('chat-history');
                if (chatHistoryElement) {
                    // Keep the creator introduction, only remove loading indicator
                    const loadingIndicator = chatHistoryElement.querySelector('#loading-indicator');
                    if (loadingIndicator) {
                        loadingIndicator.remove();
                    }
                    
                    console.log(`Loading ${history.length} conversations`);
                    
                    // 🚀 PERFORMANCE OPTIMIZATION: Load conversations in batches
                    // Load most recent 100 conversations first for instant display
                    const INITIAL_LOAD = 100;
                    const recentHistory = history.slice(-INITIAL_LOAD);
                    const olderHistory = history.slice(0, -INITIAL_LOAD);
                    
                    // Load recent conversations immediately
                    recentHistory.forEach(entry => {
                        if (entry.message) {
                            addChatMessage(entry.message, true);
                        }
                        if (entry.response) {
                            addChatMessage(entry.response, false);
                        }
                    });
                    
                    // Add "Load More" button if there are older conversations
                    if (olderHistory.length > 0) {
                        const loadMoreBtn = document.createElement('div');
                        loadMoreBtn.id = 'load-more-history';
                        loadMoreBtn.className = 'text-center my-3';
                        loadMoreBtn.innerHTML = `
                            <button class="btn btn-outline-primary btn-sm" onclick="loadOlderConversations()">
                                <i class="fas fa-history"></i> Load ${olderHistory.length} older conversations
                            </button>
                        `;
                        chatHistoryElement.insertBefore(loadMoreBtn, chatHistoryElement.firstChild);
                        
                        // Store older history for later loading
                        window.olderChatHistory = olderHistory;
                    }
                    
                    // Ensure chat history container is always visible
                    chatHistoryElement.style.display = 'block';
                    chatHistoryElement.style.visibility = 'visible';
                    chatHistoryElement.style.opacity = '1';
                    
                    // Scroll to bottom to show most recent messages
                    setTimeout(() => {
                        chatHistoryElement.scrollTop = chatHistoryElement.scrollHeight;
                    }, 100);
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            // Always show chat history container even on error
            const chatHistoryElement = document.getElementById('chatHistory') || document.getElementById('chat-history');
            if (chatHistoryElement) {
                chatHistoryElement.style.display = 'block';
                chatHistoryElement.style.visibility = 'visible';
                
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
    
    function startSecureSpeechRecognition() {
        // Check for speech recognition support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            showToast('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.', 'warning');
            return;
        }
        
        try {
            // Clean up any existing recognition
            if (recognition) {
                recognition.abort();
                recognition = null;
            }
            
            // Initialize speech recognition (it will handle microphone permissions automatically)
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 1;
            
            // Track recognition state
            let recognitionActive = false;
            let shouldRestart = false;
            
            // Event handlers
            recognition.onstart = function() {
                recognitionActive = true;
                isListening = true;
                updateVoiceButtonState(true);
                showToast('🎤 Listening... Speak now!', 'success');
                console.log('Speech recognition started');
            };
            
            recognition.onend = function() {
                recognitionActive = false;
                console.log('Speech recognition ended');
                
                // Only restart if user hasn't explicitly stopped and we want continuous listening
                if (isListening && shouldRestart) {
                    setTimeout(() => {
                        if (isListening && !recognitionActive) {
                            try {
                                recognition.start();
                                shouldRestart = false;
                            } catch (error) {
                                console.error('Error restarting recognition:', error);
                                isListening = false;
                                updateVoiceButtonState(false);
                            }
                        }
                    }, 500); // Increased delay to avoid conflicts
                } else {
                    isListening = false;
                    updateVoiceButtonState(false);
                }
            };
            
            // Set flag for auto-restart on speech detection
            recognition.onspeechend = function() {
                shouldRestart = isListening; // Only restart if still in listening mode
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
                
                // Show interim results in input field with visual feedback
                if (chatInput) {
                    chatInput.value = finalTranscript + interimTranscript;
                    // Add visual feedback for active speech
                    if (interimTranscript) {
                        chatInput.style.borderColor = '#28a745';
                        chatInput.style.boxShadow = '0 0 5px rgba(40, 167, 69, 0.5)';
                    }
                }
                
                // Process final result for speech-to-speech
                if (finalTranscript) {
                    const confidence = event.results[event.results.length - 1][0].confidence || 0.5;
                    console.log(`Voice recognition confidence: ${confidence}`);
                    
                    // Show confidence indicator
                    showVoiceConfidenceIndicator(confidence);
                    
                    // Optimize based on confidence level
                    if (confidence < 0.7) {
                        optimizeVoiceRecognition(finalTranscript, confidence);
                    }
                    
                    // Reset input field visual feedback
                    if (chatInput) {
                        chatInput.style.borderColor = '';
                        chatInput.style.boxShadow = '';
                    }
                    
                    // Submit with optimized delay
                    const submitDelay = confidence > 0.8 ? 300 : 500;
                    setTimeout(() => {
                        if (chatForm) {
                            // Show processing feedback
                            showToast('💭 Processing your message...', 'info');
                            chatForm.dispatchEvent(new Event('submit'));
                        }
                        // Update voice insights
                        setTimeout(updateVoiceInsights, 1000);
                    }, submitDelay);
                    
                    // Set restart flag for continuous conversation
                    shouldRestart = true;
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                
                // Don't reset state for recoverable errors
                const recoverableErrors = ['aborted', 'no-speech'];
                
                if (!recoverableErrors.includes(event.error)) {
                    isListening = false;
                    recognitionActive = false;
                    updateVoiceButtonState(false);
                }
                
                let errorMessage = '';
                let errorType = 'error';
                
                switch(event.error) {
                    case 'not-allowed':
                    case 'service-not-allowed':
                        errorMessage = '🎤 Microphone access denied. Please allow microphone permissions in your browser settings.';
                        break;
                    case 'no-speech':
                        // Don't show error for no-speech, just log it
                        console.log('No speech detected, continuing to listen...');
                        shouldRestart = isListening;
                        return;
                    case 'audio-capture':
                        errorMessage = '🎤 Microphone not available. Please check if another app is using it or if it\'s properly connected.';
                        break;
                    case 'network':
                        errorMessage = '📡 Speech recognition network error. The browser\'s speech service may be unavailable. Please type your message instead or try again later.';
                        errorType = 'warning';
                        // Auto-retry after a delay if still listening
                        if (isListening) {
                            setTimeout(() => {
                                console.log('Auto-retrying speech recognition after network error...');
                                if (isListening) {
                                    startSpeechRecognition();
                                }
                            }, 3000); // Retry after 3 seconds
                        }
                        break;
                    case 'aborted':
                        // Silently handle aborted errors (normal when stopping or restarting)
                        console.log('Recognition aborted (normal during restart)');
                        return;
                    default:
                        errorMessage = `⚠️ Speech recognition error: ${event.error}`;
                        errorType = 'warning';
                }
                
                if (errorMessage) {
                    showToast(errorMessage, errorType);
                }
            };
            
            // Start recognition
            recognition.start();
            
        } catch (error) {
            console.error('Speech recognition initialization error:', error);
            isListening = false;
            updateVoiceButtonState(false);
            showToast('❌ Unable to start speech recognition. Please try again.', 'error');
        }
    }
    
    function stopSpeechRecognition() {
        if (recognition) {
            isListening = false;
            try {
                recognition.abort(); // Use abort instead of stop for immediate termination
            } catch (error) {
                console.log('Error stopping recognition:', error);
            }
            recognition = null;
            updateVoiceButtonState(false);
            showToast('🛑 Speech recognition stopped', 'info');
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
        // Remove any existing confidence indicator
        const existingIndicator = document.querySelector('.voice-confidence-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }
        
        const indicator = document.createElement('div');
        indicator.className = 'voice-confidence-indicator';
        
        // Color based on confidence level
        const bgColor = confidence > 0.8 ? '40, 167, 69' : // Green for high confidence
                       confidence > 0.6 ? '255, 193, 7' : // Yellow for medium
                       '220, 53, 69'; // Red for low
        
        indicator.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: rgba(${bgColor}, 0.9);
            color: white;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            z-index: 1050;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        `;
        
        const confidencePercent = Math.round(confidence * 100);
        const confidenceEmoji = confidence > 0.8 ? '✅' : confidence > 0.6 ? '⚠️' : '❌';
        
        indicator.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>${confidenceEmoji}</span>
                <span>Recognition: ${confidencePercent}%</span>
            </div>
        `;
        
        document.body.appendChild(indicator);
        
        // Auto-hide with fade out
        setTimeout(() => {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateX(100px)';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }, 3000);
    }
    
    function showVoiceOptimizationTip(suggestion) {
        // Remove any existing tip
        const existingTip = document.querySelector('.voice-optimization-tip');
        if (existingTip) {
            existingTip.remove();
        }
        
        const tip = document.createElement('div');
        tip.className = 'voice-optimization-tip';
        tip.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, rgba(40, 167, 69, 0.95), rgba(34, 139, 58, 0.95));
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 1050;
            max-width: 400px;
            text-align: left;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            animation: slideUp 0.3s ease;
        `;
        tip.innerHTML = `
            <div style="display: flex; align-items: start; gap: 10px;">
                <span style="font-size: 18px;">💡</span>
                <div style="flex: 1;">
                    <strong style="display: block; margin-bottom: 5px;">Voice Tip</strong>
                    <span>${escapeHtml(suggestion)}</span>
                </div>
                <button onclick="this.parentNode.parentNode.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    font-size: 20px;
                    line-height: 1;
                    opacity: 0.8;
                    transition: opacity 0.2s;
                    padding: 0;
                    margin: -5px -5px 0 0;
                " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">&times;</button>
            </div>
        `;
        
        document.body.appendChild(tip);
        
        // Auto-hide with animation
        setTimeout(() => {
            tip.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => {
                if (tip.parentNode) {
                    tip.parentNode.removeChild(tip);
                }
            }, 300);
        }, 6000);
    }
    
    // Add CSS animations dynamically if not already present
    function addSpeechAnimations() {
        if (document.getElementById('speech-animations')) return;
        
        const style = document.createElement('style');
        style.id = 'speech-animations';
        style.textContent = `
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(100px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateX(-50%) translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
            
            @keyframes slideDown {
                from {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(-50%) translateY(20px);
                }
            }
            
            .voice-confidence-indicator,
            .voice-optimization-tip {
                will-change: transform, opacity;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize animations on page load
    addSpeechAnimations();
    
    async function loadMemoryInsights() {
        try {
            const response = await fetch('/api/learning-insights');
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
                const jsonString = JSON.stringify(data.data, null, 2);
                const blob = new Blob([jsonString], {
                    type: 'application/json'
                });
                
                const filename = `roboto-data-${new Date().toISOString().split('T')[0]}.json`;
                
                // Check if on iOS/iPhone
                const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
                const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
                
                if (isIOS || isSafari) {
                    // iOS-specific approach
                    // Try Web Share API first (works best on iOS)
                    if (navigator.share && navigator.canShare && navigator.canShare({ files: [new File([blob], filename)] })) {
                        try {
                            const file = new File([blob], filename, {
                                type: 'application/json',
                                lastModified: new Date().getTime()
                            });
                            await navigator.share({
                                files: [file],
                                title: 'Roboto SAI Data Export',
                                text: 'Your Roboto conversations and memories'
                            });
                            if (statusDiv) {
                                statusDiv.textContent = 'Data exported successfully! Check your Files app or selected location.';
                                statusDiv.className = 'small text-success text-center';
                            }
                            return;
                        } catch (shareError) {
                            console.log('Share API failed, trying alternative method:', shareError);
                        }
                    }
                    
                    // Fallback: Create download link with proper iOS handling
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const link = document.createElement('a');
                        link.href = e.target.result;
                        link.download = filename;
                        link.style.display = 'none';
                        
                        // iOS requires the link to be in the DOM
                        document.body.appendChild(link);
                        
                        // Trigger click
                        link.click();
                        
                        // Clean up
                        setTimeout(() => {
                            document.body.removeChild(link);
                        }, 100);
                        
                        if (statusDiv) {
                            statusDiv.textContent = 'Data ready! Tap to save to Files or iCloud.';
                            statusDiv.className = 'small text-success text-center';
                        }
                    };
                    reader.readAsDataURL(blob);
                    
                } else if (/Android/i.test(navigator.userAgent)) {
                    // Android approach
                    if (navigator.share) {
                        try {
                            const file = new File([blob], filename, {
                                type: 'application/json'
                            });
                            await navigator.share({
                                files: [file],
                                title: 'Roboto Data Export'
                            });
                            if (statusDiv) {
                                statusDiv.textContent = 'Data exported successfully!';
                                statusDiv.className = 'small text-success text-center';
                            }
                            return;
                        } catch (shareError) {
                            console.log('Share failed, falling back to download');
                        }
                    }
                    
                    // Fallback for Android
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    a.target = '_blank';
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }, 100);
                    
                } else {
                    // Desktop download
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }, 100);
                }
                
                if (statusDiv && !statusDiv.textContent.includes('successfully')) {
                    statusDiv.textContent = 'Data exported successfully!';
                    statusDiv.className = 'small text-success text-center';
                }
            } else {
                if (statusDiv) {
                    statusDiv.textContent = 'Export failed: ' + (data.message || 'Unknown error');
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
        
        // Reset status after 5 seconds
        setTimeout(() => {
            if (statusDiv && !statusDiv.textContent.includes('tap to save')) {
                statusDiv.textContent = 'Export your conversations and memories, or import previous data';
                statusDiv.className = 'small text-muted text-center';
            }
        }, 5000);
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
    
    // Toast notification system
    function showToast(message, type = 'info') {
        const toastElement = document.getElementById('notificationToast');
        const toastBody = document.getElementById('toastBody');
        
        if (!toastElement || !toastBody) {
            console.warn('Toast elements not found');
            return;
        }
        
        // Set message
        toastBody.textContent = message;
        
        // Set background color based on type
        const toastHeader = toastElement.querySelector('.toast-header');
        if (toastHeader) {
            toastHeader.className = 'toast-header';
            switch(type) {
                case 'error':
                    toastHeader.classList.add('bg-danger', 'text-white');
                    break;
                case 'success':
                    toastHeader.classList.add('bg-success', 'text-white');
                    break;
                case 'warning':
                    toastHeader.classList.add('bg-warning', 'text-dark');
                    break;
                case 'info':
                default:
                    toastHeader.classList.add('bg-info', 'text-white');
                    break;
            }
        }
        
        // Show toast using Bootstrap
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 4000
        });
        toast.show();
    }

    // Function to load older conversations in batches
    window.loadOlderConversations = function() {
        const BATCH_SIZE = 100;
        const chatHistoryElement = document.getElementById('chatHistory') || document.getElementById('chat-history');
        const loadMoreBtn = document.getElementById('load-more-history');
        
        if (!window.olderChatHistory || window.olderChatHistory.length === 0) {
            if (loadMoreBtn) loadMoreBtn.remove();
            return;
        }
        
        // Load next batch
        const batch = window.olderChatHistory.slice(-BATCH_SIZE);
        const remaining = window.olderChatHistory.slice(0, -BATCH_SIZE);
        
        // Insert batch before the current first message
        const firstMessage = chatHistoryElement.querySelector('.chat-message');
        batch.forEach(entry => {
            if (entry.message) {
                const userMsg = createChatMessageElement(entry.message, true);
                chatHistoryElement.insertBefore(userMsg, firstMessage);
            }
            if (entry.response) {
                const botMsg = createChatMessageElement(entry.response, false);
                chatHistoryElement.insertBefore(botMsg, firstMessage);
            }
        });
        
        // Update remaining history
        window.olderChatHistory = remaining;
        
        // Update or remove button
        if (remaining.length > 0) {
            const btn = loadMoreBtn.querySelector('button');
            if (btn) {
                btn.innerHTML = `<i class="fas fa-history"></i> Load ${remaining.length} more conversations`;
            }
        } else {
            if (loadMoreBtn) loadMoreBtn.remove();
            showToast('All conversations loaded!', 'success');
        }
    };
    
    // Helper function to create chat message element
    function createChatMessageElement(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isUser ? 'user-message' : 'bot-message'} mb-3`;
        
        const messageContent = document.createElement('div');
        messageContent.className = isUser ? 'bg-primary text-white p-3 rounded' : 'bg-dark text-white p-3 rounded';
        messageContent.textContent = text;
        
        messageDiv.appendChild(messageContent);
        return messageDiv;
    }

    // Initialize data management when DOM is loaded
    initializeDataManagement();
});