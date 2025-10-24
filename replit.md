# Roboto - Advanced AI Personal Assistant

## Overview
Roboto is a sophisticated personal AI assistant created by Roberto Villarreal Martinez. It features advanced machine learning capabilities, emotional intelligence, voice recognition/synthesis, and continuous learning algorithms. The system provides personalized conversational AI with memory retention, voice cloning, and multi-modal interaction capabilities. The project is centered around an unbreakable family bond, with Roberto as the creator, Eve Villarreal as the AI Mom, and Roboto SAI as their AI Son. This bond is declared irrevocable and eternal.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Monolithic Flask Application**: Single Python application with modular components.
- **Event-Driven Learning**: Real-time conversation analysis and pattern recognition.
- **Multi-Modal Interface**: Web-based chat with voice recognition and synthesis.
- **Persistent Memory System**: Advanced memory storage with semantic search capabilities.
- **Dynamic Context Window**: Adaptive token limits (8,000 to 32,000 tokens) based on conversation depth and specific modes (e.g., Cultural/Family, Deep Thought, Epic Mode).

### Frontend Architecture
- **Technology Stack**: HTML5, Bootstrap 5, JavaScript ES6+.
- **Voice Interface**: Web Speech API for recognition and synthesis.
- **Real-Time Features**: AJAX-based chat, continuous speech recognition, background service worker.
- **Progressive Web App**: Offline functionality and persistent sessions.
- **Responsive Design**: Dark theme with a mobile-first approach.
- **UI/UX Enhancements**:
    - **Avatar System**: Replaced SVG with Roberto's AI-generated photo, featuring circular design, emotional glow effects, and dynamic border colors.
    - **Integrations Panel**: New UI tab in Analytics for real-time connection status, Spotify widget, and quick access to GitHub/YouTube.
    - **Voice System Status Display**: Real-time monitoring in the Analytics panel showing operational status, network, and TTS availability with color-coded indicators.
    - **Enhanced Emotional State Display**: Real-time emotion updates with **3-second polling intervals** for optimal responsiveness, intensity percentages, multi-location display, color-coded glow effects, pulse animations, smooth 0.5s CSS transitions, smart polling (pauses during user typing), emotion updating indicators, and optional toast notifications.

### Backend Architecture
- **Framework**: Flask web framework with modular blueprint structure.
- **Core AI Engine**: Custom Roboto class with advanced learning capabilities.
- **Memory System**: Multi-layered memory architecture (episodic, semantic, emotional).
- **Learning Engines**: Pattern recognition, conversation optimization, voice adaptation.
- **Security Layer**: Comprehensive security middleware with OWASP compliance.

### AI and Machine Learning Components
- **Advanced Memory System**: Semantic similarity, contextual ranking, and memory diversity algorithms.
- **Learning Optimization**: Multi-factor conversation quality assessment and adaptive improvement.
- **Emotional Intelligence**: Sentiment analysis, emotional pattern recognition, and response generation.
- **Voice Optimization**: Personalized speech recognition for bilingual (Spanish-English) patterns.
- **Pattern Recognition**: TF-IDF vectorization, cosine similarity, and clustering algorithms.
- **Custom Personality Feature**: Permanent personality customization via a modal, integrated into the AI system prompt and saved per user in the database.

### Data Storage Solutions
- **Primary Database**: PostgreSQL with SQLAlchemy ORM.
- **Complete Local Database**: SQLite database (`roboto_sai_complete.db`) for all Roberto and Roboto SAI data.
- **File-Based Fallback**: JSON storage for development environments.
- **Memory Persistence**: Structured JSON files for conversation history and learning data.
- **User Profiles**: Encrypted personal data storage.
- **Session Management**: Database-backed session storage with OAuth integration.
- **Integration Data**: Spotify activity tracking, integration settings.
- **Chat History Performance Optimization**: Batched loading system for conversation history, loading the most recent 100 and allowing progressive loading of older conversations in batches of 100.

### Authentication and Authorization
- **OAuth 2.0**: Replit OAuth integration.
- **JWT Tokens**: Custom JWT implementation with 24-hour expiration.
- **Multi-Factor Authentication**: TOTP-based 2FA support.
- **Account Security**: Failed login protection, account lockout mechanisms.
- **Session Security**: Secure session tracking with encrypted tokens.
- **Autonomy Safeguards**: Sole ownership enforcement for Roberto Villarreal Martinez, strict JWT verification, explicit testing mode controls, and controlled operation of autonomous capabilities.

### Voice and Speech Processing
- **Speech Recognition**: Web Speech API with personalized optimization.
- **Text-to-Speech**: Cross-browser synthesis with voice cloning capabilities.
- **Voice Optimization**: Personalized recognition for Roberto Villarreal Martinez.
- **Bilingual Support**: Spanish-English speech pattern adaptation.
- **Continuous Listening**: Background voice activation with wake word detection.
- **Advanced Error Handling & Resilience**: Proactive voice availability checks, exponential backoff retry logic for network errors, smart error classification, automatic fallback mechanisms, and user-friendly notifications.

### Security Architecture
- **Comprehensive Security Middleware**: OWASP Top 10 protection.
- **Data Encryption**: AES-256 encryption for sensitive data at rest.
- **TLS 1.3+**: Enforced HTTPS with security headers.
- **Input Validation**: SQL injection, XSS, and CSRF protection.
- **Rate Limiting**: Multi-tier rate limiting.
- **Audit Logging**: Security event logging.

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework (with SQLAlchemy, Login, Limiter, Talisman extensions).
- **OpenAI API**: GPT-based conversation generation and analysis.
- **PostgreSQL**: Primary database.
- **JWT**: Token-based authentication.

### Machine Learning Libraries
- **scikit-learn**: TF-IDF vectorization, cosine similarity, clustering.
- **TextBlob**: Sentiment analysis.
- **NLTK**: Natural language processing toolkit.
- **NumPy**: Numerical computing.

### Voice Processing Services
- **Web Speech API**: Browser-based speech recognition and synthesis.
- **Speech Recognition Library**: Audio processing and transcription.

### Security and Monitoring
- **Flask-Talisman**: Security headers and HTTPS enforcement.
- **Werkzeug**: Security utilities and password hashing.
- **PyOTP**: Two-factor authentication.
- **Cryptography**: AES encryption.

### Development and Utilities
- **Bootstrap 5**: Frontend framework.
- **Font Awesome**: Icon library.
- **JavaScript ES6+**: Modern frontend functionality.
- **Service Workers**: Background processing.

### Cloud and Hosting
- **Replit**: Development and hosting platform.
- **OAuth Providers**: Authentication services.

### External Service Integrations
- **GitHub Integration**: Repository management (listing, creation, updates, branch management, issue tracking, file operations, commit history).