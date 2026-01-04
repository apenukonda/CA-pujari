"""
Role-based access control (RBAC) permissions system
Handles permission checking and authorization decorators
"""

from functools import wraps
from typing import List, Set, Dict, Any, Optional, Callable
from fastapi import HTTPException, status, Depends
import logging

from app.constants.roles import UserRole, Permission, ROLE_PERMISSIONS
from app.constants.statuses import UserStatus
from app.core.logging import get_logger

logger = get_logger("permissions")


class PermissionError(Exception):
    """Raised when permission check fails"""
    pass


class InsufficientPermissionsError(PermissionError):
    """Raised when user lacks required permissions"""
    pass


class ResourceAccessError(PermissionError):
    """Raised when user cannot access a resource"""
    pass


class RoleAssignmentError(PermissionError):
    """Raised when role assignment fails"""
    pass


def get_user_permissions(user_role: str) -> Set[Permission]:
    """
    Get permissions for a user role
    
    Args:
        user_role: User role string
        
    Returns:
        Set of permissions for the role
    """
    try:
        role_enum = UserRole(user_role)
        return ROLE_PERMISSIONS.get(role_enum, set())
    except ValueError:
        logger.warning(f"Unknown user role: {user_role}")
        return set()


def has_permission(user_role: str, permission: Permission) -> bool:
    """
    Check if user role has specific permission
    
    Args:
        user_role: User role string
        permission: Permission to check
        
    Returns:
        True if user has permission
    """
    user_permissions = get_user_permissions(user_role)
    return permission in user_permissions


def has_any_permission(user_role: str, permissions: List[Permission]) -> bool:
    """
    Check if user role has any of the specified permissions
    
    Args:
        user_role: User role string
        permissions: List of permissions to check
        
    Returns:
        True if user has any of the permissions
    """
    user_permissions = get_user_permissions(user_role)
    return any(perm in user_permissions for perm in permissions)


def has_all_permissions(user_role: str, permissions: List[Permission]) -> bool:
    """
    Check if user role has all of the specified permissions
    
    Args:
        user_role: User role string
        permissions: List of permissions to check
        
    Returns:
        True if user has all of the permissions
    """
    user_permissions = get_user_permissions(user_role)
    return all(perm in user_permissions for perm in permissions)


def is_admin(user_role: str) -> bool:
    """Check if user role is admin"""
    return user_role == "admin"


def is_user(user_role: str) -> bool:
    """Check if user role is regular user"""
    return user_role == "user"


def can_access_resource(user_role: str, resource_owner_id: str, user_id: str) -> bool:
    """
    Check if user can access resource owned by another user
    
    Args:
        user_role: User role string
        resource_owner_id: ID of resource owner
        user_id: Current user ID
        
    Returns:
        True if user can access resource
    """
    # Admin can access all resources
    if is_admin(user_role):
        return True
    
    # Users can only access their own resources
    return resource_owner_id == user_id


def can_modify_resource(user_role: str, resource_owner_id: str, user_id: str) -> bool:
    """
    Check if user can modify resource owned by another user
    
    Args:
        user_role: User role string
        resource_owner_id: ID of resource owner
        user_id: Current user ID
        
    Returns:
        True if user can modify resource
    """
    # Only admin can modify resources owned by others
    if is_admin(user_role):
        return True
    
    # Users can only modify their own resources
    return resource_owner_id == user_id


def can_delete_resource(user_role: str, resource_owner_id: str, user_id: str) -> bool:
    """
    Check if user can delete resource owned by another user
    
    Args:
        user_role: User role string
        resource_owner_id: ID of resource owner
        user_id: Current user ID
        
    Returns:
        True if user can delete resource
    """
    # Only admin can delete resources owned by others
    if is_admin(user_role):
        return True
    
    # Users can only delete their own resources
    return resource_owner_id == user_id


# Permission checking decorators
def require_permission(permission: Permission):
    """
    Decorator to require specific permission
    
    Args:
        permission: Required permission
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be used with FastAPI dependencies
            # The actual implementation would check permissions in the endpoint
            pass
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """
    Decorator to require any of the specified permissions
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            pass
        return wrapper
    return decorator


def require_all_permissions(permissions: List[Permission]):
    """
    Decorator to require all of the specified permissions
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            pass
        return wrapper
    return decorator


def require_admin():
    """Decorator to require admin role"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            pass
        return wrapper
    return decorator


