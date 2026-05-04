"""
Authentication Middleware for Student Performance App
Integrates with Clerk.com for secure authentication
"""

import os
import requests
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta

# Try to import jwt, but make it optional for basic functionality
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("Warning: PyJWT not installed. Some advanced features may not work.")
    print("Install with: pip install pyjwt")

class ClerkAuth:
    def __init__(self, app=None, publishable_key=None, secret_key=None):
        self.app = app
        self.publishable_key = publishable_key or os.getenv('CLERK_PUBLISHABLE_KEY')
        self.secret_key = secret_key or os.getenv('CLERK_SECRET_KEY')
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.config.setdefault('CLERK_PUBLISHABLE_KEY', self.publishable_key)
        app.config.setdefault('CLERK_SECRET_KEY', self.secret_key)
        
        # Add authentication middleware
        app.before_request(self.before_request)
        
        # Add authentication routes
        app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        app.add_url_rule('/signup', 'signup', self.signup, methods=['GET', 'POST'])
        app.add_url_rule('/logout', 'logout', self.logout, methods=['POST'])
        app.add_url_rule('/auth/callback', 'auth_callback', self.auth_callback, methods=['GET'])
        app.add_url_rule('/dashboard', 'dashboard', self.dashboard, methods=['GET'])
    
    def before_request(self):
        """Check authentication before each request"""
        # Public routes that don't require authentication
        public_routes = [
            '/login', '/signup', '/auth/callback', '/static',
            '/favicon.ico', '/health'
        ]
        
        if request.path in public_routes or request.path.startswith('/static'):
            return None
        
        # Check if user is authenticated
        if not self.is_authenticated():
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                return redirect(url_for('login'))
        
        # Add user info to request context
        if self.is_authenticated():
            request.user = self.get_current_user()
    
    def is_authenticated(self):
        """Check if current user is authenticated"""
        token = session.get('clerk_token') or request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]  # Remove 'Bearer ' prefix
        
        if not token:
            return False
        
        try:
            # Verify JWT token with Clerk
            payload = self.verify_clerk_token(token)
            return payload is not None
        except:
            return False
    
    def verify_clerk_token(self, token):
        """Verify Clerk JWT token"""
        try:
            # Get Clerk's JWKS
            jwks_url = f"https://clerk.{self.get_clerk_domain()}/.well-known/jwks.json"
            jwks_response = requests.get(jwks_url)
            jwks = jwks_response.json()
            
            # Decode JWT token
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=self.publishable_key,
                issuer=f"https://clerk.{self.get_clerk_domain()}"
            )
            
            return payload
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def get_clerk_domain(self):
        """Get Clerk domain from publishable key"""
        if self.publishable_key:
            # Extract domain from publishable key (pk_live_ or pk_test_)
            key_parts = self.publishable_key.split('_')
            if len(key_parts) >= 2:
                instance_id = key_parts[2]
                return f"{instance_id}.clerk.accounts.dev"
        return "clerk.accounts.dev"
    
    def get_current_user(self):
        """Get current authenticated user"""
        token = session.get('clerk_token')
        if token:
            payload = self.verify_clerk_token(token)
            if payload:
                return {
                    'id': payload.get('sub'),
                    'email': payload.get('email'),
                    'name': payload.get('name'),
                    'picture': payload.get('picture'),
                    'metadata': payload.get('public_metadata', {})
                }
        return None
    
    def login(self):
        """Login route"""
        if request.method == 'GET':
            return self.render_template('login.html')
        return redirect('/')
    
    def signup(self):
        """Signup route"""
        if request.method == 'GET':
            return self.render_template('signup.html')
        return redirect('/')
    
    def logout(self):
        """Logout route"""
        session.clear()
        return redirect(url_for('login'))
    
    def auth_callback(self):
        """Handle OAuth callback"""
        # Handle Clerk OAuth callback
        token = request.args.get('token')
        if token:
            session['clerk_token'] = token
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    def dashboard(self):
        """User dashboard"""
        user = self.get_current_user()
        if not user:
            return redirect(url_for('login'))
        
        return self.render_template('dashboard.html', user=user)
    
    def render_template(self, template_name, **kwargs):
        """Render template with authentication context"""
        from flask import render_template
        
        # Add authentication context
        kwargs['is_authenticated'] = self.is_authenticated()
        kwargs['current_user'] = self.get_current_user()
        
        return render_template(template_name, **kwargs)

# Decorator for protecting routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        token = session.get('clerk_token') or request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                return redirect(url_for('login'))
        
        try:
            # Verify token
            auth = ClerkAuth()
            payload = auth.verify_clerk_token(token)
            if not payload:
                if request.is_json:
                    return jsonify({'error': 'Invalid token'}), 401
                else:
                    return redirect(url_for('login'))
            
            # Add user to request context
            request.user = {
                'id': payload.get('sub'),
                'email': payload.get('email'),
                'name': payload.get('name'),
                'metadata': payload.get('public_metadata', {})
            }
            
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Authentication error: {e}")
            if request.is_json:
                return jsonify({'error': 'Authentication failed'}), 401
            else:
                return redirect(url_for('login'))
    
    return decorated_function

# Session management utilities
class SessionManager:
    @staticmethod
    def create_session(user_data):
        """Create user session"""
        session.update({
            'user_id': user_data.get('id'),
            'user_email': user_data.get('email'),
            'user_name': user_data.get('name'),
            'user_role': user_data.get('metadata', {}).get('role', 'student'),
            'login_time': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def update_last_activity():
        """Update last activity timestamp"""
        session['last_activity'] = datetime.utcnow().isoformat()
    
    @staticmethod
    def is_session_valid():
        """Check if session is still valid"""
        if 'login_time' not in session:
            return False
        
        login_time = datetime.fromisoformat(session['login_time'])
        last_activity = datetime.fromisoformat(session.get('last_activity', session['login_time']))
        
        # Session expires after 24 hours of inactivity
        if datetime.utcnow() - last_activity > timedelta(hours=24):
            return False
        
        return True
    
    @staticmethod
    def destroy_session():
        """Destroy user session"""
        session.clear()

# Role-based access control
def role_required(*allowed_roles):
    """Decorator for role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not SessionManager.is_session_valid():
                return redirect(url_for('login'))
            
            user_role = session.get('user_role', 'student')
            if user_role not in allowed_roles:
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                else:
                    return render_template('unauthorized.html'), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API authentication helper
def api_auth_required(f):
    """Decorator for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401
        
        token = token[7:]  # Remove 'Bearer ' prefix
        
        try:
            auth = ClerkAuth()
            payload = auth.verify_clerk_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            request.user = {
                'id': payload.get('sub'),
                'email': payload.get('email'),
                'metadata': payload.get('public_metadata', {})
            }
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function
