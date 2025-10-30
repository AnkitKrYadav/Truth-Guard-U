"""
Security utilities for TruthGuard
- Password hashing with bcrypt
- Input sanitization
- SQL injection prevention
- Rate limiting
- JWT token generation
"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Password security
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    import hashlib

# JWT tokens (optional, for future auth)
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


# ============ Password Hashing ============
def hash_password(password: str) -> str:
    """Hash password using bcrypt (or fallback to SHA-256 if bcrypt unavailable)."""
    if BCRYPT_AVAILABLE:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    else:
        # Fallback: SHA-256 with salt (less secure, but better than plaintext)
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    if BCRYPT_AVAILABLE:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    else:
        # Fallback verification
        try:
            salt, stored_hash = hashed.split('$')
            computed = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed == stored_hash
        except Exception:
            return False


# ============ Input Sanitization ============
def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    if not text:
        return ""
    
    # Truncate to max length
    text = str(text)[:max_length]
    
    # Remove dangerous characters/patterns
    text = re.sub(r'[<>"\']', '', text)  # Remove HTML/script chars
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)  # Remove event handlers
    
    return text.strip()


def sanitize_email(email: str) -> str:
    """Validate and sanitize email address."""
    email = str(email).strip().lower()
    # Basic email pattern
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return ""
    return email[:100]


def sanitize_username(username: str) -> str:
    """Sanitize username (alphanumeric, underscore, hyphen only)."""
    username = str(username).strip()
    # Allow only safe characters
    username = re.sub(r'[^a-zA-Z0-9_-]', '', username)
    return username[:50]


def sanitize_url(url: str) -> str:
    """Sanitize URL to prevent injection."""
    url = str(url).strip()
    # Only allow http/https schemes
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return ""
    # Remove dangerous patterns
    url = re.sub(r'javascript:', '', url, flags=re.IGNORECASE)
    return url[:2000]


# ============ SQL Injection Prevention ============
def escape_sql_like(pattern: str) -> str:
    """Escape special characters in LIKE patterns."""
    pattern = str(pattern)
    pattern = pattern.replace('\\', '\\\\')
    pattern = pattern.replace('%', '\\%')
    pattern = pattern.replace('_', '\\_')
    return pattern


# ============ Rate Limiting ============
class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}  # {key: [timestamp1, timestamp2, ...]}
    
    def is_allowed(self, key: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check if request is allowed within rate limit."""
        now = datetime.now().timestamp()
        
        # Clean old entries
        if key in self.requests:
            self.requests[key] = [ts for ts in self.requests[key] 
                                 if now - ts < window_seconds]
        else:
            self.requests[key] = []
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """Remove entries older than max_age_seconds."""
        now = datetime.now().timestamp()
        for key in list(self.requests.keys()):
            self.requests[key] = [ts for ts in self.requests[key] 
                                 if now - ts < max_age_seconds]
            if not self.requests[key]:
                del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Decorator to apply rate limiting to Flask routes."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Use IP address as key
            key = request.remote_addr or 'unknown'
            
            if not rate_limiter.is_allowed(key, max_requests, window_seconds):
                return jsonify({
                    "error": "Rate limit exceeded. Please try again later."
                }), 429
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ============ JWT Token Management (Optional) ============
SECRET_KEY = secrets.token_hex(32)  # Generate on startup

def generate_token(user_id: str, username: str, role: str = "user", expires_in_hours: int = 24) -> str:
    """Generate JWT token for user session."""
    if not JWT_AVAILABLE:
        # Fallback: simple token
        return secrets.token_urlsafe(32)
    
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    if not JWT_AVAILABLE:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        user = verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Add user info to request context
        request.user = user
        return f(*args, **kwargs)
    return wrapper


def require_role(role: str):
    """Decorator to require specific role for routes."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({"error": "Authentication required"}), 401
            
            user = verify_token(token)
            if not user:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            if user.get('role') != role and user.get('role') != 'admin':
                return jsonify({"error": "Insufficient permissions"}), 403
            
            request.user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ============ Security Headers ============
def add_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # CSP for production
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


# ============ Session Security ============
def generate_csrf_token() -> str:
    """Generate CSRF token for form protection."""
    return secrets.token_hex(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """Verify CSRF token."""
    return secrets.compare_digest(token, stored_token)
