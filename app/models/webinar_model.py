"""
Webinar Model for Firestore Database
Handles webinar creation, scheduling, and attendee management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.constants.statuses import WebinarStatus


class WebinarHost(BaseModel):
    """Webinar host information"""
    uid: str
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    credentials: List[str] = []
    is_primary: bool = True


class WebinarAgenda(BaseModel):
    """Webinar agenda item"""
    title: str
    description: Optional[str] = None
    duration_minutes: int
    start_time_offset: int  # Minutes from webinar start
    order: int


class WebinarRecording(BaseModel):
    """Webinar recording information"""
    recording_url: Optional[str] = None
    recording_duration_minutes: Optional[int] = None
    recording_size_mb: Optional[float] = None
    is_available: bool = False
    download_allowed: bool = False
    expires_at: Optional[datetime] = None


class WebinarResource(BaseModel):
    """Webinar resource/material"""
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size_mb: Optional[float] = None
    is_downloadable: bool = True
    order: int


class WebinarRegistration(BaseModel):
    """Webinar registration details"""
    registration_id: str
    user_uid: str
    user_email: str
    user_name: str
    registered_at: datetime
    reminder_sent: bool = False
    attended: bool = False
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    feedback_submitted: bool = False
    recording_access_granted: bool = False


class WebinarPricing(BaseModel):
    """Webinar pricing structure"""
    price: float = 0.0
    currency: str = "USD"
    discount_price: Optional[float] = None
    discount_valid_until: Optional[datetime] = None
    is_free: bool = True
    early_bird_price: Optional[float] = None
    early_bird_deadline: Optional[datetime] = None


class WebinarModel:
    """Webinar model for Firestore operations"""
    
    COLLECTION_NAME = "webinars"
    REGISTRATION_COLLECTION = "webinar_registrations"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
        self.registration_collection = self.db.collection(self.REGISTRATION_COLLECTION)
    
    def create_webinar_data(
        self,
        title: str,
        description: str,
        host_uid: str,
        host_name: str,
        start_time: datetime,
        duration_minutes: int = 60,
        max_attendees: Optional[int] = None,
        price: float = 0.0,
        is_free: bool = True,
        category: str = "",
        status: WebinarStatus = WebinarStatus.DRAFT,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create webinar data structure
        
        Args:
            title: Webinar title
            description: Webinar description
            host_uid: Firebase UID of host
            host_name: Host name
            start_time: Webinar start time
            duration_minutes: Duration in minutes
            max_attendees: Maximum number of attendees
            price: Webinar price
            is_free: Whether webinar is free
            category: Webinar category
            status: Webinar status
            additional_data: Additional webinar data
            
        Returns:
            Dictionary with webinar data
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        webinar_data = {
            "id": "",  # Will be set when created
            "title": title,
            "slug": self._generate_slug(title),
            "description": description,
            "short_description": description[:200] + "..." if len(description) > 200 else description,
            "host": {
                "uid": host_uid,
                "name": host_name,
                "bio": "",
                "avatar_url": None,
                "credentials": [],
                "is_primary": True
            },
            "category": category,
            "status": status.value,
            "timing": {
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
                "timezone": "UTC",
                "is_recurring": False,
                "recurrence_pattern": None
            },
            "settings": {
                "max_attendees": max_attendees,
                "allow_chat": True,
                "allow_screen_share": True,
                "record_webinar": True,
                "require_registration": True,
                "send_reminders": True,
                "is_public": status != WebinarStatus.PRIVATE,
                "approval_required": False
            },
            "pricing": {
                "price": price,
                "currency": "USD",
                "discount_price": None,
                "discount_valid_until": None,
                "is_free": is_free,
                "early_bird_price": None,
                "early_bird_deadline": None
            },
            "agenda": {
                "total_items": 0,
                "items": [],
                "estimated_duration": duration_minutes
            },
            "media": {
                "thumbnail_url": None,
                "cover_image_url": None,
                "preview_video_url": None,
                "slides_url": None
            },
            "recording": {
                "recording_url": None,
                "recording_duration_minutes": None,
                "recording_size_mb": None,
                "is_available": False,
                "download_allowed": False,
                "expires_at": None
            },
            "resources": [],
            "stats": {
                "registered_attendees": 0,
                "attended_count": 0,
                "completion_rate": 0.0,
                "average_rating": 0.0,
                "total_ratings": 0,
                "total_reviews": 0,
                "total_revenue": 0.0,
                "no_show_count": 0
            },
            "registration": {
                "is_open": True,
                "closes_at": start_time - timedelta(hours=1),  # Close 1 hour before
                "approval_required": False,
                "auto_approve": True
            },
            "seo": {
                "meta_title": title,
                "meta_description": description[:160],
                "tags": [],
                "keywords": []
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "published_at": None if status != WebinarStatus.PUBLISHED else datetime.utcnow(),
            "metadata": {}
        }
        
        if additional_data:
            webinar_data["metadata"].update(additional_data)
        
        return webinar_data
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        return slug
    
    async def create_webinar(
        self,
        title: str,
        description: str,
        host_uid: str,
        host_name: str,
        start_time: datetime,
        duration_minutes: int = 60,
        max_attendees: Optional[int] = None,
        price: float = 0.0,
        is_free: bool = True,
        category: str = "",
        status: WebinarStatus = WebinarStatus.DRAFT,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new webinar
        
        Args:
            title: Webinar title
            description: Webinar description
            host_uid: Firebase UID of host
            host_name: Host name
            start_time: Webinar start time
            duration_minutes: Duration in minutes
            max_attendees: Maximum number of attendees
            price: Webinar price
            is_free: Whether webinar is free
            category: Webinar category
            status: Webinar status
            additional_data: Additional webinar data
            
        Returns:
            Webinar ID
        """
        webinar_data = self.create_webinar_data(
            title, description, host_uid, host_name, start_time, 
            duration_minutes, max_attendees, price, is_free, category, status, additional_data
        )
        
        # Create webinar document
        doc_ref = self.collection.document()
        webinar_data["id"] = doc_ref.id
        
        await doc_ref.set(webinar_data)
        
        return doc_ref.id
    
    async def get_webinar(self, webinar_id: str) -> Optional[Dict[str, Any]]:
        """
        Get webinar by ID
        
        Args:
            webinar_id: Webinar ID
            
        Returns:
            Webinar data or None if not found
        """
        doc = self.collection.document(webinar_id).get()
        
        if doc.exists:
            webinar_data = doc.to_dict()
            webinar_data["id"] = doc.id
            return webinar_data
        
        return None
    
    async def get_webinar_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get webinar by slug
        
        Args:
            slug: Webinar slug
            
        Returns:
            Webinar data or None if not found
        """
        query = self.collection.where("slug", "==", slug).limit(1)
        docs = query.get()
        
        for doc in docs:
            webinar_data = doc.to_dict()
            webinar_data["id"] = doc.id
            return webinar_data
        
        return None
    
    async def update_webinar(
        self,
        webinar_id: str,
        updates: Dict[str, Any],
        update_timestamps: bool = True
    ) -> bool:
        """
        Update webinar data
        
        Args:
            webinar_id: Webinar ID
            updates: Fields to update
            update_timestamps: Whether to update timestamps
            
        Returns:
            True if successful
        """
        if update_timestamps:
            updates["updated_at"] = datetime.utcnow()
        
        # Generate new slug if title changed
        if "title" in updates and updates["title"]:
            updates["slug"] = self._generate_slug(updates["title"])
        
        # Update end time if duration changed
        if "timing" in updates and "duration_minutes" in updates["timing"]:
            timing = updates["timing"]
            if "start_time" in timing:
                from datetime import timedelta
                end_time = timing["start_time"] + timedelta(minutes=timing["duration_minutes"])
                timing["end_time"] = end_time
        
        # Clean up None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        if not updates:
            return False
        
        doc_ref = self.collection.document(webinar_id)
        await doc_ref.update(updates)
        
        return True
    
    async def update_webinar_status(self, webinar_id: str, status: WebinarStatus) -> bool:
        """
        Update webinar status
        
        Args:
            webinar_id: Webinar ID
            status: New webinar status
            
        Returns:
            True if successful
        """
        updates = {
            "status": status.value,
            "settings.is_public": status != WebinarStatus.PRIVATE
        }
        
        if status == WebinarStatus.PUBLISHED:
            updates["published_at"] = datetime.utcnow()
        
        return await self.update_webinar(webinar_id, updates, update_timestamps=False)
    
    async def add_agenda_item(self, webinar_id: str, agenda_item: WebinarAgenda) -> bool:
        """
        Add agenda item to webinar
        
        Args:
            webinar_id: Webinar ID
            agenda_item: Agenda item to add
            
        Returns:
            True if successful
        """
        doc = self.collection.document(webinar_id).get()
        
        if not doc.exists:
            raise ValueError("Webinar not found")
        
        webinar_data = doc.to_dict()
        agenda_items = webinar_data.get("agenda", {}).get("items", [])
        
        # Add agenda item and set order
        agenda_dict = agenda_item.dict()
        agenda_dict["order"] = len(agenda_items) + 1
        
        agenda_items.append(agenda_dict)
        
        # Update agenda stats
        total_items = len(agenda_items)
        total_duration = sum(item.get("duration_minutes", 0) for item in agenda_items)
        
        updates = {
            "agenda.items": agenda_items,
            "agenda.total_items": total_items,
            "agenda.estimated_duration": total_duration
        }
        
        return await self.update_webinar(webinar_id, updates, update_timestamps=False)
    
    async def add_resource(self, webinar_id: str, resource: WebinarResource) -> bool:
        """
        Add resource to webinar
        
        Args:
            webinar_id: Webinar ID
            resource: Resource to add
            
        Returns:
            True if successful
        """
        doc = self.collection.document(webinar_id).get()
        
        if not doc.exists:
            raise ValueError("Webinar not found")
        
        webinar_data = doc.to_dict()
        resources = webinar_data.get("resources", [])
        
        # Add resource and set order
        resource_dict = resource.dict()
        resource_dict["order"] = len(resources) + 1
        
        resources.append(resource_dict)
        
        return await self.update_webinar(webinar_id, {"resources": resources}, update_timestamps=False)
    
    async def update_recording(self, webinar_id: str, recording_data: Dict[str, Any]) -> bool:
        """
        Update webinar recording information
        
        Args:
            webinar_id: Webinar ID
            recording_data: Recording data to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(webinar_id).get()
        
        if not doc.exists:
            raise ValueError("Webinar not found")
        
        current_webinar = doc.to_dict()
        current_recording = current_webinar.get("recording", {})
        
        # Merge with existing recording
        updated_recording = {**current_recording, **recording_data}
        
        return await self.update_webinar(webinar_id, {"recording": updated_recording}, update_timestamps=False)
    
    async def delete_webinar(self, webinar_id: str, soft_delete: bool = True) -> bool:
        """
        Delete webinar
        
        Args:
            webinar_id: Webinar ID
            soft_delete: Whether to soft delete
            
        Returns:
            True if successful
        """
        if soft_delete:
            # Soft delete - mark as deleted
            updates = {
                "status": WebinarStatus.CANCELLED.value,
                "settings.is_public": False,
                "cancelled_at": datetime.utcnow()
            }
            return await self.update_webinar(webinar_id, updates, update_timestamps=False)
        else:
            # Hard delete
            await self.collection.document(webinar_id).delete()
            return True
    
    async def register_for_webinar(
        self,
        webinar_id: str,
        user_uid: str,
        user_email: str,
        user_name: str
    ) -> str:
        """
        Register user for webinar
        
        Args:
            webinar_id: Webinar ID
            user_uid: User Firebase UID
            user_email: User email
            user_name: User name
            
        Returns:
            Registration ID
        """
        # Check if already registered
        existing_registration = await self.get_user_registration(webinar_id, user_uid)
        if existing_registration:
            raise ValueError("User already registered for this webinar")
        
        # Check webinar capacity
        webinar = await self.get_webinar(webinar_id)
        if not webinar:
            raise ValueError("Webinar not found")
        
        registered_count = await self.get_registration_count(webinar_id)
        max_attendees = webinar.get("settings", {}).get("max_attendees")
        
        if max_attendees and registered_count >= max_attendees:
            raise ValueError("Webinar is full")
        
        # Create registration
        registration_data = WebinarRegistration(
            registration_id="",
            user_uid=user_uid,
            user_email=user_email,
            user_name=user_name,
            registered_at=datetime.utcnow(),
            reminder_sent=False,
            attended=False,
            recording_access_granted=False
        )
        
        doc_ref = self.registration_collection.document()
        registration_data.registration_id = doc_ref.id
        
        await doc_ref.set(registration_data.dict())
        
        # Update webinar stats
        await self.update_webinar_stats(webinar_id, {"stats.registered_attendees": 1})
        
        return doc_ref.id
    
    async def get_user_registration(self, webinar_id: str, user_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user's registration for a webinar
        
        Args:
            webinar_id: Webinar ID
            user_uid: User Firebase UID
            
        Returns:
            Registration data or None
        """
        query = self.registration_collection \
            .where("user_uid", "==", user_uid) \
            .where("webinar_id", "==", webinar_id) \
            .limit(1)
        
        docs = query.get()
        
        for doc in docs:
            registration_data = doc.to_dict()
            registration_data["registration_id"] = doc.id
            return registration_data
        
        return None
    
    async def get_registration_count(self, webinar_id: str) -> int:
        """
        Get total registration count for webinar
        
        Args:
            webinar_id: Webinar ID
            
        Returns:
            Number of registrations
        """
        query = self.registration_collection.where("webinar_id", "==", webinar_id)
        docs = query.get()
        
        return len(docs)
    
    async def get_webinar_registrations(
        self,
        webinar_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get registrations for webinar
        
        Args:
            webinar_id: Webinar ID
            limit: Results limit
            offset: Results offset
            
        Returns:
            List of registrations
        """
        query = self.registration_collection \
            .where("webinar_id", "==", webinar_id) \
            .order_by("registered_at", direction="DESCENDING")
        
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        registrations = []
        for doc in docs:
            registration_data = doc.to_dict()
            registration_data["registration_id"] = doc.id
            registrations.append(registration_data)
        
        return registrations
    
    async def mark_attendance(
        self,
        webinar_id: str,
        user_uid: str,
        joined_at: Optional[datetime] = None,
        left_at: Optional[datetime] = None
    ) -> bool:
        """
        Mark user attendance for webinar
        
        Args:
            webinar_id: Webinar ID
            user_uid: User Firebase UID
            joined_at: When user joined
            left_at: When user left
            
        Returns:
            True if successful
        """
        registration = await self.get_user_registration(webinar_id, user_uid)
        if not registration:
            return False
        
        updates = {
            "attended": True,
            "joined_at": joined_at or datetime.utcnow()
        }
        
        if left_at:
            updates["left_at"] = left_at
        
        await self.registration_collection.document(registration["registration_id"]).update(updates)
        
        # Update webinar attendance stats
        await self.update_webinar_stats(webinar_id, {
            "stats.attended_count": 1
        })
        
        return True
    
    async def update_webinar_stats(self, webinar_id: str, stats_updates: Dict[str, Any]) -> bool:
        """
        Update webinar statistics
        
        Args:
            webinar_id: Webinar ID
            stats_updates: Stats to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(webinar_id).get()
        
        if not doc.exists:
            return False
        
        current_webinar = doc.to_dict()
        current_stats = current_webinar.get("stats", {})
        
        # Handle numeric updates
        updated_stats = current_stats.copy()
        for key, value in stats_updates.items():
            if key.startswith("stats.") and isinstance(current_stats.get(key.replace("stats.", "")), (int, float)):
                stats_key = key.replace("stats.", "")
                if isinstance(value, (int, float)):
                    updated_stats[stats_key] = current_stats.get(stats_key, 0) + value
                else:
                    updated_stats[stats_key] = value
            else:
                updated_stats[key.replace("stats.", "")] = value
        
        return await self.update_webinar(webinar_id, {"stats": updated_stats})
    
    async def search_webinars(
        self,
        search_term: str = "",
        category: str = "",
        host_uid: str = "",
        status: Optional[WebinarStatus] = None,
        is_free: Optional[bool] = None,
        upcoming_only: bool = True,
        sort_by: str = "start_time",
        sort_order: str = "asc",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search webinars with filters
        
        Args:
            search_term: Search term for title/description
            category: Filter by category
            host_uid: Filter by host
            status: Filter by status
            is_free: Filter by free/paid
            upcoming_only: Only show upcoming webinars
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            Dictionary with webinars and pagination info
        """
        query = self.collection
        
        # Apply filters
        if status:
            query = query.where("status", "==", status.value)
        else:
            # Default to published webinars only
            query = query.where("status", "==", WebinarStatus.PUBLISHED.value)
        
        if host_uid:
            query = query.where("host.uid", "==", host_uid)
        
        if is_free is not None:
            query = query.where("pricing.is_free", "==", is_free)
        
        if upcoming_only:
            # Only show future webinars
            query = query.where("timing.start_time", ">", datetime.utcnow())
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        
        if sort_by == "price":
            query = query.order_by("pricing.price", direction=direction)
        elif sort_by == "rating":
            query = query.order_by("stats.average_rating", direction=direction)
        elif sort_by == "popularity":
            query = query.order_by("stats.registered_attendees", direction=direction)
        else:
            query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        webinars = []
        for doc in docs:
            webinar_data = doc.to_dict()
            webinar_data["id"] = doc.id
            
            # Apply additional filters
            skip = False
            
            # Category filter
            if category and webinar_data.get("category") != category:
                skip = True
            
            # Search term filter
            if search_term and not skip:
                search_fields = [
                    webinar_data.get("title", ""),
                    webinar_data.get("description", ""),
                    webinar_data.get("short_description", "")
                ]
                
                if not any(search_term.lower() in field.lower() for field in search_fields if field):
                    skip = True
            
            if not skip:
                webinars.append(webinar_data)
        
        # Get total count for pagination
        count_query = self.collection
        if status:
            count_query = count_query.where("status", "==", status.value)
        else:
            count_query = count_query.where("status", "==", WebinarStatus.PUBLISHED.value)
        
        if upcoming_only:
            count_query = count_query.where("timing.start_time", ">", datetime.utcnow())
        
        total_count = len(count_query.get())
        
        return {
            "webinars": webinars,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_upcoming_webinars(
        self,
        limit: int = 10,
        host_uid: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming webinars
        
        Args:
            limit: Number of webinars to return
            host_uid: Filter by specific host
            
        Returns:
            List of upcoming webinars
        """
        query = self.collection \
            .where("status", "==", WebinarStatus.PUBLISHED.value) \
            .where("timing.start_time", ">", datetime.utcnow()) \
            .order_by("timing.start_time", direction="ASCENDING") \
            .limit(limit)
        
        if host_uid:
            query = query.where("host.uid", "==", host_uid)
        
        docs = query.get()
        webinars = []
        
        for doc in docs:
            webinar_data = doc.to_dict()
            webinar_data["id"] = doc.id
            webinars.append(webinar_data)
        
        return webinars
    
    async def get_webinars_by_host(self, host_uid: str) -> List[Dict[str, Any]]:
        """
        Get all webinars by host
        
        Args:
            host_uid: Firebase UID of host
            
        Returns:
            List of webinars by host
        """
        query = self.collection.where("host.uid", "==", host_uid)
        docs = query.get()
        
        webinars = []
        for doc in docs:
            webinar_data = doc.to_dict()
            webinar_data["id"] = doc.id
            webinars.append(webinar_data)
        
        return webinars
    
    async def get_webinar_statistics(self) -> Dict[str, Any]:
        """
        Get overall webinar statistics
        
        Returns:
            Dictionary with webinar statistics
        """
        docs = self.collection.get()
        
        stats = {
            "total_webinars": 0,
            "webinars_by_status": {},
            "webinars_by_category": {},
            "total_registered_attendees": 0,
            "total_attended": 0,
            "total_revenue": 0.0,
            "average_rating": 0.0,
            "published_webinars": 0,
            "upcoming_webinars": 0,
            "live_webinars": 0
        }
        
        total_rating_sum = 0
        total_rating_count = 0
        now = datetime.utcnow()
        
        for doc in docs:
            webinar_data = doc.to_dict()
            stats["total_webinars"] += 1
            
            # Count by status
            status = webinar_data.get("status", "unknown")
            stats["webinars_by_status"][status] = stats["webinars_by_status"].get(status, 0) + 1
            
            if status == WebinarStatus.PUBLISHED.value:
                stats["published_webinars"] += 1
            
            # Count by category
            category = webinar_data.get("category", "unknown")
            stats["webinars_by_category"][category] = stats["webinars_by_category"].get(category, 0) + 1
            
            # Check timing
            timing = webinar_data.get("timing", {})
            start_time = timing.get("start_time")
            end_time = timing.get("end_time")
            
            if start_time and end_time:
                if start_time <= now <= end_time:
                    stats["live_webinars"] += 1
                elif start_time > now:
                    stats["upcoming_webinars"] += 1
            
            # Aggregate stats
            webinar_stats = webinar_data.get("stats", {})
            stats["total_registered_attendees"] += webinar_stats.get("registered_attendees", 0)
            stats["total_attended"] += webinar_stats.get("attended_count", 0)
            stats["total_revenue"] += webinar_stats.get("total_revenue", 0.0)
            
            # Calculate average rating
            avg_rating = webinar_stats.get("average_rating", 0.0)
            rating_count = webinar_stats.get("total_ratings", 0)
            
            if avg_rating > 0 and rating_count > 0:
                total_rating_sum += avg_rating * rating_count
                total_rating_count += rating_count
        
        if total_rating_count > 0:
            stats["average_rating"] = total_rating_sum / total_rating_count
        
        return stats


# Dependency for webinar operations
class WebinarDependency:
    """Helper class for webinar-related dependencies"""
    
    def __init__(self):
        self.model = WebinarModel()
    
    async def get_webinar_or_404(self, webinar_id: str) -> Dict[str, Any]:
        """Get webinar or raise exception"""
        webinar = await self.model.get_webinar(webinar_id)
        
        if not webinar:
            raise ValueError("Webinar not found")
        
        return webinar
    
    async def require_published_webinar(self, webinar_id: str) -> Dict[str, Any]:
        """Require published webinar"""
        webinar = await self.get_webinar_or_404(webinar_id)
        
        if webinar.get("status") != WebinarStatus.PUBLISHED.value:
            raise ValueError("Webinar is not published")
        
        return webinar