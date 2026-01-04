"""
Admin Activity Model for Audit Logging
Tracks all admin actions for security and compliance
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from app.models.user_model import UserModel


class AdminActivityType(str, Enum):
    """Types of admin activities"""
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_SUSPEND = "user_suspend"
    USER_ACTIVATE = "user_activate"
    USER_ROLE_CHANGE = "user_role_change"
    
    # Course Management
    COURSE_CREATE = "course_create"
    COURSE_UPDATE = "course_update"
    COURSE_DELETE = "course_delete"
    COURSE_PUBLISH = "course_publish"
    COURSE_UNPUBLISH = "course_unpublish"
    COURSE_PRICE_CHANGE = "course_price_change"
    
    # Webinar Management
    WEBINAR_CREATE = "webinar_create"
    WEBINAR_UPDATE = "webinar_update"
    WEBINAR_DELETE = "webinar_delete"
    WEBINAR_SCHEDULE_CHANGE = "webinar_schedule_change"
    WEBINAR_PRICE_CHANGE = "webinar_price_change"
    
    # Purchase Management
    PURCHASE_REFUND = "purchase_refund"
    PURCHASE_REVERSE = "purchase_reverse"
    PURCHASE_MANUAL_CREATE = "purchase_manual_create"
    PURCHASE_STATUS_CHANGE = "purchase_status_change"
    
    # Content Moderation
    DOUBT_DELETE = "doubt_delete"
    DOUBT_MODERATE = "doubt_moderate"
    FEEDBACK_DELETE = "feedback_delete"
    FEEDBACK_MODERATE = "feedback_moderate"
    
    # System Administration
    SETTINGS_UPDATE = "settings_update"
    BACKUP_CREATE = "backup_create"
    MAINTENANCE_MODE = "maintenance_mode"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    
    # Security
    SECURITY_ALERT = "security_alert"
    ACCESS_REVOCATION = "access_revocation"
    SECURITY_SCAN = "security_scan"


class AdminActivityModel:
    """Admin activity logging model for Firestore"""
    
    COLLECTION_NAME = "admin_activities"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def create_activity_log(
        self,
        admin_id: str,
        activity_type: AdminActivityType,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        description: str = "",
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an admin activity log entry
        
        Args:
            admin_id: ID of the admin performing the action
            activity_type: Type of activity performed
            target_type: Type of entity being acted upon (user, course, etc.)
            target_id: ID of the entity being acted upon
            description: Human-readable description of the action
            old_data: Previous state of the entity
            new_data: New state of the entity
            ip_address: IP address of the admin
            user_agent: User agent of the admin
            additional_info: Additional contextual information
            
        Returns:
            Dictionary with activity log data
        """
        activity_data = {
            "admin_id": admin_id,
            "activity_type": activity_type.value,
            "target_type": target_type,
            "target_id": target_id,
            "description": description,
            "timestamp": datetime.utcnow(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "old_data": old_data or {},
            "new_data": new_data or {},
            "additional_info": additional_info or {},
            "status": "completed",  # completed, failed, pending
            "risk_level": self._calculate_risk_level(activity_type),
            "category": self._categorize_activity(activity_type)
        }
        
        return activity_data
    
    def _calculate_risk_level(self, activity_type: AdminActivityType) -> str:
        """Calculate risk level based on activity type"""
        high_risk_activities = {
            AdminActivityType.USER_DELETE,
            AdminActivityType.USER_SUSPEND,
            AdminActivityType.COURSE_DELETE,
            AdminActivityType.WEBINAR_DELETE,
            AdminActivityType.PURCHASE_REFUND,
            AdminActivityType.PURCHASE_REVERSE,
            AdminActivityType.DOUBT_DELETE,
            AdminActivityType.FEEDBACK_DELETE,
            AdminActivityType.SETTINGS_UPDATE,
            AdminActivityType.MAINTENANCE_MODE,
            AdminActivityType.ACCESS_REVOCATION
        }
        
        medium_risk_activities = {
            AdminActivityType.USER_ROLE_CHANGE,
            AdminActivityType.COURSE_PRICE_CHANGE,
            AdminActivityType.WEBINAR_PRICE_CHANGE,
            AdminActivityType.PURCHASE_MANUAL_CREATE,
            AdminActivityType.DOUBT_MODERATE,
            AdminActivityType.FEEDBACK_MODERATE,
            AdminActivityType.SECURITY_ALERT
        }
        
        if activity_type in high_risk_activities:
            return "high"
        elif activity_type in medium_risk_activities:
            return "medium"
        else:
            return "low"
    
    def _categorize_activity(self, activity_type: AdminActivityType) -> str:
        """Categorize activity for reporting"""
        user_activities = {
            AdminActivityType.USER_CREATE,
            AdminActivityType.USER_UPDATE,
            AdminActivityType.USER_DELETE,
            AdminActivityType.USER_SUSPEND,
            AdminActivityType.USER_ACTIVATE,
            AdminActivityType.USER_ROLE_CHANGE
        }
        
        course_activities = {
            AdminActivityType.COURSE_CREATE,
            AdminActivityType.COURSE_UPDATE,
            AdminActivityType.COURSE_DELETE,
            AdminActivityType.COURSE_PUBLISH,
            AdminActivityType.COURSE_UNPUBLISH,
            AdminActivityType.COURSE_PRICE_CHANGE
        }
        
        webinar_activities = {
            AdminActivityType.WEBINAR_CREATE,
            AdminActivityType.WEBINAR_UPDATE,
            AdminActivityType.WEBINAR_DELETE,
            AdminActivityType.WEBINAR_SCHEDULE_CHANGE,
            AdminActivityType.WEBINAR_PRICE_CHANGE
        }
        
        purchase_activities = {
            AdminActivityType.PURCHASE_REFUND,
            AdminActivityType.PURCHASE_REVERSE,
            AdminActivityType.PURCHASE_MANUAL_CREATE,
            AdminActivityType.PURCHASE_STATUS_CHANGE
        }
        
        content_activities = {
            AdminActivityType.DOUBT_DELETE,
            AdminActivityType.DOUBT_MODERATE,
            AdminActivityType.FEEDBACK_DELETE,
            AdminActivityType.FEEDBACK_MODERATE
        }
        
        system_activities = {
            AdminActivityType.SETTINGS_UPDATE,
            AdminActivityType.BACKUP_CREATE,
            AdminActivityType.MAINTENANCE_MODE,
            AdminActivityType.SYSTEM_CONFIG_CHANGE
        }
        
        security_activities = {
            AdminActivityType.SECURITY_ALERT,
            AdminActivityType.ACCESS_REVOCATION,
            AdminActivityType.SECURITY_SCAN
        }
        
        if activity_type in user_activities:
            return "user_management"
        elif activity_type in course_activities:
            return "course_management"
        elif activity_type in webinar_activities:
            return "webinar_management"
        elif activity_type in purchase_activities:
            return "purchase_management"
        elif activity_type in content_activities:
            return "content_moderation"
        elif activity_type in system_activities:
            return "system_administration"
        elif activity_type in security_activities:
            return "security"
        else:
            return "other"
    
    async def log_activity(
        self,
        admin_id: str,
        activity_type: AdminActivityType,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        description: str = "",
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
        status: str = "completed"
    ) -> str:
        """
        Log an admin activity to Firestore
        
        Args:
            admin_id: ID of the admin performing the action
            activity_type: Type of activity performed
            target_type: Type of entity being acted upon
            target_id: ID of the entity being acted upon
            description: Human-readable description
            old_data: Previous state of the entity
            new_data: New state of the entity
            ip_address: IP address of the admin
            user_agent: User agent of the admin
            additional_info: Additional contextual information
            status: Status of the activity (completed, failed, pending)
            
        Returns:
            ID of the created activity log
        """
        activity_data = self.create_activity_log(
            admin_id=admin_id,
            activity_type=activity_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_info=additional_info
        )
        
        activity_data["status"] = status
        
        # Add to Firestore
        doc_ref = self.collection.document()
        activity_data["id"] = doc_ref.id
        await doc_ref.set(activity_data)
        
        return doc_ref.id
    
    async def get_activities(
        self,
        admin_id: Optional[str] = None,
        activity_type: Optional[AdminActivityType] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get admin activities with filtering and pagination
        
        Args:
            admin_id: Filter by admin ID
            activity_type: Filter by activity type
            target_type: Filter by target type
            target_id: Filter by target ID
            risk_level: Filter by risk level
            category: Filter by category
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Number of results to return
            offset: Number of results to skip
            
        Returns:
            Dictionary with activities and pagination info
        """
        query = self.collection
        
        # Apply filters
        if admin_id:
            query = query.where("admin_id", "==", admin_id)
        
        if activity_type:
            query = query.where("activity_type", "==", activity_type.value)
        
        if target_type:
            query = query.where("target_type", "==", target_type)
        
        if target_id:
            query = query.where("target_id", "==", target_id)
        
        if risk_level:
            query = query.where("risk_level", "==", risk_level)
        
        if category:
            query = query.where("category", "==", category)
        
        if start_date:
            query = query.where("timestamp", ">=", start_date)
        
        if end_date:
            query = query.where("timestamp", "<=", end_date)
        
        # Order by timestamp descending
        query = query.order_by("timestamp", direction="DESCENDING")
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        activities = []
        for doc in docs:
            activity = doc.to_dict()
            activity["id"] = doc.id
            activities.append(activity)
        
        # Get total count for pagination
        count_query = self.collection
        if admin_id:
            count_query = count_query.where("admin_id", "==", admin_id)
        if activity_type:
            count_query = count_query.where("activity_type", "==", activity_type.value)
        if target_type:
            count_query = count_query.where("target_type", "==", target_type)
        if target_id:
            count_query = count_query.where("target_id", "==", target_id)
        if risk_level:
            count_query = count_query.where("risk_level", "==", risk_level)
        if category:
            count_query = count_query.where("category", "==", category)
        if start_date:
            count_query = count_query.where("timestamp", ">=", start_date)
        if end_date:
            count_query = count_query.where("timestamp", "<=", end_date)
        
        total_count = len(count_query.get())
        
        return {
            "activities": activities,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_activity_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get admin activity statistics
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with activity statistics
        """
        query = self.collection
        
        if start_date:
            query = query.where("timestamp", ">=", start_date)
        
        if end_date:
            query = query.where("timestamp", "<=", end_date)
        
        docs = query.get()
        
        stats = {
            "total_activities": 0,
            "activities_by_type": {},
            "activities_by_admin": {},
            "activities_by_category": {},
            "activities_by_risk_level": {},
            "recent_activities": []
        }
        
        for doc in docs:
            activity = doc.to_dict()
            stats["total_activities"] += 1
            
            # Count by type
            activity_type = activity.get("activity_type", "unknown")
            stats["activities_by_type"][activity_type] = stats["activities_by_type"].get(activity_type, 0) + 1
            
            # Count by admin
            admin_id = activity.get("admin_id", "unknown")
            stats["activities_by_admin"][admin_id] = stats["activities_by_admin"].get(admin_id, 0) + 1
            
            # Count by category
            category = activity.get("category", "unknown")
            stats["activities_by_category"][category] = stats["activities_by_category"].get(category, 0) + 1
            
            # Count by risk level
            risk_level = activity.get("risk_level", "unknown")
            stats["activities_by_risk_level"][risk_level] = stats["activities_by_risk_level"].get(risk_level, 0) + 1
        
        # Get recent activities (last 10)
        recent_docs = self.collection.order_by("timestamp", direction="DESCENDING").limit(10).get()
        for doc in recent_docs:
            activity = doc.to_dict()
            activity["id"] = doc.id
            stats["recent_activities"].append(activity)
        
        return stats
    
    async def search_activities(
        self,
        search_term: str,
        search_fields: Optional[list] = None,
        **filters
    ) -> Dict[str, Any]:
        """
        Search activities by text in specified fields
        
        Args:
            search_term: Term to search for
            search_fields: Fields to search in (default: description, additional_info)
            **filters: Additional filters to apply
            
        Returns:
            Dictionary with search results
        """
        # Get all activities and filter client-side for text search
        activities = await self.get_activities(**filters, limit=1000)
        
        if not search_fields:
            search_fields = ["description"]
        
        matching_activities = []
        search_term_lower = search_term.lower()
        
        for activity in activities["activities"]:
            found = False
            for field in search_fields:
                value = activity.get(field, "")
                if isinstance(value, dict):
                    # Search in nested dictionaries
                    for nested_value in value.values():
                        if isinstance(nested_value, str) and search_term_lower in nested_value.lower():
                            found = True
                            break
                elif isinstance(value, str) and search_term_lower in value.lower():
                    found = True
                    break
            
            if found:
                matching_activities.append(activity)
        
        return {
            "activities": matching_activities,
            "total_count": len(matching_activities),
            "search_term": search_term,
            "search_fields": search_fields
        }


# Dependency for automatic activity logging
class ActivityLogger:
    """Helper class for automatic activity logging"""
    
    def __init__(self, admin_id: str, ip_address: str = None, user_agent: str = None):
        self.admin_id = admin_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.model = AdminActivityModel()
    
    async def log(
        self,
        activity_type: AdminActivityType,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        description: str = "",
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        additional_info: Optional[Dict[str, Any]] = None,
        status: str = "completed"
    ) -> str:
        """Log activity with pre-filled admin info"""
        return await self.model.log_activity(
            admin_id=self.admin_id,
            activity_type=activity_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            old_data=old_data,
            new_data=new_data,
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            additional_info=additional_info,
            status=status
        )