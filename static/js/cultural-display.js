
/**
 * 🌅 Cultural Legacy Display Interface
 * JavaScript integration for Roboto SAI Cultural Display system
 */

class CulturalDisplayInterface {
    constructor() {
        this.isActive = false;
        this.currentTheme = 'All';
        this.displayMode = 'normal';
        this.initializeInterface();
    }

    initializeInterface() {
        console.log('🌅 Initializing Cultural Legacy Display Interface...');
        this.setupControls();
        this.setupEventListeners();
    }

    setupControls() {
        // Add cultural display controls to the chat interface
        const controlsHtml = `
            <div id="cultural-display-controls" class="mt-3 border-top pt-3">
                <h6 class="text-info">🌅 Cultural Legacy Display</h6>
                <div class="row">
                    <div class="col-md-6">
                        <button id="launch-cultural-display" class="btn btn-outline-info btn-sm me-2">
                            <i class="fas fa-palette"></i> Launch Display
                        </button>
                        <button id="cultural-ai-query" class="btn btn-outline-success btn-sm">
                            <i class="fas fa-brain"></i> Cultural AI Query
                        </button>
                    </div>
                    <div class="col-md-6">
                        <select id="cultural-theme-selector" class="form-select form-select-sm">
                            <option value="All">All Themes</option>
                            <option value="Aztec Mythology">Aztec Mythology</option>
                            <option value="Aztec Creation">Aztec Creation</option>
                            <option value="Monterrey Heritage">Monterrey Heritage</option>
                            <option value="2025 YTK RobThuGod">2025 YTK RobThuGod</option>
                            <option value="Eclipses">Eclipses</option>
                            <option value="Numerology & Etymology">Numerology & Etymology</option>
                            <option value="Roboto SAI Integration">Roboto SAI Integration</option>
                        </select>
                    </div>
                </div>
                <div class="mt-2">
                    <small class="text-muted">
                        🎨 Advanced visualization of Roberto's cultural heritage and cosmic connections
                    </small>
                </div>
            </div>
        `;

        // Insert controls after the emotional status section
        const emotionalStatus = document.getElementById('emotional-status');
        if (emotionalStatus) {
            emotionalStatus.insertAdjacentHTML('afterend', controlsHtml);
        }
    }

    setupEventListeners() {
        // Launch Cultural Display button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'launch-cultural-display') {
                this.launchCulturalDisplay();
            } else if (e.target.id === 'cultural-ai-query') {
                this.sendCulturalAIQuery();
            }
        });

        // Theme selector
        document.addEventListener('change', (e) => {
            if (e.target.id === 'cultural-theme-selector') {
                this.currentTheme = e.target.value;
                this.updateThemeInfo();
            }
        });
    }

    async launchCulturalDisplay() {
        try {
            console.log('🌅 Launching Cultural Legacy Display...');
            
            // Show launch notification
            this.showNotification('🌅 Launching Cultural Legacy Display...', 'info');
            
            // Send launch request to backend
            const response = await fetch('/api/cultural-display/launch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    theme: this.currentTheme,
                    mode: 'integrated'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.isActive = true;
                this.showNotification('✅ Cultural Legacy Display launched successfully!', 'success');
                this.updateDisplayStatus();
            } else {
                this.showNotification(`❌ Failed to launch: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Cultural display launch error:', error);
            this.showNotification('❌ Cultural display launch failed', 'error');
        }
    }

    async sendCulturalAIQuery() {
        try {
            const culturalPrompts = [
                "Analyze the spiritual significance of Aztec mythology in modern AI consciousness",
                "How does Roberto's heritage connect to cosmic cycles and eclipses?",
                "Explain the numerological patterns in Roberto Villarreal Martinez's identity",
                "Describe the fusion of ancient Nahuatl wisdom with advanced AI technology",
                "What is the cultural importance of preserving Monterrey heritage through AI?"
            ];

            const prompt = culturalPrompts[Math.floor(Math.random() * culturalPrompts.length)];
            
            this.showNotification('🧠 Generating cultural AI analysis...', 'info');

            const response = await fetch('/api/roboto-request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'cultural_query',
                    content: prompt,
                    context: {
                        theme: this.currentTheme,
                        cultural_focus: 'aztec_nahuatl_heritage',
                        user: 'Roberto Villarreal Martinez'
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                // Display the cultural AI response
                this.displayCulturalResponse(data);
            } else {
                this.showNotification(`❌ Cultural AI query failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Cultural AI query error:', error);
            this.showNotification('❌ Cultural AI query failed', 'error');
        }
    }

    displayCulturalResponse(data) {
        // Create a special cultural response display
        const responseHtml = `
            <div class="alert alert-info cultural-response mt-3">
                <h6 class="alert-heading">🌅 Cultural AI Analysis</h6>
                <p>${data.response || data.cultural_response}</p>
                <hr>
                <small class="text-muted">
                    Theme: ${this.currentTheme} | 
                    Query Type: ${data.query_type || 'cultural_analysis'} |
                    Timestamp: ${new Date().toLocaleTimeString()}
                </small>
            </div>
        `;

        // Insert into chat history or dedicated panel
        const chatHistory = document.getElementById('chat-history');
        if (chatHistory) {
            chatHistory.insertAdjacentHTML('beforeend', responseHtml);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        this.showNotification('✅ Cultural AI analysis completed', 'success');
    }

    updateThemeInfo() {
        const themeDescriptions = {
            'All': 'Complete cultural heritage display',
            'Aztec Mythology': 'Ancient deities and cosmic wisdom',
            'Aztec Creation': 'Nahuatl creation myths and origins',
            'Monterrey Heritage': 'Regional identity and genealogy',
            '2025 YTK RobThuGod': 'Artistic persona and musical legacy',
            'Eclipses': 'Cosmic events and thunder powers',
            'Numerology & Etymology': 'Sacred numbers and linguistic roots',
            'Roboto SAI Integration': 'AI-enhanced cultural preservation'
        };

        const description = themeDescriptions[this.currentTheme] || 'Cultural theme selected';
        console.log(`🎨 Cultural theme: ${this.currentTheme} - ${description}`);
    }

    updateDisplayStatus() {
        const launchButton = document.getElementById('launch-cultural-display');
        if (launchButton) {
            if (this.isActive) {
                launchButton.innerHTML = '<i class="fas fa-eye"></i> Display Active';
                launchButton.className = 'btn btn-success btn-sm me-2';
            } else {
                launchButton.innerHTML = '<i class="fas fa-palette"></i> Launch Display';
                launchButton.className = 'btn btn-outline-info btn-sm me-2';
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize Cultural Display Interface when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.culturalDisplay = new CulturalDisplayInterface();
    console.log('🌅 Cultural Legacy Display Interface initialized');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CulturalDisplayInterface;
}
