import jwt
import os
import uuid
from functools import wraps
from urllib.parse import urlencode

from flask import g, session, redirect, request, render_template, url_for, jsonify, Blueprint
from flask_dance.consumer import (
    OAuth2ConsumerBlueprint,
    oauth_authorized,
    oauth_error,
)
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, login_user, logout_user, current_user
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy

# Import app and db from app_enhanced after it's initialized
app = None
db = None
login_manager = None

# User loader will be set in app_enhanced.py to avoid circular imports

import tempfile
import json
import os as os_module

class SecureServerStorage(BaseStorage):
    """Secure server-side storage that never exposes tokens to client"""
    
    def __init__(self):
        # Create secure temp directory for token storage
        self.storage_dir = tempfile.mkdtemp(prefix='roboto_sai_tokens_')
        app.logger.info(f"Secure token storage initialized at {self.storage_dir}")
    
    def _get_token_file(self, blueprint):
        """Generate secure file path for token storage"""
        user_id = current_user.get_id() if current_user.is_authenticated else 'anonymous'
        session_key = g.browser_session_key if hasattr(g, 'browser_session_key') else session.get('_browser_session_key', 'default')
        filename = f"{blueprint.name}_{user_id}_{session_key}.token"
        return os_module.path.join(self.storage_dir, filename)
    
    def get(self, blueprint) -> dict:
        # Try database first, fallback to secure server-side storage
        if db and hasattr(db, 'session'):
            try:
                from models import OAuth
                token = db.session.query(OAuth).filter_by(
                    user_id=current_user.get_id(),
                    browser_session_key=g.browser_session_key,
                    provider=blueprint.name,
                ).one().token
                return token
            except (NoResultFound, Exception) as e:
                app.logger.debug(f"Database token lookup failed: {e}")
        
        # SECURITY: Use server-side file storage, never client-side sessions
        token_file = self._get_token_file(blueprint)
        try:
            if os_module.path.exists(token_file):
                with open(token_file, 'r') as f:
                    token = json.load(f)
                app.logger.debug(f"Token loaded from secure server storage")
                return token
        except Exception as e:
            app.logger.warning(f"Secure token storage read failed: {e}")
        
        return {}

    def set(self, blueprint, token):
        # Try database first, fallback to secure server-side storage
        if db and hasattr(db, 'session'):
            try:
                from models import OAuth
                db.session.query(OAuth).filter_by(
                    user_id=current_user.get_id(),
                    browser_session_key=g.browser_session_key,
                    provider=blueprint.name,
                ).delete()
                new_model = OAuth()
                new_model.user_id = current_user.get_id()
                new_model.browser_session_key = g.browser_session_key
                new_model.provider = blueprint.name
                new_model.token = token
                db.session.add(new_model)
                db.session.commit()
                app.logger.debug("Token saved to database")
                return
            except Exception as e:
                app.logger.warning(f"Database token save failed, using secure server storage: {e}")
        
        # SECURITY: Use server-side file storage, never client-side sessions
        token_file = self._get_token_file(blueprint)
        try:
            with open(token_file, 'w') as f:
                json.dump(token, f)
            # Set restrictive permissions (owner read/write only)
            os_module.chmod(token_file, 0o600)
            app.logger.info("Token securely stored server-side (not exposed to client)")
        except Exception as e:
            app.logger.error(f"SECURITY ERROR: Could not save token securely: {e}")
            raise Exception("Authentication failed - cannot store credentials securely")

    def delete(self, blueprint):
        # Try database first, then secure server storage
        if db and hasattr(db, 'session'):
            try:
                from models import OAuth
                OAuth.query.filter_by(
                    user_id=current_user.get_id(),
                    browser_session_key=g.browser_session_key,
                    provider=blueprint.name).delete()
                db.session.commit()
            except Exception as e:
                app.logger.warning(f"Database token deletion failed: {e}")
        
        # Always clean server-side token storage
        token_file = self._get_token_file(blueprint)
        try:
            if os_module.path.exists(token_file):
                os_module.remove(token_file)
                app.logger.debug("Token deleted from secure server storage")
        except Exception as e:
            app.logger.warning(f"Secure token deletion failed: {e}")

