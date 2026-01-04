"""
User roles and permissions for the E-Learning Platform
Defines role-based access control constants
"""

from enum import Enum
from typing import List, Dict, Set


class UserRole(Enum):
    """User roles in the system"""
    USER = "user"
    ADMIN = "admin"


class Permission(Enum):
    """System permissions"""
    # User management
    USER_VIEW = "user:view"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    
    # Course management
    COURSE_CREATE = "course:create"
    COURSE_EDIT = "course:edit"
    COURSE_DELETE = "course:delete"
    COURSE_VIEW = "course:view"
    
    # Webinar management
    WEBINAR_CREATE = "webinar:create"
    WEBINAR_EDIT = "webinar:edit"
    WEBINAR_DELETE = "webinar:delete"
    WEBINAR_VIEW = "webinar:view"
    
    # Purchase management
    PURCHASE_VIEW = "purchase:view"
    PURCHASE_REFUND = "purchase:refund"
    
    # Feedback and doubts
    FEEDBACK_CREATE = "feedback:create"
    FEEDBACK_VIEW = "feedback:view"
    FEEDBACK_MODERATE = "feedback:moderate"
    
    DOUBT_CREATE = "doubt:create"
    DOUBT_VIEW = "doubt:view"
    DOUBT_REPLY = "doubt:reply"
    DOUBT_MODERATE = "doubt:moderate"
    
    # Analytics and reports
    ANALYTICS_VIEW = "analytics:view"
    REPORTS_GENERATE = "reports:generate"
    
    # System administration
    SYSTEM_CONFIG = "system:config"
    USER_ADMIN = "user:admin"
    AUDIT_VIEW = "audit:view"


# Role-based permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.USER: {
        Permission.USER_VIEW,
        Permission.COURSE_VIEW,
        Permission.WEBINAR_VIEW,
        Permission.PURCHASE_VIEW,
        Permission.FEEDBACK_CREATE,
        Permission.FEEDBACK_VIEW,
        Permission.DOUBT_CREATE,
        Permission.DOUBT_VIEW,
    },
    
    UserRole.ADMIN: {
        # All permissions
        Permission.USER_VIEW,
        Permission.USER_EDIT,
        Permission.USER_DELETE,
        Permission.COURSE_CREATE,
        Permission.COURSE_EDIT,
        Permission.COURSE_DELETE,
        Permission.COURSE_VIEW,
        Permission.WEBINAR_CREATE,
        Permission.WEBINAR_EDIT,
        Permission.WEBINAR_DELETE,
        Permission.WEBINAR_VIEW,
        Permission.PURCHASE_VIEW,
        Permission.PURCHASE_REFUND,
        Permission.FEEDBACK_CREATE,
        Permission.FEEDBACK_VIEW,
        Permission.FEEDBACK_MODERATE,
        Permission.DOUBT_CREATE,
        Permission.DOUBT_VIEW,
        Permission.DOUBT_REPLY,
        Permission.DOUBT_MODERATE,
        Permission.ANALYTICS_VIEW,
        Permission.REPORTS_GENERATE,
        Permission.SYSTEM_CONFIG,
        Permission.USER_ADMIN,
        Permission.AUDIT_VIEW,
    }
}


# Role hierarchy for inheritance
ROLE_HIERARCHY: List[UserRole] = [
    UserRole.USER,
    UserRole.ADMIN
]


def get_role_permissions(role: UserRole) -> Set[Permission]:
    """
    Get permissions for a specific role
    
    Args:
        role: User role
        
    Returns:
        Set of permissions for the role
    """
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    """
    Check if a role has a specific permission
    
    Args:
        role: User role
        permission: Permission to check
        
    Returns:
        True if role has permission
    """
    return permission in ROLE_PERMISSIONS.get(role, set())


def has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
    """
    Check if a role has any of the specified permissions
    
    Args:
        role: User role
        permissions: List of permissions to check
        
    Returns:
        True if role has any of the permissions
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return any(perm in role_perms for perm in permissions)


def has_all_permissions(role: UserRole, permissions: List[Permission]) -> bool:
    """
    Check if a role has all of the specified permissions
    
    Args:
        role: User role
        permissions: List of permissions to check
        
    Returns:
        True if role has all of the permissions
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return all(perm in role_perms for perm in permissions)


def is_higher_role(role1: UserRole, role2: UserRole) -> bool:
    """
    Check if role1 is higher in hierarchy than role2
    
    Args:
        role1: First role to compare
        role2: Second role to compare
        
    Returns:
        True if role1 is higher than role2
    """
    try:
        index1 = ROLE_HIERARCHY.index(role1)
        index2 = ROLE_HIERARCHY.index(role2)
        return index1 > index2
    except ValueError:
        return False


def get_role_display_name(role: UserRole) -> str:
    """
    Get display name for a role
    
    Args:
        role: User role
        
    Returns:
        Display name for the role
    """
    role_names = {
        UserRole.USER: "User",
        UserRole.ADMIN: "Administrator"
    }
    return role_names.get(role, role.value.title())


def get_all_roles() -> List[UserRole]:
    """
    Get all available roles
    
    Returns:
        List of all user roles
    """
    return list(UserRole)


def get_all_permissions() -> List[Permission]:
    """
    Get all available permissions
    
    Returns:
        List of all permissions
    """
    return list(Permission)


# Permission categories for UI grouping
PERMISSION_CATEGORIES = {
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