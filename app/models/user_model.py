"""
User Model for Firestore Database
Handles user profile, authentication, and role management
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator
from app.constants.roles import UserRole


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BANNED = "banned"


class UserPreferences(BaseModel):
    """User preferences and settings"""
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light"
    privacy_level: str = "public"  # public, friends, private


class UserProfile(BaseModel):
    """User profile information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    education: Optional[str] = None
    profession: Optional[str] = None
    interests: List[str] = []
    
    @validator('first_name', 'last_name', 'display_name')
    def validate_names(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Basic phone validation - remove all non-digits
            import re
            v = re.sub(r'[^\d+]', '', v)
            if len(v) < 10:
                raise ValueError('Phone number must be at least 10 digits')
        return v


class UserModel:
    """User model for Firestore operations"""
    
    COLLECTION_NAME = "users"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def create_user_data(
        self,
        uid: str,
        email: str,
        role: UserRole = UserRole.USER,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create user data structure
        
        Args:
            uid: Firebase UID
            email: User email
            role: User role (default: USER)
            additional_data: Additional user data
            
        Returns:
            Dictionary with user data
        """
        user_data = {
            "id": uid,
            "uid": uid,
            "email": email.lower(),
            "email_verified": False,
            "role": role.value,
            "status": UserStatus.PENDING_VERIFICATION.value,
            "profile": UserProfile().dict(),
            "preferences": UserPreferences().dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "login_count": 0,
            "subscription": {
                "is_premium": False,
                "plan": None,
                "expires_at": None
            },
            "stats": {
                "courses_purchased": 0,
                "webinars_attended": 0,
                "doubts_asked": 0,
                "feedback_given": 0,
                "total_spent": 0.0
            },
            "security": {
                "failed_login_attempts": 0,
                "last_failed_login": None,
                "account_locked": False,
                "two_factor_enabled": False,
                "backup_codes": []
            },
            "metadata": {}
        }
        
        if additional_data:
            user_data["metadata"].update(additional_data)
        
        return user_data
    
    async def create_user(
        self,
        uid: str,
        email: str,
        role: UserRole = UserRole.USER,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new user in Firestore
        
        Args:
            uid: Firebase UID
            email: User email
            role: User role
            additional_data: Additional user data
            
        Returns:
            User ID
        """
        user_data = self.create_user_data(uid, email, role, additional_data)
        
        # Check if user already exists
        existing_user = await self.get_user_by_uid(uid)
        if existing_user:
            raise ValueError("User already exists")
        
        # Create user document
        doc_ref = self.collection.document(uid)
        await doc_ref.set(user_data)
        
        return uid
    
    async def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user by Firebase UID
        
        Args:
            uid: Firebase UID
            
        Returns:
            User data or None if not found
        """
        doc = self.collection.document(uid).get()
        
        if doc.exists:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            return user_data
        
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address
        
        Args:
            email: User email
            
        Returns:
            User data or None if not found
        """
        query = self.collection.where("email", "==", email.lower()).limit(1)
        docs = query.get()
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            return user_data
        
        return None
    
    async def update_user(
        self,
        uid: str,
        updates: Dict[str, Any],
        update_timestamps: bool = True
    ) -> bool:
        """
        Update user data
        
        Args:
            uid: User ID
            updates: Fields to update
            update_timestamps: Whether to update timestamps
            
        Returns:
            True if successful
        """
        if update_timestamps:
            updates["updated_at"] = datetime.utcnow()
        
        # Clean up None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        if not updates:
            return False
        
        doc_ref = self.collection.document(uid)
        await doc_ref.update(updates)
        
        return True
    
    async def update_user_profile(self, uid: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update user profile
        
        Args:
            uid: User ID
            profile_data: Profile data to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(uid).get()
        
        if not doc.exists:
            raise ValueError("User not found")
        
        current_user = doc.to_dict()
        current_profile = current_user.get("profile", {})
        
        # Merge with existing profile
        updated_profile = {**current_profile, **profile_data}
        
        return await self.update_user(uid, {"profile": updated_profile})
    
    async def update_user_preferences(self, uid: str, preferences_data: Dict[str, Any]) -> bool:
        """
        Update user preferences
        
        Args:
            uid: User ID
            preferences_data: Preferences to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(uid).get()
        
        if not doc.exists:
            raise ValueError("User not found")
        
        current_user = doc.to_dict()
        current_preferences = current_user.get("preferences", {})
        
        # Merge with existing preferences
        updated_preferences = {**current_preferences, **preferences_data}
        
        return await self.update_user(uid, {"preferences": updated_preferences})
    
    async def update_user_role(self, uid: str, role: UserRole) -> bool:
        """
        Update user role
        
        Args:
            uid: User ID
            role: New user role
            
        Returns:
            True if successful
        """
        return await self.update_user(uid, {"role": role.value})
    
    async def update_user_status(self, uid: str, status: UserStatus) -> bool:
        """
        Update user status
        
        Args:
            uid: User ID
            status: New user status
            
        Returns:
            True if successful
        """
        return await self.update_user(uid, {"status": status.value})
    
    async def record_login(self, uid: str) -> bool:
        """
        Record user login
        
        Args:
            uid: User ID
            
        Returns:
            True if successful
        """
        updates = {
            "last_login": datetime.utcnow(),
            "login_count": self.collection.document(uid).get().to_dict().get("login_count", 0) + 1,
            "security.failed_login_attempts": 0
        }
        
        doc_ref = self.collection.document(uid)
        await doc_ref.update(updates)
        
        return True
    
    async def record_failed_login(self, uid: str, max_attempts: int = 5) -> bool:
        """
        Record failed login attempt
        
        Args:
            uid: User ID
            max_attempts: Maximum attempts before lockout
            
        Returns:
            True if successful
        """
        doc = self.collection.document(uid).get()
        
        if not doc.exists:
            return False
        
        current_data = doc.to_dict()
        failed_attempts = current_data.get("security", {}).get("failed_login_attempts", 0) + 1
        
        updates = {
            "security.failed_login_attempts": failed_attempts,
            "security.last_failed_login": datetime.utcnow(),
            "security.account_locked": failed_attempts >= max_attempts
        }
        
        await self.collection.document(uid).update(updates)
        return True
    
    async def update_user_stats(self, uid: str, stats_updates: Dict[str, Any]) -> bool:
        """
        Update user statistics
        
        Args:
            uid: User ID
            stats_updates: Stats to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(uid).get()
        
        if not doc.exists:
            return False
        
        current_user = doc.to_dict()
        current_stats = current_user.get("stats", {})
        
        # Handle numeric updates
        updated_stats = current_stats.copy()
        for key, value in stats_updates.items():
            if key in current_stats and isinstance(current_stats[key], (int, float)) and isinstance(value, (int, float)):
                updated_stats[key] = current_stats[key] + value
            else:
                updated_stats[key] = value
        
        return await self.update_user(uid, {"stats": updated_stats})
    
    async def delete_user(self, uid: str) -> bool:
        """
        Delete user account (soft delete)
        
        Args:
            uid: User ID
            
        Returns:
            True if successful
        """
        updates = {
            "status": UserStatus.BANNED.value,
            "deleted_at": datetime.utcnow(),
            "email": f"deleted_{datetime.utcnow().timestamp()}@deleted.local"
        }
        
        return await self.update_user(uid, updates)
    
    async def search_users(
        self,
        search_term: str = "",
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search users with filters
        
        Args:
            search_term: Search term for name or email
            role: Filter by role
            status: Filter by status
            limit: Results limit
            offset: Results offset
            
        Returns:
            Dictionary with users and pagination info
        """
        query = self.collection
        
        # Apply filters
        if role:
            query = query.where("role", "==", role.value)
        
        if status:
            query = query.where("status", "==", status.value)
        
        # Order by creation date
        query = query.order_by("created_at", direction="DESCENDING")
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            
            # Apply search filter if provided
            if search_term:
                search_fields = [
                    user_data.get("email", ""),
                    user_data.get("profile", {}).get("first_name", ""),
                    user_data.get("profile", {}).get("last_name", ""),
                    user_data.get("profile", {}).get("display_name", "")
                ]
                
                if not any(search_term.lower() in field.lower() for field in search_fields if field):
                    continue
            
            users.append(user_data)
        
        # Get total count
        count_query = self.collection
        if role:
            count_query = count_query.where("role", "==", role.value)
        if status:
            count_query = count_query.where("status", "==", status.value)
        
        total_count = len(count_query.get())
        
        return {
            "users": users,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get overall user statistics
        
        Returns:
            Dictionary with user statistics
        """
        docs = self.collection.get()
        
        stats = {
            "total_users": 0,
            "users_by_role": {},
            "users_by_status": {},
            "active_users_today": 0,
            "active_users_week": 0,
            "active_users_month": 0,
            "new_users_today": 0,
            "new_users_week": 0,
            "new_users_month": 0
        }
        
        now = datetime.utcnow()
        today = now.date()
        week_ago = today.replace(day=max(1, today.day - 7))
        month_ago = today.replace(day=1)
        
        for doc in docs:
            user_data = doc.to_dict()
            stats["total_users"] += 1
            
            # Count by role
            role = user_data.get("role", "unknown")
            stats["users_by_role"][role] = stats["users_by_role"].get(role, 0) + 1
            
            # Count by status
            status = user_data.get("status", "unknown")
            stats["users_by_status"][status] = stats["users_by_status"].get(status, 0) + 1
            
            # Active users (logged in within time period)
            last_login = user_data.get("last_login")
            if last_login:
                if isinstance(last_login, datetime):
                    login_date = last_login.date()
                else:
                    login_date = last_login.date()
                
                if login_date >= today:
                    stats["active_users_today"] += 1
                if login_date >= week_ago:
                    stats["active_users_week"] += 1
                if login_date >= month_ago:
                    stats["active_users_month"] += 1
            
            # New users (created within time period)
            created_at = user_data.get("created_at")
            if created_at:
                if isinstance(created_at, datetime):
                    created_date = created_at.date()
                else:
                    created_date = created_at.date()
                
                if created_date >= today:
                    stats["new_users_today"] += 1
                if created_date >= week_ago:
                    stats["new_users_week"] += 1
                if created_date >= month_ago:
                    stats["new_users_month"] += 1
        
        return stats


# Dependency for user operations
class UserDependency:
    """Helper class for user-related dependencies"""
    
    def __init__(self):
        self.model = UserModel()
    
    async def get_current_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return await self.model.get_user_by_uid(uid)
    
    async def require_active_user(self, uid: str) -> Dict[str, Any]:
        """Require active user, raise exception if not found or inactive"""
        user = await self.get_current_user(uid)
        
        if not user:
            raise ValueError("User not found")
        
        if user.get("status") != UserStatus.ACTIVE.value:
            raise ValueError("User account is not active")
        
        return user