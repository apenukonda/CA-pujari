"""
Authentication and authorization dependencies for FastAPI
Handles Firebase token verification and user authentication
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from app.core.firebase import verify_firebase_token, get_user_by_uid
from app.core.security import TokenData
from app.constants.roles import UserRole
from app.constants.statuses import UserStatus
from app.core.logging import get_logger

logger = get_logger("auth")

# HTTP Bearer scheme for token extraction
security = HTTPBearer(auto_error=False)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class AuthorizationError(Exception):
    """Raised when authorization fails"""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when token has expired"""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid"""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found"""
    pass


class UserInactiveError(AuthenticationError):
    """Raised when user account is inactive"""
    pass


class UserDisabledError(AuthenticationError):
    """Raised when user account is disabled"""
    pass


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from Firebase token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        AuthenticationError: If authentication fails
    """
    if not credentials:
        raise AuthenticationError("No authentication credentials provided")
    
    try:
        # Verify Firebase token
        token_data = verify_firebase_token(credentials.credentials)
        
        # Extract user information
        uid = token_data.get("uid")
        email = token_data.get("email")
        role = token_data.get("role", "user")
        email_verified = token_data.get("email_verified", False)
        
        if not uid:
            raise InvalidTokenError("Token missing user ID")
        
        # Get user record from Firebase Auth
        user_record = get_user_by_uid(uid)
        
        # Build user dictionary
        user = {
            "uid": uid,
            "email": email,
            "role": role,
            "email_verified": email_verified,
            "disabled": user_record.disabled,
            "tokens_valid_after": user_record.tokens_valid_after_timestamp,
            "firebase_user": user_record
        }
        
        logger.info(f"User authenticated: {uid}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise AuthenticationError(f"Authentication failed: {str(e)}")


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current active user (not disabled)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict containing active user information
        
    Raises:
        AuthenticationError: If user is inactive or disabled
    """
    if current_user.get("disabled"):
        raise UserDisabledError("User account is disabled")
    
    # Check if user is inactive (this would be stored in Firestore)
    # For now, we assume users are active unless disabled in Firebase
    
    return current_user


async def get_current_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current verified user (email verified)
    
    Args:
        current_user: Current active user
        
    Returns:
        Dict containing verified user information
        
    Raises:
        AuthenticationError: If user email is not verified
    """
    if not current_user.get("email_verified"):
        raise AuthenticationError("User email is not verified")
    
    return current_user


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current admin user
    
    Args:
        current_user: Current active user
        
    Returns:
        Dict containing admin user information
        
    Raises:
        AuthorizationError: If user is not admin
    """
    role = current_user.get("role")
    if role != "admin":
        logger.warning(f"Admin access denied for user {current_user['uid']}")
        raise AuthorizationError("Admin access required")
    
    return current_user


async def get_current_user_with_permissions(
    required_permissions: list,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current user with specific permissions
    
    Args:
        required_permissions: List of required permissions
        current_user: Current active user
        
    Returns:
        Dict containing user information
        
    Raises:
        AuthorizationError: If user lacks required permissions
    """
    # Check if user has required permissions
    # This would be implemented based on your permission system
    user_role = current_user.get("role")
    
    if user_role == "admin":
        # Admin has all permissions
        return current_user
    
    # For regular users, check specific permissions
    # This is a simplified implementation
    if "user" in required_permissions and user_role == "user":
        return current_user
    
    logger.warning(f"Permission denied for user {current_user['uid']}")
    raise AuthorizationError("Insufficient permissions")


def require_auth(required: bool = True):
    """
    Decorator dependency to require authentication
    
    Args:
        required: Whether authentication is required
        
    Returns:
        Dependency function
    """
    async def auth_dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Dict[str, Any]]:
        if not required:
            return None
        
        if not credentials:
            raise AuthenticationError("Authentication required")
        
        try:
            return await get_current_user(credentials)
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    return auth_dependency


def require_role(required_role: str):
    """
    Decorator dependency to require specific role
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function
    """
    async def role_dependency(
        current_user: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")
        
        if user_role != required_role:
            raise AuthorizationError(f"{required_role.capitalize()} role required")
        
        return current_user
    
    return role_dependency


def require_admin():
    """Dependency to require admin role"""
    return require_role("admin")


async def optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Dict containing user information or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except Exception as e:
        logger.debug(f"Optional authentication failed: {e}")
        return None


def create_user_claims(user_id: str, role: str = "user", **kwargs) -> Dict[str, Any]:
    """
    Create custom claims for user
    
    Args:
        user_id: User ID
        role: User role
        **kwargs: Additional claims
        
    Returns:
        Dict containing user claims
    """
    claims = {
        "uid": user_id,
        "role": role,
        "permissions": get_permissions_for_role(role),
        **kwargs
    }
    return claims


def get_permissions_for_role(role: str) -> list:
    """
    Get permissions for a specific role
    
    Args:
        role: User role
        
    Returns:
        List of permissions
    """
    # This would be integrated with your permission system
    role_permissions = {
        "user": ["view_own_profile", "view_courses", "view_webinars"],
        "admin": ["*"]  # Admin has all permissions
    }
    
    return role_permissions.get(role, [])


class AuthenticatedRequest:
    """Wrapper for authenticated requests"""
    
    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.uid = user.get("uid")
        self.role = user.get("role")
        self.email = user.get("email")
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.is_admin():
            return True
        
        # Check specific permissions
        user_permissions = self.user.get("permissions", [])
        return permission in user_permissions
    
    def can_access_resource(self, resource_owner_id: str) -> bool:
        """Check if user can access resource owned by another user"""
        if self.is_admin():
            return True
        
        return self.uid == resource_owner_id


async def get_authenticated_request(
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(optional_current_user)
) -> AuthenticatedRequest:
    """
    Get authenticated request wrapper
    
    Args:
        request: FastAPI request
        current_user: Current user if authenticated
        
    Returns:
        AuthenticatedRequest wrapper
    """
    return AuthenticatedRequest(current_user) if current_user else None


# Convenience dependencies
get_current_user_optional = optional_current_user
get_current_user_required = get_current_user
get_current_active_user_optional = optional_current_user
get_current_admin_user_optional = optional_current_user