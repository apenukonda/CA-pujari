"""
Security utilities for authentication and authorization
Handles token verification, password hashing, and security helpers
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import string
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityError(Exception):
    """Base exception for security-related errors"""
    pass


class TokenError(SecurityError):
    """Raised when token operations fail"""
    pass


class PasswordError(SecurityError):
    """Raised when password operations fail"""
    pass


class TokenData:
    """Data class for token payload"""
    def __init__(self, uid: str, email: str = None, role: str = "user", **kwargs):
        self.uid = uid
        self.email = email
        self.role = role
        self.exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.iat = datetime.utcnow()
        self.type = "access"
        
        # Add any additional claims
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token data to dictionary"""
        return {
            "uid": self.uid,
            "email": self.email,
            "role": self.role,
            "exp": self.exp,
            "iat": self.iat,
            "type": self.type
        }


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
        
    Raises:
        PasswordError: If hashing fails
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise PasswordError(f"Failed to hash password: {e}")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Token payload data
        expires_delta: Custom expiration time
        
    Returns:
        str: JWT token
        
    Raises:
        TokenError: If token creation fails
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise TokenError(f"Failed to create token: {e}")


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        TokenError: If token verification fails
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        uid: str = payload.get("uid")
        email: str = payload.get("email")
        role: str = payload.get("role", "user")
        
        if uid is None:
            raise TokenError("Invalid token: missing uid")
        
        return TokenData(uid=uid, email=email, role=role)
        
    except JWTError as e:
        logger.error(f"Token verification error: {e}")
        raise TokenError(f"Invalid token: {e}")


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: Token length in bytes
        
    Returns:
        str: Random token
    """
    return secrets.token_urlsafe(length)


def generate_password(length: int = 12) -> str:
    """
    Generate a secure random password
    
    Args:
        length: Password length
        
    Returns:
        str: Random password
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def validate_password_strength(password: str) -> Dict[str, bool]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dict[str, bool]: Validation results
    """
    validation = {
        "length_ok": len(password) >= 8,
        "has_uppercase": any(c.isupper() for c in password),
        "has_lowercase": any(c.islower() for c in password),
        "has_digit": any(c.isdigit() for c in password),
        "has_special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    }
    
    validation["is_strong"] = all(validation.values())
    return validation


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # Basic sanitization - remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '%', ';', '(', ')', '+', '=']
    
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()


def validate_email_format(email: str) -> bool:
    """
    Basic email format validation
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_session_id() -> str:
    """
    Create a secure session ID
    
    Returns:
        str: Session ID
    """
    return generate_secure_token(24)


def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data (like API keys, tokens, etc.)
    
    Args:
        data: Data to hash
        
    Returns:
        str: SHA-256 hash
    """
    import hashlib
    
    return hashlib.sha256(data.encode()).hexdigest()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature (HMAC-SHA256)
    
    Args:
        payload: Request payload
        signature: Provided signature
        secret: Webhook secret
        
    Returns:
        bool: True if signature is valid
    """
    import hmac
    import hashlib
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(f"sha256={expected_signature}", signature)


def rate_limit_key(user_id: str, endpoint: str) -> str:
    """
    Generate a rate limiting key
    
    Args:
        user_id: User ID
        endpoint: API endpoint
        
    Returns:
        str: Rate limit key
    """
    return f"rate_limit:{user_id}:{endpoint}"


def is_admin_user(token_data: TokenData) -> bool:
    """Check if user has admin role"""
    return token_data.role == "admin"


def is_valid_user_role(role: str) -> bool:
    """Check if user role is valid"""
    valid_roles = ["user", "admin", "moderator"]
    return role in valid_roles


class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers dictionary"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


def add_security_middleware_headers(response_headers: Dict[str, str]) -> None:
    """
    Add security headers to response
    
    Args:
        response_headers: Response headers dictionary to modify
    """
    headers = SecurityHeaders.get_security_headers()
    response_headers.update(headers)