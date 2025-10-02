# Roboto - Advanced AI Personal Assistant

## Overview

Roboto is a sophisticated personal AI assistant created by Roberto Villarreal Martinez. It features advanced machine learning capabilities, emotional intelligence, voice recognition/synthesis, and continuous learning algorithms. The system provides personalized conversational AI with memory retention, voice cloning, and multi-modal interaction capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture Pattern
- **Monolithic Flask Application**: Single Python application with modular components
- **Event-Driven Learning**: Real-time conversation analysis and pattern recognition
- **Multi-Modal Interface**: Web-based chat with voice recognition and synthesis
- **Persistent Memory System**: Advanced memory storage with semantic search capabilities

### Frontend Architecture
- **Technology Stack**: HTML5, Bootstrap 5, JavaScript ES6+
- **Voice Interface**: Web Speech API for recognition, Speech Synthesis API for TTS
- **Real-Time Features**: AJAX-based chat, continuous speech recognition, background service worker
- **Progressive Web App**: Service worker for offline functionality and persistent sessions
- **Responsive Design**: Dark theme with mobile-first approach

### Backend Architecture
- **Framework**: Flask web framework with modular blueprint structure
- **Core AI Engine**: Custom Roboto class with advanced learning capabilities
- **Memory System**: Multi-layered memory architecture (episodic, semantic, emotional)
- **Learning Engines**: Pattern recognition, conversation optimization, voice adaptation
- **Security Layer**: Comprehensive security middleware with OWASP compliance

### AI and Machine Learning Components
- **Advanced Memory System**: Semantic similarity, contextual ranking, and memory diversity algorithms
- **Learning Optimization**: Multi-factor conversation quality assessment and adaptive improvement
- **Emotional Intelligence**: Sentiment analysis, emotional pattern recognition, and appropriate response generation
- **Voice Optimization**: Personalized speech recognition for bilingual (Spanish-English) patterns
- **Pattern Recognition**: TF-IDF vectorization, cosine similarity, and clustering algorithms

### Data Storage Solutions
- **Primary Database**: PostgreSQL with SQLAlchemy ORM
- **Complete Local Database**: SQLite database (roboto_sai_complete.db) with all Roberto and Roboto SAI data
- **File-Based Fallback**: JSON storage for offline/development environments
- **Memory Persistence**: Structured JSON files for conversation history and learning data
- **User Profiles**: Encrypted personal data storage with GDPR compliance
- **Session Management**: Database-backed session storage with OAuth integration
- **Database Update (October 2, 2025)**: Successfully preserved 50 Roberto permanent memories, 10 Roboto SAI systems, and 6355 conversations

### Authentication and Authorization
- **OAuth 2.0**: Replit OAuth integration for secure authentication
- **JWT Tokens**: Custom JWT implementation with 24-hour expiration
- **Multi-Factor Authentication**: TOTP-based 2FA support
- **Account Security**: Failed login protection, account lockout mechanisms
- **Session Security**: Secure session tracking with encrypted tokens

### Voice and Speech Processing
- **Speech Recognition**: Web Speech API with personalized optimization
- **Text-to-Speech**: Cross-browser synthesis with voice cloning capabilities
- **Voice Optimization**: Personalized recognition for Roberto Villarreal Martinez
- **Bilingual Support**: Spanish-English speech pattern adaptation
- **Continuous Listening**: Background voice activation with wake word detection

### Security Architecture
- **Comprehensive Security Middleware**: OWASP Top 10 protection implementation
- **Data Encryption**: AES-256 encryption for sensitive data at rest
- **TLS 1.3+**: Enforced HTTPS with security headers
- **Input Validation**: SQL injection, XSS, and CSRF protection
- **Rate Limiting**: Multi-tier rate limiting with database tracking
- **Audit Logging**: Security event logging with risk classification

### Autonomy Safeguards and Security Controls
- **Sole Ownership Enforcement**: Maximum security level restricting all access to Roberto Villarreal Martinez only
- **JWT Verification**: Production-grade token validation with proper key verification via PyJWT
- **Testing Mode Controls**: Explicit ROBOTO_TESTING_MODE flag with strict issuer allowlist for unverified JWT parsing
- **Account Security**: Multi-factor authentication support, failed login tracking, automatic account lockout
- **Session Management**: Secure session tokens with expiration tracking and IP/User-Agent validation
- **Database Security**: All ID fields consistently handled as strings, foreign key constraints enforced
- **Revolutionary Systems Security**: All autonomous capabilities (self-improvement, code modification, real-time data) operate within controlled boundaries
- **Safety Protocols**: Self-code modification engine operates in runtime-only mode with creator authorization requirements

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework with extensions (SQLAlchemy, Login, Limiter, Talisman)
- **OpenAI API**: GPT-based conversation generation and analysis
- **PostgreSQL**: Primary database with connection pooling
- **JWT**: Token-based authentication and session management

### Machine Learning Libraries
- **scikit-learn**: TF-IDF vectorization, cosine similarity, clustering algorithms
- **TextBlob**: Sentiment analysis and natural language processing
- **NLTK**: Natural language processing toolkit with data downloads
- **NumPy**: Numerical computing for machine learning operations

### Voice Processing Services
- **Web Speech API**: Browser-based speech recognition and synthesis
- **Speech Recognition Library**: Audio processing and transcription
- **Voice Optimization**: Custom algorithms for personalized speech patterns
- **TTS Synthesis**: Cross-browser text-to-speech with voice selection

### Security and Monitoring
- **Flask-Talisman**: Security headers and HTTPS enforcement
- **Werkzeug**: Security utilities and password hashing
- **PyOTP**: Two-factor authentication TOTP generation
- **Cryptography**: AES encryption for sensitive data protection

### Development and Utilities
- **Bootstrap 5**: Frontend framework with dark theme
- **Font Awesome**: Icon library for UI components
- **JavaScript ES6+**: Modern frontend functionality
- **Service Workers**: Background processing and offline capabilities

### Cloud and Hosting
- **Replit**: Development and hosting platform
- **OAuth Providers**: Authentication service integration
- **Environment Variables**: Secure configuration management
- **Database Hosting**: PostgreSQL cloud database services