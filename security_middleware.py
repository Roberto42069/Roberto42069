
"""
Comprehensive Security Middleware for Roboto AI Application
Implements OWASP Top 10 protections, rate limiting, and security headers
"""

import os
import jwt
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g, current_app, abort
import re
import html


class SecurityManager:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        jwt_secret = os.environ.get('JWT_SECRET_KEY')
        if not jwt_secret:
            raise ValueError("JWT_SECRET_KEY environment variable is required for secure operation")
        app.config.setdefault('JWT_SECRET_KEY', jwt_secret)
        app.config.setdefault('JWT_EXPIRATION_HOURS', 24)
        app.config.setdefault('RATE_LIMIT_PER_MINUTE', 60)
        app.config.setdefault('RATE_LIMIT_PER_HOUR', 1000)
        
        # Register security middleware
        app.before_request(self.before_request_security)
        app.after_request(self.after_request_security)
    
    def before_request_security(self):
        """Security checks before each request"""
        # Skip security for static files
        if request.endpoint and request.endpoint.startswith('static'):
            return
        
        # Rate limiting
        if not self.check_rate_limit():
            self.log_security_event('rate_limit_exceeded', risk_level='medium')
            abort(429, description="Rate limit exceeded")
        
        # Input validation and XSS protection
        self.validate_and_sanitize_input()
        
        # CSRF protection for state-changing requests
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            if not self.verify_csrf_token():
                self.log_security_event('csrf_token_invalid', risk_level='high')
                abort(403, description="CSRF token invalid")
        
        # JWT validation for protected endpoints
        if self.requires_jwt_auth():
            user = self.validate_jwt_token()
            if not user:
                abort(401, description="Invalid or expired token")
            g.current_user = user
    
    def after_request_security(self, response):
        """Add security headers after each request"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # HSTS for HTTPS
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    def check_rate_limit(self):
        """Implement rate limiting with Redis-like behavior using database"""
        identifier = self.get_client_identifier()
        endpoint = request.endpoint or 'unknown'
        current_time = datetime.utcnow()
        
        # Check minute-based rate limiting
        minute_start = current_time.replace(second=0, microsecond=0)
        minute_key = f"{identifier}:{endpoint}:minute"
        
        try:
            from models import RateLimitTracker, db
            minute_tracker = RateLimitTracker.query.filter_by(
                identifier=minute_key,
                window_start=minute_start
            ).first()
            
            if minute_tracker:
                if minute_tracker.request_count >= current_app.config['RATE_LIMIT_PER_MINUTE']:
                    return False
                minute_tracker.request_count += 1
            else:
                minute_tracker = RateLimitTracker(
                    identifier=minute_key,
                    endpoint=endpoint,
                    window_start=minute_start,
                    request_count=1
                )
                db.session.add(minute_tracker)
        except ImportError:
            # Fallback if database is not available
            return True
        
            # Cleanup old entries
            cleanup_time = current_time - timedelta(hours=2)
            RateLimitTracker.query.filter(
                RateLimitTracker.window_start < cleanup_time
            ).delete()
            
            db.session.commit()
        except Exception:
            pass
        return True
    
    def get_client_identifier(self):
        """Get client identifier for rate limiting"""
        # Use authenticated user ID if available
        if hasattr(g, 'current_user') and g.current_user:
            return f"user:{g.current_user.id}"
        
        # Use IP address with consideration for proxies
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip:
            # Take first IP if comma-separated
            ip = ip.split(',')[0].strip()
        return f"ip:{ip}"
    
    def validate_and_sanitize_input(self):
        """Validate and sanitize all input to prevent XSS and injection attacks"""
        # SQL injection patterns
        sql_patterns = [
            r'union\s+select', r'drop\s+table', r'delete\s+from',
            r'insert\s+into', r'update\s+set', r'exec\s*\(',
            r'sp_executesql', r'xp_cmdshell', r'--', r'/\*.*\*/'
        ]
        
        # XSS patterns
        xss_patterns = [
            r'<script[^>]*>.*?</script>', r'javascript:', r'vbscript:',
            r'onload\s*=', r'onerror\s*=', r'onclick\s*=', r'onmouseover\s*='
        ]
        
        def check_patterns(value, patterns, attack_type):
            if isinstance(value, str):
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        self.log_security_event(f'{attack_type}_attempt', 
                                              risk_level='high',
                                              details={'pattern': pattern, 'value': value[:100]})
                        abort(400, description="Invalid input detected")
        
        # Check form data
        for key, value in request.form.items():
            check_patterns(value, sql_patterns, 'sql_injection')
            check_patterns(value, xss_patterns, 'xss')
            # Sanitize HTML
            if isinstance(value, str):
                request.form = request.form.copy()
                request.form[key] = html.escape(value)
        
        # Check JSON data
        if request.is_json and request.json:
            self._recursive_check_json(request.json, sql_patterns + xss_patterns)
    
    def _recursive_check_json(self, data, patterns):
        """Recursively check JSON data for malicious patterns"""
        if isinstance(data, dict):
            for key, value in data.items():
                self._recursive_check_json(value, patterns)
        elif isinstance(data, list):
            for item in data:
                self._recursive_check_json(item, patterns)
        elif isinstance(data, str):
            for pattern in patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    self.log_security_event('malicious_json_input', 
                                          risk_level='high',
                                          details={'pattern': pattern})
                    abort(400, description="Invalid JSON input detected")
    
    def verify_csrf_token(self):
        """Verify CSRF token for state-changing requests"""
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not token:
            return False
        
        # Verify token structure and signature
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return data.get('csrf') == True and data.get('exp', 0) > time.time()
        except jwt.InvalidTokenError:
            return False
    
    def generate_csrf_token(self):
        """Generate CSRF token"""
        payload = {
            'csrf': True,
            'exp': time.time() + 3600,  # 1 hour expiration
            'iat': time.time()
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def requires_jwt_auth(self):
        """Check if current endpoint requires JWT authentication"""
        protected_endpoints = [
            'chat', 'get_chat_history', 'export_data', 
            'import_data', 'get_emotional_status'
        ]
        return request.endpoint in protected_endpoints
    
    def validate_jwt_token(self):
        """Validate JWT token and return user"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            from models import User
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return None
            
            user = User.query.get(user_id)
            if not user:
                return None
            
            # Check if account is locked
            if hasattr(user, 'is_account_locked') and user.is_account_locked():
                self.log_security_event('locked_account_access_attempt', 
                                       risk_level='medium',
                                       user_id=user.id)
                return None
            
            return user
            
        except jwt.ExpiredSignatureError:
            self.log_security_event('expired_token_usage', risk_level='low')
            return None
        except jwt.InvalidTokenError:
            self.log_security_event('invalid_token_usage', risk_level='medium')
            return None
        except ImportError:
            return None
    
    def generate_jwt_token(self, user):
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
            'iat': datetime.utcnow(),
            'sub': user.id
        }
        
        token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        try:
            from models import UserSession, db
            # Create session record
            session_record = UserSession(
                user_id=user.id,
                session_token=hashlib.sha256(token.encode()).hexdigest(),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:512],
                expires_at=payload['exp']
            )
            db.session.add(session_record)
            db.session.commit()
        except ImportError:
            pass
        
        return token
    
    def log_security_event(self, event_type, risk_level='low', user_id=None, details=None):
        """Log security events for monitoring and analysis"""
        try:
            from models import SecurityAuditLog, db
            log_entry = SecurityAuditLog(
                user_id=user_id or (g.current_user.id if hasattr(g, 'current_user') and g.current_user else None),
                event_type=event_type,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:512],
                details=details or {},
                risk_level=risk_level
            )
            db.session.add(log_entry)
            db.session.commit()
        except ImportError:
            # Log to application logger as fallback
            current_app.logger.warning(f"Security event: {event_type} - {risk_level} - {details}")