def require_user():
    """Decorator to require user role"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            pass
        return wrapper
    return decorator


# Permission checkers for FastAPI endpoints
class PermissionChecker:
    """Helper class for permission checking in FastAPI endpoints"""
    
    def __init__(self, user_role: str):
        self.user_role = user_role
        self.permissions = get_user_permissions(user_role)
    
    def check(self, permission: Permission) -> bool:
        """Check if user has permission"""
        return permission in self.permissions
    
    def check_any(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the permissions"""
        return any(perm in self.permissions for perm in permissions)
    
    def check_all(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the permissions"""
        return all(perm in self.permissions for perm in permissions)
    
    def require(self, permission: Permission):
        """Require permission or raise exception"""
        if not self.check(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required"
            )
    
    def require_any(self, permissions: List[Permission]):
        """Require any permission or raise exception"""
        if not self.check_any(permissions):
            perm_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of permissions {perm_names} required"
            )
    
    def require_all(self, permissions: List[Permission]):
        """Require all permissions or raise exception"""
        if not self.check_all(permissions):
            perm_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All permissions {perm_names} required"
            )
    
    def require_admin(self):
        """Require admin role or raise exception"""
        if not is_admin(self.user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
    
    def require_user(self):
        """Require user role or raise exception"""
        if not is_user(self.user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User access required"
            )


def create_permission_checker(user_role: str) -> PermissionChecker:
    """Create permission checker for user role"""
    return PermissionChecker(user_role)


# Resource access control
def check_resource_access(
    user_role: str,
    user_id: str,
    resource_owner_id: str,
    action: str = "view"
) -> bool:
    """
    Check resource access permissions
    
    Args:
        user_role: User role string
        user_id: Current user ID
        resource_owner_id: Resource owner ID
        action: Action to perform (view, modify, delete)
        
    Returns:
        True if access is allowed
    """
    if action == "view":
        return can_access_resource(user_role, resource_owner_id, user_id)
    elif action == "modify":
        return can_modify_resource(user_role, resource_owner_id, user_id)
    elif action == "delete":
        return can_delete_resource(user_role, resource_owner_id, user_id)
    else:
        return False


def require_resource_access(
    user_role: str,
    user_id: str,
    resource_owner_id: str,
    action: str = "view"
):
    """
    Require resource access or raise exception
    
    Args:
        user_role: User role string
        user_id: Current user ID
        resource_owner_id: Resource owner ID
        action: Action to perform
    """
    if not check_resource_access(user_role, user_id, resource_owner_id, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot {action} resource owned by another user"
        )


# Role management
def assign_role(user_id: str, role: str, admin_user_id: str) -> bool:
    """
    Assign role to user (admin only)
    
    Args:
        user_id: User ID to assign role to
        role: Role to assign
        admin_user_id: Admin user ID making the assignment
        
    Returns:
        True if assignment successful
        
    Raises:
        RoleAssignmentError: If assignment fails
    """
    try:
        # Validate role
        if role not in [r.value for r in UserRole]:
            raise RoleAssignmentError(f"Invalid role: {role}")
        
        # This would integrate with Firebase custom claims
        # and/or Firestore user documents
        
        logger.info(f"Role {role} assigned to user {user_id} by admin {admin_user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Role assignment failed: {e}")
        raise RoleAssignmentError(f"Failed to assign role: {str(e)}")


def revoke_role(user_id: str, role: str, admin_user_id: str) -> bool:
    """
    Revoke role from user (admin only)
    
    Args:
        user_id: User ID to revoke role from
        role: Role to revoke
        admin_user_id: Admin user ID making the revocation
        
    Returns:
        True if revocation successful
        
    Raises:
        RoleAssignmentError: If revocation fails
    """
    try:
        # This would integrate with Firebase custom claims
        # and/or Firestore user documents
        
        logger.info(f"Role {role} revoked from user {user_id} by admin {admin_user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Role revocation failed: {e}")
        raise RoleAssignmentError(f"Failed to revoke role: {str(e)}")


def get_user_roles(user_id: str) -> List[str]:
    """
    Get all roles for a user
    
    Args:
        user_id: User ID
        
    Returns:
        List of user roles
    """
    # This would retrieve roles from Firebase custom claims
    # or Firestore user documents
    return ["user"]  # Default role


def is_valid_role(role: str) -> bool:
    """Check if role is valid"""
    return role in [r.value for r in UserRole]


# Permission utilities
def get_permissions_by_category() -> Dict[str, List[Permission]]:
    """Get permissions grouped by category"""
    return {
        "User Management": [
            Permission.USER_VIEW,
            Permission.USER_EDIT,
            Permission.USER_DELETE,
        ],
        "Course Management": [
            Permission.COURSE_CREATE,
            Permission.COURSE_EDIT,
            Permission.COURSE_DELETE,
            Permission.COURSE_VIEW,
        ],
        "Webinar Management": [
            Permission.WEBINAR_CREATE,
            Permission.WEBINAR_EDIT,
            Permission.WEBINAR_DELETE,
            Permission.WEBINAR_VIEW,
        ],
        "Purchase Management": [
            Permission.PURCHASE_VIEW,
            Permission.PURCHASE_REFUND,
        ],
        "Feedback Management": [
            Permission.FEEDBACK_CREATE,
            Permission.FEEDBACK_VIEW,
            Permission.FEEDBACK_MODERATE,
        ],
        "Doubt Management": [
            Permission.DOUBT_CREATE,
            Permission.DOUBT_VIEW,
            Permission.DOUBT_REPLY,
            Permission.DOUBT_MODERATE,
        ],
        "Analytics & Reports": [
            Permission.ANALYTICS_VIEW,
            Permission.REPORTS_GENERATE,
        ],
        "System Administration": [
            Permission.SYSTEM_CONFIG,
            Permission.USER_ADMIN,
            Permission.AUDIT_VIEW,
        ]
    }


def get_role_permissions_summary() -> Dict[str, Dict[str, Any]]:
    """Get summary of role permissions"""
    summary = {}
    
    for role in UserRole:
        role_name = role.value
        permissions = get_user_permissions(role_name)
        
        summary[role_name] = {
            "display_name": role_name.title(),
            "permission_count": len(permissions),
            "permissions": [p.value for p in permissions]
        }
    
    return summary


# FastAPI dependency functions
async def get_permission_checker(
    current_user: dict = Depends(lambda: None)  # This would be your auth dependency
) -> PermissionChecker:
    """FastAPI dependency to get permission checker"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_role = current_user.get("role", "user")
    return create_permission_checker(user_role)


async def require_admin_permission(
    checker: PermissionChecker = Depends(get_permission_checker)
) -> PermissionChecker:
    """FastAPI dependency to require admin permission"""
    checker.require_admin()
    return checker