"""Utility functions for Flask app."""

import hashlib
import secrets
from functools import wraps
from flask import request, jsonify

def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify a password against its hash."""
    return hash_password(password) == hashed

def require_api_key(f):
    """Decorator to require API key for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # In a real app, validate against database
        if api_key != 'test-api-key':
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def paginate(query, page=1, per_page=20):
    """Paginate a SQLAlchemy query."""
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }

class ValidationError(Exception):
    """Custom validation error."""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_email(email):
    """Basic email validation."""
    if '@' not in email or '.' not in email:
        raise ValidationError('Invalid email format', 'email')
    return True

def validate_username(username):
    """Validate username."""
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters', 'username')
    if not username.isalnum():
        raise ValidationError('Username must be alphanumeric', 'username')
    return True