"""
Status constants for the E-Learning Platform
Defines various status enums used throughout the system
"""

from enum import Enum
from typing import List, Dict


# User Status
class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BANNED = "banned"


# Course Status
class CourseStatus(Enum):
    """Course status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    PENDING_APPROVAL = "pending_approval"
    REJECTED = "rejected"


# Webinar Status
class WebinarStatus(Enum):
    """Webinar status"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


# Purchase Status
class PurchaseStatus(Enum):
    """Purchase status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"


# Payment Status
class PaymentStatus(Enum):
    """Payment transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"


# Feedback Status
class FeedbackStatus(Enum):
    """Feedback status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


# Doubt Status
class DoubtStatus(Enum):
    """Doubt/Q&A status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FLAGGED = "flagged"


# Notification Status
class NotificationStatus(Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


# Access Level
class AccessLevel(Enum):
    """Content access levels"""
    FREE = "free"
    PURCHASED = "purchased"
    SUBSCRIPTION = "subscription"
    PREMIUM = "premium"
    ADMIN_ONLY = "admin_only"


# File Upload Status
class FileUploadStatus(Enum):
    """File upload status"""
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"


# Webinar Registration Status
class WebinarRegistrationStatus(Enum):
    """Webinar registration status"""
    REGISTERED = "registered"
    CANCELLED = "cancelled"
    ATTENDED = "attended"
    NO_SHOW = "no_show"


# Subscription Status
class SubscriptionStatus(Enum):
    """Subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"


# Audit Action Types
class AuditAction(Enum):
    """Audit log action types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    PAYMENT = "payment"
    REFUND = "refund"


# Rate Limit Status
class RateLimitStatus(Enum):
    """Rate limiting status"""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    THROTTLED = "throttled"


# API Response Status
class APIResponseStatus(Enum):
    """API response status"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Email Status
class EmailStatus(Enum):
    """Email status"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"


# Webhook Status
class WebhookStatus(Enum):
    """Webhook status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


# Session Status
class SessionStatus(Enum):
    """User session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


# Status mapping for display names
STATUS_DISPLAY_NAMES = {
    # User Status
    UserStatus.ACTIVE: "Active",
    UserStatus.INACTIVE: "Inactive",
    UserStatus.SUSPENDED: "Suspended",
    UserStatus.PENDING_VERIFICATION: "Pending Verification",
    UserStatus.BANNED: "Banned",
    
    # Course Status
    CourseStatus.DRAFT: "Draft",
    CourseStatus.PUBLISHED: "Published",
    CourseStatus.ARCHIVED: "Archived",
    CourseStatus.PENDING_APPROVAL: "Pending Approval",
    CourseStatus.REJECTED: "Rejected",
    
    # Webinar Status
    WebinarStatus.SCHEDULED: "Scheduled",
    WebinarStatus.LIVE: "Live",
    WebinarStatus.COMPLETED: "Completed",
    WebinarStatus.CANCELLED: "Cancelled",
    WebinarStatus.POSTPONED: "Postponed",
    
    # Purchase Status
    PurchaseStatus.PENDING: "Pending",
    PurchaseStatus.COMPLETED: "Completed",
    PurchaseStatus.FAILED: "Failed",
    PurchaseStatus.REFUNDED: "Refunded",
    PurchaseStatus.PARTIALLY_REFUNDED: "Partially Refunded",
    PurchaseStatus.CANCELLED: "Cancelled",
    
    # Payment Status
    PaymentStatus.PENDING: "Pending",
    PaymentStatus.PROCESSING: "Processing",
    PaymentStatus.COMPLETED: "Completed",
    PaymentStatus.FAILED: "Failed",
    PaymentStatus.CANCELLED: "Cancelled",
    PaymentStatus.REFUNDED: "Refunded",
    PaymentStatus.PARTIALLY_REFUNDED: "Partially Refunded",
    PaymentStatus.DISPUTED: "Disputed",
    
    # Feedback Status
    FeedbackStatus.PENDING: "Pending",
    FeedbackStatus.APPROVED: "Approved",
    FeedbackStatus.REJECTED: "Rejected",
    FeedbackStatus.FLAGGED: "Flagged",
    
    # Doubt Status
    DoubtStatus.OPEN: "Open",
    DoubtStatus.IN_PROGRESS: "In Progress",
    DoubtStatus.RESOLVED: "Resolved",
    DoubtStatus.CLOSED: "Closed",
    DoubtStatus.FLAGGED: "Flagged",
    
    # Notification Status
    NotificationStatus.PENDING: "Pending",
    NotificationStatus.SENT: "Sent",
    NotificationStatus.DELIVERED: "Delivered",
    NotificationStatus.FAILED: "Failed",
    NotificationStatus.READ: "Read",
    
    # Access Level
    AccessLevel.FREE: "Free",
    AccessLevel.PURCHASED: "Purchased",
    AccessLevel.SUBSCRIPTION: "Subscription",
    AccessLevel.PREMIUM: "Premium",
    AccessLevel.ADMIN_ONLY: "Admin Only",
    
    # File Upload Status
    FileUploadStatus.UPLOADING: "Uploading",
    FileUploadStatus.COMPLETED: "Completed",
    FileUploadStatus.FAILED: "Failed",
    FileUploadStatus.PROCESSING: "Processing",
    
    # Webinar Registration Status
    WebinarRegistrationStatus.REGISTERED: "Registered",
    WebinarRegistrationStatus.CANCELLED: "Cancelled",
    WebinarRegistrationStatus.ATTENDED: "Attended",
    WebinarRegistrationStatus.NO_SHOW: "No Show",
    
    # Subscription Status
    SubscriptionStatus.ACTIVE: "Active",
    SubscriptionStatus.EXPIRED: "Expired",
    SubscriptionStatus.CANCELLED: "Cancelled",
    SubscriptionStatus.PAST_DUE: "Past Due",
    SubscriptionStatus.UNPAID: "Unpaid",
    
    # Email Status
    EmailStatus.QUEUED: "Queued",
    EmailStatus.SENT: "Sent",
    EmailStatus.DELIVERED: "Delivered",
    EmailStatus.FAILED: "Failed",
    EmailStatus.BOUNCED: "Bounced",
    EmailStatus.OPENED: "Opened",
    EmailStatus.CLICKED: "Clicked",
    
    # Webhook Status
    WebhookStatus.PENDING: "Pending",
    WebhookStatus.PROCESSING: "Processing",
    WebhookStatus.COMPLETED: "Completed",
    WebhookStatus.FAILED: "Failed",
    WebhookStatus.RETRY: "Retry",
    
    # Session Status
    SessionStatus.ACTIVE: "Active",
    SessionStatus.EXPIRED: "Expired",
    SessionStatus.REVOKED: "Revoked",
}


def get_status_display_name(status: Enum) -> str:
    """
    Get display name for a status enum
    
    Args:
        status: Status enum value
        
    Returns:
        Display name for the status
    """
    return STATUS_DISPLAY_NAMES.get(status, status.value.title())


def is_active_status(status: Enum) -> bool:
    """
    Check if a status represents an active/operational state
    
    Args:
        status: Status enum value
        
    Returns:
        True if status is active
    """
    active_statuses = {
        UserStatus.ACTIVE,
        CourseStatus.PUBLISHED,
        WebinarStatus.SCHEDULED,
        WebinarStatus.LIVE,
        PurchaseStatus.COMPLETED,
        PaymentStatus.COMPLETED,
        AccessLevel.FREE,
        AccessLevel.PURCHASED,
        SubscriptionStatus.ACTIVE,
        SessionStatus.ACTIVE,
    }
    
    return status in active_statuses


def is_error_status(status: Enum) -> bool:
    """
    Check if a status represents an error/failure state
    
    Args:
        status: Status enum value
        
    Returns:
        True if status is an error state
    """
    error_statuses = {
        UserStatus.SUSPENDED,
        UserStatus.BANNED,
        CourseStatus.REJECTED,
        WebinarStatus.CANCELLED,
        PurchaseStatus.FAILED,
        PurchaseStatus.CANCELLED,
        PaymentStatus.FAILED,
        PaymentStatus.CANCELLED,
        FeedbackStatus.REJECTED,
        FeedbackStatus.FLAGGED,
        DoubtStatus.FLAGGED,
        NotificationStatus.FAILED,
        FileUploadStatus.FAILED,
        EmailStatus.FAILED,
        EmailStatus.BOUNCED,
        WebhookStatus.FAILED,
        SessionStatus.EXPIRED,
        SessionStatus.REVOKED,
    }
    
    return status in error_statuses


def is_pending_status(status: Enum) -> bool:
    """
    Check if a status represents a pending state
    
    Args:
        status: Status enum value
        
    Returns:
        True if status is pending
    """
    pending_statuses = {
        UserStatus.PENDING_VERIFICATION,
        CourseStatus.DRAFT,
        CourseStatus.PENDING_APPROVAL,
        PurchaseStatus.PENDING,
        PaymentStatus.PENDING,
        PaymentStatus.PROCESSING,
        FeedbackStatus.PENDING,
        DoubtStatus.OPEN,
        NotificationStatus.PENDING,
        FileUploadStatus.UPLOADING,
        FileUploadStatus.PROCESSING,
        EmailStatus.QUEUED,
        WebhookStatus.PENDING,
        WebhookStatus.PROCESSING,
    }
    
    return status in pending_statuses


def get_valid_statuses_for_type(status_type: str) -> List[Enum]:
    """
    Get all valid statuses for a given status type
    
    Args:
        status_type: Type of status (e.g., 'user', 'course', 'webinar')
        
    Returns:
        List of valid status enum values
    """
    status_mappings = {
        'user': list(UserStatus),
        'course': list(CourseStatus),
        'webinar': list(WebinarStatus),
        'purchase': list(PurchaseStatus),
        'payment': list(PaymentStatus),
        'feedback': list(FeedbackStatus),
        'doubt': list(DoubtStatus),
        'notification': list(NotificationStatus),
        'access': list(AccessLevel),
        'file_upload': list(FileUploadStatus),
        'webinar_registration': list(WebinarRegistrationStatus),
        'subscription': list(SubscriptionStatus),
        'email': list(EmailStatus),
        'webhook': list(WebhookStatus),
        'session': list(SessionStatus),
    }
    
    return status_mappings.get(status_type, [])


# Color coding for UI status indicators
STATUS_COLORS = {
    # Success/Active states - Green
    UserStatus.ACTIVE: "#10B981",
    CourseStatus.PUBLISHED: "#10B981",
    WebinarStatus.SCHEDULED: "#10B981",
    WebinarStatus.LIVE: "#10B981",
    PurchaseStatus.COMPLETED: "#10B981",
    PaymentStatus.COMPLETED: "#10B981",
    FeedbackStatus.APPROVED: "#10B981",
    DoubtStatus.RESOLVED: "#10B981",
    NotificationStatus.SENT: "#10B981",
    NotificationStatus.DELIVERED: "#10B981",
    NotificationStatus.READ: "#10B981",
    AccessLevel.FREE: "#10B981",
    AccessLevel.PURCHASED: "#10B981",
    FileUploadStatus.COMPLETED: "#10B981",
    WebinarRegistrationStatus.REGISTERED: "#10B981",
    WebinarRegistrationStatus.ATTENDED: "#10B981",
    SubscriptionStatus.ACTIVE: "#10B981",
    EmailStatus.SENT: "#10B981",
    EmailStatus.DELIVERED: "#10B981",
    EmailStatus.OPENED: "#10B981",
    EmailStatus.CLICKED: "#10B981",
    WebhookStatus.COMPLETED: "#10B981",
    SessionStatus.ACTIVE: "#10B981",
    
    # Pending/Warning states - Yellow/Orange
    UserStatus.PENDING_VERIFICATION: "#F59E0B",
    CourseStatus.DRAFT: "#F59E0B",
    CourseStatus.PENDING_APPROVAL: "#F59E0B",
    WebinarStatus.POSTPONED: "#F59E0B",
    PurchaseStatus.PENDING: "#F59E0B",
    PaymentStatus.PENDING: "#F59E0B",
    PaymentStatus.PROCESSING: "#F59E0B",
    FeedbackStatus.PENDING: "#F59E0B",
    DoubtStatus.OPEN: "#F59E0B",
    DoubtStatus.IN_PROGRESS: "#F59E0B",
    NotificationStatus.PENDING: "#F59E0B",
    FileUploadStatus.UPLOADING: "#F59E0B",
    FileUploadStatus.PROCESSING: "#F59E0B",
    EmailStatus.QUEUED: "#F59E0B",
    WebhookStatus.PENDING: "#F59E0B",
    WebhookStatus.PROCESSING: "#F59E0B",
    WebhookStatus.RETRY: "#F59E0B",
    SubscriptionStatus.PAST_DUE: "#F59E0B",
    
    # Error/Failed states - Red
    UserStatus.SUSPENDED: "#EF4444",
    UserStatus.BANNED: "#EF4444",
    CourseStatus.REJECTED: "#EF4444",
    CourseStatus.ARCHIVED: "#EF4444",
    WebinarStatus.CANCELLED: "#EF4444",
    PurchaseStatus.FAILED: "#EF4444",
    PurchaseStatus.CANCELLED: "#EF4444",
    PaymentStatus.FAILED: "#EF4444",
    PaymentStatus.CANCELLED: "#EF4444",
    FeedbackStatus.REJECTED: "#EF4444",
    FeedbackStatus.FLAGGED: "#EF4444",
    DoubtStatus.FLAGGED: "#EF4444",
    NotificationStatus.FAILED: "#EF4444",
    FileUploadStatus.FAILED: "#EF4444",
    WebinarRegistrationStatus.CANCELLED: "#EF4444",
    WebinarRegistrationStatus.NO_SHOW: "#EF4444",
    SubscriptionStatus.EXPIRED: "#EF4444",
    SubscriptionStatus.CANCELLED: "#EF4444",
    SubscriptionStatus.UNPAID: "#EF4444",
    EmailStatus.FAILED: "#EF4444",
    EmailStatus.BOUNCED: "#EF4444",
    WebhookStatus.FAILED: "#EF4444",
    SessionStatus.EXPIRED: "#EF4444",
    SessionStatus.REVOKED: "#EF4444",
    
    # Neutral states - Gray
    UserStatus.INACTIVE: "#6B7280",
    WebinarStatus.COMPLETED: "#6B7280",
    PurchaseStatus.REFUNDED: "#6B7280",
    PurchaseStatus.PARTIALLY_REFUNDED: "#6B7280",
    PaymentStatus.REFUNDED: "#6B7280",
    PaymentStatus.PARTIALLY_REFUNDED: "#6B7280",
    PaymentStatus.DISPUTED: "#6B7280",
    DoubtStatus.CLOSED: "#6B7280",
    AccessLevel.SUBSCRIPTION: "#6B7280",
    AccessLevel.PREMIUM: "#6B7280",
    AccessLevel.ADMIN_ONLY: "#6B7280",
}


def get_status_color(status: Enum) -> str:
    """
    Get color code for status for UI display
    
    Args:
        status: Status enum value
        
    Returns:
        Hex color code
    """
    return STATUS_COLORS.get(status, "#6B7280")  # Default gray