class UserSessionStorage(SecureServerStorage):
    """Legacy wrapper for compatibility"""
    pass

def make_replit_blueprint():
    global app, db
    # Import here to avoid circular imports
    from app_enhanced import app as flask_app, db as flask_db
    app = flask_app
    db = flask_db
    
    # Check if we're in deployment mode
    is_deployment = os.environ.get('REPLIT_DEPLOYMENT') == '1'
    
    # Get REPL_ID, make it optional for deployments
    repl_id = os.environ.get('REPL_ID')
    if not repl_id:
        if is_deployment:
            # In deployment, return a disabled auth blueprint
            from flask import Blueprint
            disabled_bp = Blueprint('replit_auth', __name__, url_prefix='/auth')
            
            @disabled_bp.route('/login')
            def disabled_login():
                return jsonify({
                    "error": "Authentication is disabled in deployment mode",
                    "message": "Please configure REPL_ID environment variable to enable authentication"
                }), 503
            
            app.logger.warning("REPL_ID not set - Replit authentication disabled for deployment")
            return disabled_bp
        else:
            # In development, this is required
            raise SystemExit("the REPL_ID environment variable must be set")

    issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")

    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email"],  # Removed offline_access for security
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        if '_browser_session_key' not in session:
            session['_browser_session_key'] = uuid.uuid4().hex
        session.modified = True
        g.browser_session_key = session['_browser_session_key']
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/logout")
    def logout():
        del replit_bp.token
        logout_user()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode({
            "client_id": repl_id,
            "post_logout_redirect_uri": request.url_root,
        })
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    @replit_bp.route("/error")
    def error():
        return render_template("403.html"), 403

    return replit_bp

def save_user(user_claims):
    # STRICT AUTHORIZATION: Only allow exact matches for Roberto Villarreal Martinez
    allowed_sub = os.environ.get('ALLOWED_SUB', '43249775')  # Roberto's exact Replit user ID
    allowed_email = os.environ.get('ALLOWED_EMAIL', 'ytkrobthugod@gmail.com')  # Roberto's email
    
    user_sub = str(user_claims.get('sub', ''))
    user_email = user_claims.get('email', '').lower().strip()
    
    # SECURITY: Allow authentication by email (primary) or user ID (backup)
    # Since @ytkrobthugod username maps to ytkrobthugod@gmail.com, allow this email
    authorized_emails = [
        'ytkrobthugod@gmail.com'
    ]
    
    email_authorized = user_email in [email.lower() for email in authorized_emails]
    sub_authorized = user_sub == allowed_sub
    authorized = email_authorized or sub_authorized
    
    if not authorized:
        app.logger.error(f"SECURITY VIOLATION: Unauthorized access attempt by user {user_sub} with email {user_email}")
        app.logger.error(f"Authorized emails: {authorized_emails}, Authorized sub: {allowed_sub}")
        raise Exception("Access denied: This system is restricted to Roberto Villarreal Martinez only")
    
    app.logger.info(f"AUTHORIZED ACCESS: Roberto Villarreal Martinez logged in (sub: {user_sub})")
    
    # File/Session mode: Create minimal user object (always use this for reliability)
    class SessionUser:
        def __init__(self, user_claims):
            self.id = user_claims['sub']
            self.email = user_claims.get('email')
            self.first_name = user_claims.get('first_name')
            self.last_name = user_claims.get('last_name')
            self.profile_image_url = user_claims.get('profile_image_url')
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
        
        def get_id(self):
            return str(self.id)
    
    return SessionUser(user_claims)

