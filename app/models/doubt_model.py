"""
Doubt Model for Firestore Database
Handles user questions/doubts, admin responses, and Q&A functionality
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.constants.statuses import DoubtStatus, QuestionCategory


class DoubtPriority(BaseModel):
    """Doubt priority classification"""
    level: str = Field("medium", description="Priority level")  # low, medium, high, urgent
    reasons: List[str] = Field(default_factory=list, description="Reasons for priority")
    auto_assigned: bool = Field(True, description="Whether priority was auto-assigned")
    admin_assigned: Optional[str] = Field(None, description="Admin who assigned priority")


class DoubtAssignment(BaseModel):
    """Doubt assignment to admins"""
    assigned_to: Optional[str] = Field(None, description="Admin UID assigned to handle doubt")
    assigned_by: Optional[str] = Field(None, description="Admin who assigned the doubt")
    assigned_at: Optional[datetime] = Field(None, description="Assignment timestamp")
    priority: DoubtPriority = Field(default_factory=DoubtPriority)
    estimated_response_time: Optional[int] = Field(None, description="Estimated response time in hours")
    tags: List[str] = Field(default_factory=list, description="Doubt tags/categories")


class DoubtResponse(BaseModel):
    """Response to user doubt"""
    response_id: str = Field("", description="Unique response ID")
    admin_uid: str = Field(..., description="Admin who responded")
    admin_name: str = Field(..., description="Admin name")
    response_text: str = Field(..., description="Response content")
    response_type: str = Field("answer", description="answer, clarification, followup, closing")
    
    # Response metadata
    helpful_votes: int = Field(0, ge=0)
    unhelpful_votes: int = Field(0, ge=0)
    user_feedback: Optional[str] = Field(None, description="User feedback on response")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('response_type')
    def validate_response_type(cls, v):
        if v not in ['answer', 'clarification', 'followup', 'closing']:
            raise ValueError('response_type must be one of: answer, clarification, followup, closing')
        return v


class UserDoubt(BaseModel):
    """User doubt/question structure"""
    doubt_id: str = Field("", description="Unique doubt ID")
    user_uid: str = Field(..., description="User Firebase UID")
    user_info: Dict[str, str] = Field(..., description="User basic info")
    
    # Question details
    question_title: str = Field(..., max_length=200, description="Question title")
    question_content: str = Field(..., max_length=2000, description="Question content")
    category: QuestionCategory = Field(default=QuestionCategory.GENERAL)
    subcategory: Optional[str] = Field(None, description="Specific subcategory")
    
    # Context information
    related_item_id: Optional[str] = Field(None, description="Related course/webinar ID")
    related_item_type: Optional[str] = Field(None, description="course, webinar, or None")
    chapter_id: Optional[str] = Field(None, description="Specific chapter/section")
    lesson_id: Optional[str] = Field(None, description="Specific lesson")
    
    # Attachment information
    has_attachment: bool = Field(False, description="Whether doubt has attachments")
    attachment_urls: List[str] = Field(default_factory=list, description="Attachment URLs")
    attachment_types: List[str] = Field(default_factory=list, description="Attachment file types")
    
    # Status and priority
    status: DoubtStatus = Field(default=QuestionCategory.GENERAL)
    assignment: DoubtAssignment = Field(default_factory=DoubtAssignment)
    
    # Responses
    responses: List[DoubtResponse] = Field(default_factory=list)
    is_resolved: bool = Field(False, description="Whether doubt is resolved")
    is_closed: bool = Field(False, description="Whether doubt is closed")
    
    # User interaction
    is_urgent: bool = Field(False, description="Marked as urgent by user")
    user_priority_reason: Optional[str] = Field(None, description="Reason for marking as urgent")
    views_count: int = Field(0, ge=0, description="Number of views")
    helpful_votes: int = Field(0, ge=0)
    unhelpful_votes: int = Field(0, ge=0)
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    language: Optional[str] = "en"
    tags: List[str] = Field(default_factory=list, description="Custom tags")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    @validator('related_item_type')
    def validate_related_item_type(cls, v):
        if v is not None and v not in ['course', 'webinar']:
            raise ValueError('related_item_type must be either "course" or "webinar"')
        return v
    
    @validator('question_title')
    def validate_question_title(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Question title must be at least 10 characters long')
        return v.strip()
    
    @validator('question_content')
    def validate_question_content(cls, v):
        if len(v.strip()) < 30:
            raise ValueError('Question content must be at least 30 characters long')
        return v.strip()


class DoubtResponseModel(BaseModel):
    """Response model for doubt operations"""
    success: bool
    message: str
    doubt_id: Optional[str] = None
    response_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class DoubtModel:
    """Doubt model for Firestore operations"""
    
    COLLECTION_NAME = "doubts"
    RESPONSE_COLLECTION = "doubt_responses"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
        self.response_collection = self.db.collection(self.RESPONSE_COLLECTION)
    
    async def create_doubt(
        self,
        user_uid: str,
        user_name: str,
        user_email: str,
        question_title: str,
        question_content: str,
        category: QuestionCategory = QuestionCategory.GENERAL,
        subcategory: Optional[str] = None,
        related_item_id: Optional[str] = None,
        related_item_type: Optional[str] = None,
        chapter_id: Optional[str] = None,
        lesson_id: Optional[str] = None,
        is_urgent: bool = False,
        user_priority_reason: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new user doubt
        
        Args:
            user_uid: User Firebase UID
            user_name: User name
            user_email: User email
            question_title: Question title
            question_content: Question content
            category: Question category
            subcategory: Optional subcategory
            related_item_id: Related course/webinar ID
            related_item_type: "course" or "webinar"
            chapter_id: Specific chapter
            lesson_id: Specific lesson
            is_urgent: Whether user marked as urgent
            user_priority_reason: Reason for urgency
            additional_data: Additional doubt data
            
        Returns:
            Doubt ID
        """
        user_info = {
            "name": user_name,
            "email": user_email
        }
        
        # Auto-assign priority based on question content and user marking
        priority = await self._calculate_priority(
            question_title, question_content, category, is_urgent
        )
        
        assignment = DoubtAssignment(priority=priority)
        
        doubt_data = UserDoubt(
            user_uid=user_uid,
            user_info=user_info,
            question_title=question_title,
            question_content=question_content,
            category=category,
            subcategory=subcategory,
            related_item_id=related_item_id,
            related_item_type=related_item_type,
            chapter_id=chapter_id,
            lesson_id=lesson_id,
            is_urgent=is_urgent,
            user_priority_reason=user_priority_reason,
            assignment=assignment,
            **additional_data
        )
        
        # Create doubt document
        doc_ref = self.collection.document()
        doubt_data.doubt_id = doc_ref.id
        
        doubt_dict = doubt_data.dict()
        
        # Convert datetime objects to ISO strings for Firestore
        for key, value in doubt_dict.items():
            if isinstance(value, datetime):
                doubt_dict[key] = value.isoformat()
            elif isinstance(value, list) and value and isinstance(value[0], datetime):
                doubt_dict[key] = [v.isoformat() if isinstance(v, datetime) else v for v in value]
        
        await doc_ref.set(doubt_dict)
        
        # Trigger notifications for urgent questions
        if is_urgent or priority.level in ['high', 'urgent']:
            await self._send_urgent_doubt_notification(doc_ref.id, doubt_data)
        
        return doc_ref.id
    
    async def get_doubt(self, doubt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get doubt by ID
        
        Args:
            doubt_id: Doubt ID
            
        Returns:
            Doubt data or None if not found
        """
        doc = self.collection.document(doubt_id).get()
        
        if doc.exists:
            doubt_data = doc.to_dict()
            doubt_data["doubt_id"] = doc.id
            return self._convert_datetime_strings(doubt_data)
        
        return None
    
    async def get_user_doubts(
        self,
        user_uid: str,
        status: Optional[DoubtStatus] = None,
        category: Optional[QuestionCategory] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's doubts
        
        Args:
            user_uid: User Firebase UID
            status: Filter by doubt status
            category: Filter by question category
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            List of doubts
        """
        query = self.collection.where("user_uid", "==", user_uid)
        
        if status:
            query = query.where("status", "==", status.value)
        
        if category:
            query = query.where("category", "==", category.value)
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        doubts_list = []
        for doc in docs:
            doubt_data = doc.to_dict()
            doubt_data["doubt_id"] = doc.id
            doubts_list.append(self._convert_datetime_strings(doubt_data))
        
        return doubts_list
    
    async def get_assigned_doubts(
        self,
        admin_uid: str,
        status: Optional[DoubtStatus] = None,
        priority_level: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "asc",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get doubts assigned to an admin
        
        Args:
            admin_uid: Admin Firebase UID
            status: Filter by doubt status
            priority_level: Filter by priority level
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            List of doubts
        """
        query = self.collection.where("assignment.assigned_to", "==", admin_uid)
        
        if status:
            query = query.where("status", "==", status.value)
        
        if priority_level:
            query = query.where("assignment.priority.level", "==", priority_level)
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        doubts_list = []
        for doc in docs:
            doubt_data = doc.to_dict()
            doubt_data["doubt_id"] = doc.id
            doubts_list.append(self._convert_datetime_strings(doubt_data))
        
        return doubts_list
    
    async def update_doubt(
        self,
        doubt_id: str,
        updates: Dict[str, Any],
        authorized_uid: str,
        is_admin: bool = False
    ) -> bool:
        """
        Update doubt
        
        Args:
            doubt_id: Doubt ID
            updates: Fields to update
            authorized_uid: User/admin UID making the update
            is_admin: Whether the updater is an admin
            
        Returns:
            True if successful
        """
        # Verify authorization
        doubt = await self.get_doubt(doubt_id)
        if not doubt:
            return False
        
        if not is_admin and doubt["user_uid"] != authorized_uid:
            return False
        
        # Restrict certain fields for non-admin users
        if not is_admin:
            restricted_fields = [
                "doubt_id", "user_uid", "user_info", "status", "assignment",
                "responses", "is_resolved", "is_closed", "helpful_votes",
                "unhelpful_votes", "created_at", "first_response_at",
                "resolved_at", "closed_at"
            ]
            
            for field in restricted_fields:
                updates.pop(field, None)
        
        updates["updated_at"] = datetime.utcnow()
        
        doc_ref = self.collection.document(doubt_id)
        await doc_ref.update(updates)
        
        return True
    
    async def assign_doubt(
        self,
        doubt_id: str,
        admin_uid: str,
        assigned_admin_uid: str,
        estimated_response_time: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Assign doubt to admin
        
        Args:
            doubt_id: Doubt ID
            admin_uid: Admin UID making the assignment
            assigned_admin_uid: Admin UID to assign to
            estimated_response_time: Estimated response time in hours
            tags: Doubt tags
            
        Returns:
            True if successful
        """
        updates = {
            "assignment": {
                "assigned_to": assigned_admin_uid,
                "assigned_by": admin_uid,
                "assigned_at": datetime.utcnow(),
                "priority": {
                    "level": "medium",
                    "reasons": [],
                    "auto_assigned": True
                },
                "estimated_response_time": estimated_response_time,
                "tags": tags or []
            },
            "updated_at": datetime.utcnow()
        }
        
        doc_ref = self.collection.document(doubt_id)
        await doc_ref.update(updates)
        
        return True
    
    async def add_response(
        self,
        doubt_id: str,
        admin_uid: str,
        admin_name: str,
        response_text: str,
        response_type: str = "answer"
    ) -> str:
        """
        Add response to doubt
        
        Args:
            doubt_id: Doubt ID
            admin_uid: Admin Firebase UID
            admin_name: Admin name
            response_text: Response content
            response_type: Type of response
            
        Returns:
            Response ID
        """
        doubt = await self.get_doubt(doubt_id)
        if not doubt:
            raise ValueError("Doubt not found")
        
        # Create response object
        response = DoubtResponse(
            admin_uid=admin_uid,
            admin_name=admin_name,
            response_text=response_text,
            response_type=response_type
        )
        
        # Add response to doubt
        current_responses = doubt.get("responses", [])
        current_responses.append(response.dict())
        
        updates = {
            "responses": current_responses,
            "updated_at": datetime.utcnow()
        }
        
        # Set first response time if this is the first response
        if not doubt.get("first_response_at"):
            updates["first_response_at"] = datetime.utcnow()
        
        doc_ref = self.collection.document(doubt_id)
        await doc_ref.update(updates)
        
        # Send notification to user
        await self._send_response_notification(doubt_id, doubt, response)
        
        return f"response_{datetime.utcnow().timestamp()}"
    
    async def vote_response_helpful(
        self,
        doubt_id: str,
        response_index: int,
        voter_uid: str,
        is_helpful: bool
    ) -> bool:
        """
        vote if response is helpful or not
        
        Args:
            doubt_id: Doubt ID
            response_index: Index of response in responses array
            voter_uid: User who is voting
            is_helpful: Whether vote is helpful (True) or not (False)
            
        Returns:
            True if successful
        """
        # Check if user has already voted on this response
        votes_collection = self.collection.document(doubt_id).collection("response_votes")
        vote_doc = votes_collection.document(f"{response_index}_{voter_uid}").get()
        
        if vote_doc.exists:
            return False  # User has already voted
        
        # Add vote
        vote_data = {
            "response_index": response_index,
            "is_helpful": is_helpful,
            "voted_at": datetime.utcnow()
        }
        await votes_collection.document(f"{response_index}_{voter_uid}").set(vote_data)
        
        # Update response vote counts
        doubt_doc = self.collection.document(doubt_id).get()
        if doubt_doc.exists:
            doubt_data = doubt_doc.to_dict()
            responses = doubt_data.get("responses", [])
            
            if 0 <= response_index < len(responses):
                if is_helpful:
                    responses[response_index]["helpful_votes"] += 1
                else:
                    responses[response_index]["unhelpful_votes"] += 1
                
                responses[response_index]["updated_at"] = datetime.utcnow()
                
                await doubt_doc.reference.update({"responses": responses})
        
        return True
    
    async def mark_as_resolved(
        self,
        doubt_id: str,
        admin_uid: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Mark doubt as resolved
        
        Args:
            doubt_id: Doubt ID
            admin_uid: Admin UID
            resolution_notes: Optional resolution notes
            
        Returns:
            True if successful
        """
        updates = {
            "status": DoubtStatus.RESOLVED.value,
            "is_resolved": True,
            "resolved_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if resolution_notes:
            updates["resolution_notes"] = resolution_notes
        
        doc_ref = self.collection.document(doubt_id)
        await doc_ref.update(updates)
        
        # Send resolution notification
        await self._send_resolution_notification(doubt_id, admin_uid)
        
        return True
    
    async def close_doubt(
        self,
        doubt_id: str,
        admin_uid: str,
        close_reason: Optional[str] = None
    ) -> bool:
        """
        Close doubt (final status)
        
        Args:
            doubt_id: Doubt ID
            admin_uid: Admin UID
            close_reason: Reason for closing
            
        Returns:
            True if successful
        """
        updates = {
            "status": DoubtStatus.CLOSED.value,
            "is_closed": True,
            "closed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if close_reason:
            updates["close_reason"] = close_reason
        
        doc_ref = self.collection.document(doubt_id)
        await doc_ref.update(updates)
        
        return True
    
    async def search_doubts(
        self,
        search_term: str = "",
        user_uid: str = "",
        status: Optional[DoubtStatus] = None,
        category: Optional[QuestionCategory] = None,
        priority_level: str = "",
        related_item_id: str = "",
        is_urgent: Optional[bool] = None,
        is_resolved: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        assigned_to: str = "",
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search doubts with filters
        
        Args:
            search_term: Search term for question content/title
            user_uid: Filter by user
            status: Filter by doubt status
            category: Filter by question category
            priority_level: Filter by priority level
            related_item_id: Filter by related item
            is_urgent: Filter by urgency
            is_resolved: Filter by resolution status
            start_date: Filter by start date
            end_date: Filter by end date
            assigned_to: Filter by assigned admin
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            Dictionary with doubts and pagination info
        """
        query = self.collection
        
        # Apply filters
        if user_uid:
            query = query.where("user_uid", "==", user_uid)
        
        if status:
            query = query.where("status", "==", status.value)
        
        if category:
            query = query.where("category", "==", category.value)
        
        if priority_level:
            query = query.where("assignment.priority.level", "==", priority_level)
        
        if related_item_id:
            query = query.where("related_item_id", "==", related_item_id)
        
        if is_urgent is not None:
            query = query.where("is_urgent", "==", is_urgent)
        
        if is_resolved is not None:
            query = query.where("is_resolved", "==", is_resolved)
        
        if assigned_to:
            query = query.where("assignment.assigned_to", "==", assigned_to)
        
        if start_date:
            query = query.where("created_at", ">=", start_date.isoformat())
        
        if end_date:
            query = query.where("created_at", "<=", end_date.isoformat())
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        doubts_list = []
        for doc in docs:
            doubt_data = doc.to_dict()
            doubt_data["doubt_id"] = doc.id
            
            # Apply search term filter (for text content)
            if search_term:
                search_fields = [
                    doubt_data.get("question_title", ""),
                    doubt_data.get("question_content", ""),
                    doubt_data.get("user_info", {}).get("name", "")
                ]
                
                if not any(search_term.lower() in field.lower() for field in search_fields if field):
                    continue
            
            doubts_list.append(self._convert_datetime_strings(doubt_data))
        
        # Get total count for pagination
        count_query = self.collection
        if status:
            count_query = count_query.where("status", "==", status.value)
        if category:
            count_query = count_query.where("category", "==", category.value)
        
        total_count = len(count_query.get())
        
        return {
            "doubts": doubts_list,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_doubt_statistics(self, admin_uid: Optional[str] = None) -> Dict[str, Any]:
        """
        Get doubt statistics
        
        Args:
            admin_uid: Optional admin UID to get statistics for assigned doubts
            
        Returns:
            Statistics data
        """
        query = self.collection
        
        if admin_uid:
            query = query.where("assignment.assigned_to", "==", admin_uid)
        
        docs = query.get()
        
        stats = {
            "total_doubts": 0,
            "pending_doubts": 0,
            "resolved_doubts": 0,
            "closed_doubts": 0,
            "urgent_doubts": 0,
            "avg_response_time": 0.0,
            "avg_resolution_time": 0.0,
            "category_breakdown": {},
            "priority_breakdown": {},
            "assigned_to_breakdown": {}
        }
        
        response_times = []
        resolution_times = []
        
        for doc in docs:
            doubt_data = doc.to_dict()
            stats["total_doubts"] += 1
            
            # Count by status
            status = doubt_data.get("status", "")
            if status == DoubtStatus.PENDING.value:
                stats["pending_doubts"] += 1
            elif status == DoubtStatus.RESOLVED.value:
                stats["resolved_doubts"] += 1
            elif status == DoubtStatus.CLOSED.value:
                stats["closed_doubts"] += 1
            
            # Count urgent
            if doubt_data.get("is_urgent", False):
                stats["urgent_doubts"] += 1
            
            # Category breakdown
            category = doubt_data.get("category", QuestionCategory.GENERAL.value)
            stats["category_breakdown"][category] = stats["category_breakdown"].get(category, 0) + 1
            
            # Priority breakdown
            priority_level = doubt_data.get("assignment", {}).get("priority", {}).get("level", "medium")
            stats["priority_breakdown"][priority_level] = stats["priority_breakdown"].get(priority_level, 0) + 1
            
            # Assignment breakdown
            assigned_to = doubt_data.get("assignment", {}).get("assigned_to", "unassigned")
            stats["assigned_to_breakdown"][assigned_to] = stats["assigned_to_breakdown"].get(assigned_to, 0) + 1
            
            # Calculate response and resolution times
            created_at = doubt_data.get("created_at")
            first_response_at = doubt_data.get("first_response_at")
            resolved_at = doubt_data.get("resolved_at")
            
            if created_at:
                created_time = self._parse_datetime(created_at)
                if first_response_at:
                    first_response_time = self._parse_datetime(first_response_at)
                    if created_time and first_response_time:
                        response_times.append((first_response_time - created_time).total_seconds() / 3600)  # hours
                
                if resolved_at:
                    resolved_time = self._parse_datetime(resolved_at)
                    if created_time and resolved_time:
                        resolution_times.append((resolved_time - created_time).total_seconds() / 3600)  # hours
        
        # Calculate averages
        if response_times:
            stats["avg_response_time"] = round(sum(response_times) / len(response_times), 2)
        
        if resolution_times:
            stats["avg_resolution_time"] = round(sum(resolution_times) / len(resolution_times), 2)
        
        return stats
    
    async def _calculate_priority(
        self,
        question_title: str,
        question_content: str,
        category: QuestionCategory,
        is_urgent: bool
    ) -> DoubtPriority:
        """
        Calculate doubt priority based on content and category
        
        Args:
            question_title: Question title
            question_content: Question content
            category: Question category
            is_urgent: Whether user marked as urgent
            
        Returns:
            DoubtPriority object
        """
        priority = "medium"
        reasons = []
        
        # User-marked urgent gets highest priority
        if is_urgent:
            priority = "urgent"
            reasons.append("marked_urgent_by_user")
        
        # Category-based priority
        high_priority_categories = [
            QuestionCategory.BILLING,
            QuestionCategory.TECHNICAL,
            QuestionCategory.ACCOUNT
        ]
        
        if category in high_priority_categories:
            if priority != "urgent":
                priority = "high"
            reasons.append(f"category_{category.value}")
        
        # Content analysis for urgency indicators
        urgent_keywords = ["error", "urgent", "critical", "not working", "broken", "failed", "crash"]
        question_text = (question_title + " " + question_content).lower()
        
        urgent_count = sum(1 for keyword in urgent_keywords if keyword in question_text)
        if urgent_count >= 2 and priority != "urgent":
            priority = "high"
            reasons.append("urgent_keywords_detected")
        
        return DoubtPriority(level=priority, reasons=reasons, auto_assigned=True)
    
    async def _send_urgent_doubt_notification(self, doubt_id: str, doubt_data: UserDoubt):
        """
        Send notification for urgent doubts
        
        Args:
            doubt_id: Doubt ID
            doubt_data: Doubt data
        """
        # Implementation would integrate with email/notification service
        # This is a placeholder for the notification logic
        pass
    
    async def _send_response_notification(self, doubt_id: str, doubt_data: Dict[str, Any], response: DoubtResponse):
        """
        Send notification when admin responds to doubt
        
        Args:
            doubt_id: Doubt ID
            doubt_data: Doubt data
            response: Response data
        """
        # Implementation would integrate with email/notification service
        # This is a placeholder for the notification logic
        pass
    
    async def _send_resolution_notification(self, doubt_id: str, admin_uid: str):
        """
        Send notification when doubt is resolved
        
        Args:
            doubt_id: Doubt ID
            admin_uid: Admin UID
        """
        # Implementation would integrate with email/notification service
        # This is a placeholder for the notification logic
        pass
    
    def _convert_datetime_strings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert datetime strings back to datetime objects
        
        Args:
            data: Dictionary with datetime strings
            
        Returns:
            Dictionary with datetime objects
        """
        for key, value in data.items():
            if isinstance(value, str) and value.endswith('Z'):
                try:
                    data[key] = self._parse_datetime(value)
                except (ValueError, AttributeError):
                    pass
            elif isinstance(value, list):
                # Handle list of datetime strings
                new_list = []
                for item in value:
                    if isinstance(item, str) and item.endswith('Z'):
                        try:
                            new_list.append(self._parse_datetime(item))
                        except (ValueError, AttributeError):
                            new_list.append(item)
                    else:
                        new_list.append(item)
                data[key] = new_list
        
        return data
    
    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Parse datetime string to datetime object
        
        Args:
            datetime_str: ISO format datetime string
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None


# Helper functions for doubt operations
def create_doubt_assignment(
    assigned_to: str,
    assigned_by: str,
    priority_level: str = "medium",
    estimated_response_time: Optional[int] = None,
    tags: Optional[List[str]] = None
) -> DoubtAssignment:
    """
    Create doubt assignment
    
    Args:
        assigned_to: Admin UID to assign to
        assigned_by: Admin UID making assignment
        priority_level: Priority level
        estimated_response_time: Estimated response time in hours
        tags: Doubt tags
        
    Returns:
        DoubtAssignment object
    """
    priority = DoubtPriority(level=priority_level, reasons=[], auto_assigned=False)
    
    return DoubtAssignment(
        assigned_to=assigned_to,
        assigned_by=assigned_by,
        assigned_at=datetime.utcnow(),
        priority=priority,
        estimated_response_time=estimated_response_time,
        tags=tags or []
    )


def create_doubt_response(
    admin_uid: str,
    admin_name: str,
    response_text: str,
    response_type: str = "answer"
) -> DoubtResponse:
    """
    Create doubt response
    
    Args:
        admin_uid: Admin UID
        admin_name: Admin name
        response_text: Response content
        response_type: Type of response
        
    Returns:
        DoubtResponse object
    """
    return DoubtResponse(
        admin_uid=admin_uid,
        admin_name=admin_name,
        response_text=response_text,
        response_type=response_type
    )