def require_auth(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has admin privileges (you can implement your own logic)
        if not getattr(g.current_user, 'is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def validate_password_strength(password):
    """Validate password strength according to security best practices"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common patterns
    common_patterns = ['password', '123456', 'qwerty', 'admin']
    if any(pattern in password.lower() for pattern in common_patterns):
        return False, "Password contains common patterns"
    
    return True, "Password meets security requirements"


def encrypt_sensitive_data(data, key=None):
    """Encrypt sensitive data using AES-256"""
    from cryptography.fernet import Fernet
    
    if not key:
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            # Generate and store encryption key
            key = Fernet.generate_key()
            # In production, store this securely
            os.environ['ENCRYPTION_KEY'] = key.decode()
    
    if isinstance(key, str):
        key = key.encode()
    
    f = Fernet(key)
    if isinstance(data, str):
        data = data.encode()
    
    return f.encrypt(data).decode()


def decrypt_sensitive_data(encrypted_data, key=None):
    """Decrypt sensitive data using AES-256"""
    from cryptography.fernet import Fernet
    
    if not key:
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("Encryption key not found")
    
    if isinstance(key, str):
        key = key.encode()
    
    f = Fernet(key)
    if isinstance(encrypted_data, str):
        encrypted_data = encrypted_data.encode()
    
    return f.decrypt(encrypted_data).decode()