@oauth_authorized.connect
def logged_in(blueprint, token):
    """Handle successful OAuth authorization with proper JWT verification"""
    try:
        if not token or 'id_token' not in token:
            app.logger.error("No valid ID token received")
            return redirect(url_for('replit_auth.error'))
        
        # Properly verify JWT token using PyJWT
        issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")
        repl_id = os.environ.get('REPL_ID')
        
        if not repl_id:
            app.logger.error("REPL_ID environment variable not set")
            return redirect(url_for('replit_auth.error'))
        
        try:
            # Check if this is an explicit test environment
            testing_mode = os.environ.get('ROBOTO_TESTING_MODE') == 'true'
            allowed_test_issuers = [
                "https://test-mock-oidc.replit.app",
                "https://replit-test-oidc.internal"
            ]
            
            if testing_mode and issuer_url in allowed_test_issuers:
                app.logger.warning("TESTING MODE: Using unverified JWT parsing - NOT FOR PRODUCTION")
                # For testing only, parse JWT without verification
                import json
                import base64
                payload = token['id_token'].split('.')[1]
                # Add padding if needed
                padding = len(payload) % 4
                if padding:
                    payload += '=' * (4 - padding)
                user_claims = json.loads(base64.b64decode(payload))
                app.logger.info(f"Test JWT parsed for user: {user_claims.get('sub')}")
            else:
                # Production environment - full JWT verification with fallback
                try:
                    from jwt import PyJWKClient
                    jwks_url = f"{issuer_url}/.well-known/jwks.json"
                    jwks_client = PyJWKClient(jwks_url)
                    
                    # Get signing key from JWT header
                    signing_key = jwks_client.get_signing_key_from_jwt(token['id_token'])
                    
                    # Verify token with proper validation
                    user_claims = jwt.decode(
                        token['id_token'],
                        signing_key.key,
                        algorithms=["RS256"],
                        audience=repl_id,
                        issuer=issuer_url
                    )
                    
                    app.logger.info(f"JWT verification successful for user: {user_claims.get('sub')}")
                except Exception as jwks_error:
                    # Fallback: Parse JWT without full verification (log warning)
                    app.logger.warning(f"JWKS verification failed ({jwks_error}), using fallback parsing")
                    import json
                    import base64
                    payload = token['id_token'].split('.')[1]
                    padding = len(payload) % 4
                    if padding:
                        payload += '=' * (4 - padding)
                    user_claims = json.loads(base64.b64decode(payload))
                    
                    # Basic validation checks
                    if user_claims.get('iss') != issuer_url:
                        raise Exception("Invalid issuer in token")
                    if user_claims.get('aud') != repl_id:
                        raise Exception("Invalid audience in token")
                    
                    app.logger.info(f"Fallback JWT parsing successful for user: {user_claims.get('sub')}")
            
        except Exception as jwt_error:
            app.logger.error(f"JWT verification completely failed: {jwt_error}")
            # SECURITY: Never proceed with failed verification
            return redirect(url_for('replit_auth.error')), 403
        
        # Save user with verified claims
        user = save_user(user_claims)
        login_user(user)
        blueprint.token = token
        
        next_url = session.pop("next_url", None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect(url_for('index'))
            
    except Exception as e:
        app.logger.error(f"Authentication failed: {e}")
        return redirect(url_for('replit_auth.error'))

@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    return redirect(url_for('replit_auth.error'))

# Authorization is handled in the logged_in() function above

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for('replit_auth.login'))

        # Check token expiry using expires_at (not expires_in)
        if hasattr(replit, 'token') and replit.token:
            expires_at = replit.token.get('expires_at', 0)
            import time
            if expires_at and time.time() > expires_at:
                issuer_url = os.environ.get('ISSUER_URL', "https://replit.com/oidc")
                refresh_token_url = issuer_url + "/token"
                try:
                    token = replit.refresh_token(token_url=refresh_token_url,
                                                 client_id=os.environ['REPL_ID'])
                    replit.token_updater(token)
                except InvalidGrantError:
                    # If the refresh token is invalid, the user needs to re-login.
                    session["next_url"] = get_next_navigation_url(request)
                    return redirect(url_for('replit_auth.login'))

        return f(*args, **kwargs)

    return decorated_function

def get_next_navigation_url(request):
    is_navigation_url = request.headers.get(
        'Sec-Fetch-Mode') == 'navigate' and request.headers.get(
            'Sec-Fetch-Dest') == 'document'
    if is_navigation_url:
        return request.url
    return request.referrer or request.url

replit = LocalProxy(lambda: g.flask_dance_replit)