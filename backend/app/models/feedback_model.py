"""
Feedback Model for Firestore Database
Handles user feedback, ratings, and reviews for courses/webinars
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.constants.statuses import FeedbackStatus, ReviewStatus


class RatingBreakdown(BaseModel):
    """Individual rating component breakdown"""
    rating_1: int = Field(0, ge=0, le=1000)  # Count of 1-star ratings
    rating_2: int = Field(0, ge=0, le=1000)  # Count of 2-star ratings
    rating_3: int = Field(0, ge=0, le=1000)  # Count of 3-star ratings
    rating_4: int = Field(0, ge=0, le=1000)  # Count of 4-star ratings
    rating_5: int = Field(0, ge=0, le=1000)  # Count of 5-star ratings


class FeedbackAnalytics(BaseModel):
    """Feedback analytics and metrics"""
    total_ratings: int = 0
    average_rating: float = 0.0
    rating_breakdown: RatingBreakdown = Field(default_factory=RatingBreakdown)
    total_reviews: int = 0
    reviews_with_comments: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    response_rate: float = 0.0  # Percentage of users who provided feedback
    sentiment_score: float = 0.0  # AI-generated sentiment analysis
    topic_frequency: Dict[str, int] = {}  # Common topics mentioned


class FeedbackCategory(BaseModel):
    """Feedback categorization"""
    overall: str = "general"  # general, content, instructor, technical, billing
    content_quality: Optional[int] = None  # 1-5 rating
    instructor_rating: Optional[int] = None  # 1-5 rating
    technical_quality: Optional[int] = None  # 1-5 rating
    value_for_money: Optional[int] = None  # 1-5 rating
    difficulty_level: Optional[str] = None  # beginner, intermediate, advanced
    learning_outcomes: Optional[str] = None  # met, partially_met, not_met


class UserFeedback(BaseModel):
    """User feedback structure"""
    feedback_id: str = Field("", description="Unique feedback ID")
    user_uid: str = Field(..., description="User Firebase UID")
    item_id: str = Field(..., description="Course or webinar ID")
    item_type: str = Field(..., description="course or webinar")
    user_info: Dict[str, str] = Field(..., description="User basic info")
    
    # Rating (1-5 scale)
    rating: int = Field(..., ge=1, le=5, description="Overall rating")
    
    # Review content
    review_title: Optional[str] = Field(None, max_length=200)
    review_content: Optional[str] = Field(None, max_length=2000)
    
    # Detailed feedback
    category: FeedbackCategory = Field(default_factory=FeedbackCategory)
    
    # Status and moderation
    status: FeedbackStatus = Field(default=FeedbackStatus.PENDING)
    moderation_notes: Optional[str] = None
    moderated_by: Optional[str] = None
    moderated_at: Optional[datetime] = None
    
    # Admin response
    admin_response: Optional[str] = None
    admin_response_date: Optional[datetime] = None
    admin_responded_by: Optional[str] = None
    
    # User interaction
    helpful_votes: int = Field(0, ge=0)
    unhelpful_votes: int = Field(0, ge=0)
    is_verified_purchase: bool = False
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    language: Optional[str] = "en"
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('item_type')
    def validate_item_type(cls, v):
        if v not in ['course', 'webinar']:
            raise ValueError('item_type must be either "course" or "webinar"')
        return v
    
    @validator('review_title')
    def validate_review_title(cls, v):
        if v and len(v.strip()) < 5:
            raise ValueError('Review title must be at least 5 characters long')
        return v
    
    @validator('review_content')
    def validate_review_content(cls, v):
        if v and len(v.strip()) < 20:
            raise ValueError('Review content must be at least 20 characters long')
        return v


class FeedbackResponse(BaseModel):
    """Response model for feedback operations"""
    success: bool
    message: str
    feedback_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class FeedbackModel:
    """Feedback model for Firestore operations"""
    
    COLLECTION_NAME = "feedback"
    ANALYTICS_COLLECTION = "feedback_analytics"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
        self.analytics_collection = self.db.collection(self.ANALYTICS_COLLECTION)
    
    async def create_feedback(
        self,
        user_uid: str,
        user_email: str,
        user_name: str,
        item_id: str,
        item_type: str,
        rating: int,
        review_title: Optional[str] = None,
        review_content: Optional[str] = None,
        category: Optional[Dict[str, Any]] = None,
        is_verified_purchase: bool = False,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new user feedback
        
        Args:
            user_uid: User Firebase UID
            user_email: User email
            user_name: User name
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            rating: Rating (1-5)
            review_title: Optional review title
            review_content: Optional review content
            category: Optional feedback category details
            is_verified_purchase: Whether user has purchased the item
            additional_data: Additional feedback data
            
        Returns:
            Feedback ID
        """
        # Check if user already has feedback for this item
        existing_feedback = await self.get_user_feedback_for_item(user_uid, item_id)
        if existing_feedback:
            raise ValueError("User has already provided feedback for this item")
        
        # Create user feedback object
        user_info = {
            "name": user_name,
            "email": user_email
        }
        
        feedback_category = FeedbackCategory()
        if category:
            for key, value in category.items():
                if hasattr(feedback_category, key):
                    setattr(feedback_category, key, value)
        
        feedback_data = UserFeedback(
            user_uid=user_uid,
            item_id=item_id,
            item_type=item_type,
            user_info=user_info,
            rating=rating,
            review_title=review_title,
            review_content=review_content,
            category=feedback_category,
            is_verified_purchase=is_verified_purchase,
            **additional_data
        )
        
        # Create feedback document
        doc_ref = self.collection.document()
        feedback_data.feedback_id = doc_ref.id
        
        feedback_dict = feedback_data.dict()
        
        # Convert datetime objects to ISO strings for Firestore
        for key, value in feedback_dict.items():
            if isinstance(value, datetime):
                feedback_dict[key] = value.isoformat()
        
        await doc_ref.set(feedback_dict)
        
        # Update analytics
        await self._update_item_analytics(item_id, item_type, feedback_data)
        
        return doc_ref.id
    
    async def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """
        Get feedback by ID
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            Feedback data or None if not found
        """
        doc = self.collection.document(feedback_id).get()
        
        if doc.exists:
            feedback_data = doc.to_dict()
            feedback_data["feedback_id"] = doc.id
            return self._convert_datetime_strings(feedback_data)
        
        return None
    
    async def get_user_feedback_for_item(self, user_uid: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's feedback for a specific item
        
        Args:
            user_uid: User Firebase UID
            item_id: Course or webinar ID
            
        Returns:
            Feedback data or None if not found
        """
        query = self.collection \
            .where("user_uid", "==", user_uid) \
            .where("item_id", "==", item_id)
        
        docs = query.get()
        
        for doc in docs:
            feedback_data = doc.to_dict()
            feedback_data["feedback_id"] = doc.id
            return self._convert_datetime_strings(feedback_data)
        
        return None
    
    async def get_item_feedback(
        self,
        item_id: str,
        item_type: str,
        status: Optional[FeedbackStatus] = None,
        min_rating: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get feedback for a specific item
        
        Args:
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            status: Filter by feedback status
            min_rating: Minimum rating filter
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            List of feedback
        """
        query = self.collection \
            .where("item_id", "==", item_id) \
            .where("item_type", "==", item_type)
        
        if status:
            query = query.where("status", "==", status.value)
        
        if min_rating:
            query = query.where("rating", ">=", min_rating)
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        feedback_list = []
        for doc in docs:
            feedback_data = doc.to_dict()
            feedback_data["feedback_id"] = doc.id
            feedback_list.append(self._convert_datetime_strings(feedback_data))
        
        return feedback_list
    
    async def update_feedback(
        self,
        feedback_id: str,
        user_uid: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update user feedback
        
        Args:
            feedback_id: Feedback ID
            user_uid: User Firebase UID (for authorization)
            updates: Fields to update
            
        Returns:
            True if successful
        """
        # Verify ownership
        feedback = await self.get_feedback(feedback_id)
        if not feedback or feedback["user_uid"] != user_uid:
            return False
        
        # Remove fields that shouldn't be updated by user
        protected_fields = [
            "feedback_id", "user_uid", "item_id", "item_type", "user_info",
            "status", "moderation_notes", "moderated_by", "moderated_at",
            "admin_response", "admin_response_date", "admin_responded_by",
            "helpful_votes", "unhelpful_votes", "is_verified_purchase",
            "created_at"
        ]
        
        for field in protected_fields:
            updates.pop(field, None)
        
        updates["updated_at"] = datetime.utcnow()
        
        doc_ref = self.collection.document(feedback_id)
        await doc_ref.update(updates)
        
        return True
    
    async def moderate_feedback(
        self,
        feedback_id: str,
        admin_uid: str,
        status: FeedbackStatus,
        moderation_notes: Optional[str] = None
    ) -> bool:
        """
        Moderate feedback (admin only)
        
        Args:
            feedback_id: Feedback ID
            admin_uid: Admin user UID
            status: New moderation status
            moderation_notes: Moderation notes
            
        Returns:
            True if successful
        """
        updates = {
            "status": status.value,
            "moderated_by": admin_uid,
            "moderated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if moderation_notes:
            updates["moderation_notes"] = moderation_notes
        
        doc_ref = self.collection.document(feedback_id)
        await doc_ref.update(updates)
        
        return True
    
    async def add_admin_response(
        self,
        feedback_id: str,
        admin_uid: str,
        response: str
    ) -> bool:
        """
        Add admin response to feedback
        
        Args:
            feedback_id: Feedback ID
            admin_uid: Admin user UID
            response: Admin response text
            
        Returns:
            True if successful
        """
        updates = {
            "admin_response": response,
            "admin_response_date": datetime.utcnow(),
            "admin_responded_by": admin_uid,
            "updated_at": datetime.utcnow()
        }
        
        doc_ref = self.collection.document(feedback_id)
        await doc_ref.update(updates)
        
        return True
    
    async def vote_feedback_helpful(
        self,
        feedback_id: str,
        voter_uid: str,
        is_helpful: bool
    ) -> bool:
        """
        Vote if feedback is helpful or not
        
        Args:
            feedback_id: Feedback ID
            voter_uid: User who is voting
            is_helpful: Whether vote is helpful (True) or not (False)
            
        Returns:
            True if successful
        """
        # Check if user has already voted
        votes_collection = self.collection.document(feedback_id).collection("votes")
        vote_doc = votes_collection.document(voter_uid).get()
        
        if vote_doc.exists:
            return False  # User has already voted
        
        # Add vote
        vote_data = {
            "is_helpful": is_helpful,
            "voted_at": datetime.utcnow()
        }
        await votes_collection.document(voter_uid).set(vote_data)
        
        # Update feedback vote counts
        feedback_doc = self.collection.document(feedback_id).get()
        if feedback_doc.exists:
            feedback_data = feedback_doc.to_dict()
            
            updates = {
                "updated_at": datetime.utcnow()
            }
            
            if is_helpful:
                updates["helpful_votes"] = feedback_data.get("helpful_votes", 0) + 1
            else:
                updates["unhelpful_votes"] = feedback_data.get("unhelpful_votes", 0) + 1
            
            await feedback_doc.reference.update(updates)
        
        return True
    
    async def search_feedback(
        self,
        search_term: str = "",
        item_id: str = "",
        item_type: str = "",
        user_uid: str = "",
        status: Optional[FeedbackStatus] = None,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        is_verified_purchase: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search feedback with filters
        
        Args:
            search_term: Search term for review content/title
            item_id: Filter by item ID
            item_type: Filter by item type
            user_uid: Filter by user
            status: Filter by feedback status
            min_rating: Minimum rating filter
            max_rating: Maximum rating filter
            is_verified_purchase: Filter by verified purchase status
            start_date: Filter by start date
            end_date: Filter by end date
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            Dictionary with feedback and pagination info
        """
        query = self.collection
        
        # Apply filters
        if item_id:
            query = query.where("item_id", "==", item_id)
        
        if item_type:
            query = query.where("item_type", "==", item_type)
        
        if user_uid:
            query = query.where("user_uid", "==", user_uid)
        
        if status:
            query = query.where("status", "==", status.value)
        
        if min_rating:
            query = query.where("rating", ">=", min_rating)
        
        if max_rating:
            query = query.where("rating", "<=", max_rating)
        
        if is_verified_purchase is not None:
            query = query.where("is_verified_purchase", "==", is_verified_purchase)
        
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
        
        feedback_list = []
        for doc in docs:
            feedback_data = doc.to_dict()
            feedback_data["feedback_id"] = doc.id
            
            # Apply search term filter (for text content)
            if search_term:
                search_fields = [
                    feedback_data.get("review_title", ""),
                    feedback_data.get("review_content", ""),
                    feedback_data.get("user_info", {}).get("name", ""),
                    feedback_data.get("admin_response", "")
                ]
                
                if not any(search_term.lower() in field.lower() for field in search_fields if field):
                    continue
            
            feedback_list.append(self._convert_datetime_strings(feedback_data))
        
        # Get total count for pagination
        count_query = self.collection
        if item_id:
            count_query = count_query.where("item_id", "==", item_id)
        if item_type:
            count_query = count_query.where("item_type", "==", item_type)
        if status:
            count_query = count_query.where("status", "==", status.value)
        
        total_count = len(count_query.get())
        
        return {
            "feedback": feedback_list,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_feedback_analytics(self, item_id: str, item_type: str) -> Dict[str, Any]:
        """
        Get feedback analytics for an item
        
        Args:
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            
        Returns:
            Dictionary with analytics data
        """
        doc_ref = self.analytics_collection.document(f"{item_type}_{item_id}")
        doc = doc_ref.get()
        
        if doc.exists:
            analytics_data = doc.to_dict()
            return self._convert_datetime_strings(analytics_data)
        
        # Calculate analytics if not exists
        return await self._calculate_item_analytics(item_id, item_type)
    
    async def _calculate_item_analytics(self, item_id: str, item_type: str) -> Dict[str, Any]:
        """
        Calculate analytics for an item
        
        Args:
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            
        Returns:
            Analytics data
        """
        query = self.collection \
            .where("item_id", "==", item_id) \
            .where("item_type", "==", item_type) \
            .where("status", "==", FeedbackStatus.APPROVED.value)
        
        docs = query.get()
        
        total_ratings = 0
        total_reviews = 0
        reviews_with_comments = 0
        rating_breakdown = RatingBreakdown()
        helpful_votes = 0
        unhelpful_votes = 0
        
        # Aggregate feedback data
        for doc in docs:
            feedback_data = doc.to_dict()
            
            total_ratings += 1
            total_reviews += 1
            
            # Update rating breakdown
            rating = feedback_data.get("rating", 0)
            if 1 <= rating <= 5:
                setattr(rating_breakdown, f"rating_{rating}", 
                       getattr(rating_breakdown, f"rating_{rating}") + 1)
            
            # Check if review has comments
            if feedback_data.get("review_content"):
                reviews_with_comments += 1
            
            # Count votes
            helpful_votes += feedback_data.get("helpful_votes", 0)
            unhelpful_votes += feedback_data.get("unhelpful_votes", 0)
        
        # Calculate metrics
        average_rating = 0.0
        if total_ratings > 0:
            total_rating_value = (
                rating_breakdown.rating_1 * 1 +
                rating_breakdown.rating_2 * 2 +
                rating_breakdown.rating_3 * 3 +
                rating_breakdown.rating_4 * 4 +
                rating_breakdown.rating_5 * 5
            )
            average_rating = total_rating_value / total_ratings
        
        response_rate = 0.0
        # Note: This would need purchase data to calculate accurately
        # For now, we'll use a placeholder calculation
        
        analytics_data = {
            "item_id": item_id,
            "item_type": item_type,
            "total_ratings": total_ratings,
            "average_rating": round(average_rating, 2),
            "rating_breakdown": rating_breakdown.dict(),
            "total_reviews": total_reviews,
            "reviews_with_comments": reviews_with_comments,
            "helpful_votes": helpful_votes,
            "unhelpful_votes": unhelpful_votes,
            "response_rate": response_rate,
            "last_updated": datetime.utcnow()
        }
        
        # Save analytics
        await self.analytics_collection.document(f"{item_type}_{item_id}").set(analytics_data)
        
        return analytics_data
    
    async def _update_item_analytics(self, item_id: str, item_type: str, feedback_data: UserFeedback):
        """
        Update item analytics when new feedback is added
        
        Args:
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            feedback_data: New feedback data
        """
        # Update analytics document
        analytics_ref = self.analytics_collection.document(f"{item_type}_{item_id}")
        analytics_doc = analytics_ref.get()
        
        if analytics_doc.exists:
            analytics_data = analytics_doc.to_dict()
        else:
            # Create new analytics document
            analytics_data = {
                "item_id": item_id,
                "item_type": item_type,
                "total_ratings": 0,
                "average_rating": 0.0,
                "rating_breakdown": RatingBreakdown().dict(),
                "total_reviews": 0,
                "reviews_with_comments": 0,
                "helpful_votes": 0,
                "unhelpful_votes": 0,
                "response_rate": 0.0,
                "last_updated": datetime.utcnow()
            }
        
        # Update counts
        analytics_data["total_ratings"] += 1
        analytics_data["total_reviews"] += 1
        
        if feedback_data.review_content:
            analytics_data["reviews_with_comments"] += 1
        
        # Update rating breakdown
        rating = feedback_data.rating
        if 1 <= rating <= 5:
            analytics_data["rating_breakdown"][f"rating_{rating}"] += 1
        
        # Recalculate average rating
        total_ratings = analytics_data["total_ratings"]
        if total_ratings > 0:
            rating_breakdown = analytics_data["rating_breakdown"]
            total_rating_value = (
                rating_breakdown.get("rating_1", 0) * 1 +
                rating_breakdown.get("rating_2", 0) * 2 +
                rating_breakdown.get("rating_3", 0) * 3 +
                rating_breakdown.get("rating_4", 0) * 4 +
                rating_breakdown.get("rating_5", 0) * 5
            )
            analytics_data["average_rating"] = round(total_rating_value / total_ratings, 2)
        
        analytics_data["last_updated"] = datetime.utcnow()
        
        await analytics_ref.set(analytics_data)
    
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
                    # Try to parse ISO format datetime
                    from datetime import datetime
                    data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
        
        return data


# Helper functions for feedback operations
def create_feedback_category(
    overall: str = "general",
    content_quality: Optional[int] = None,
    instructor_rating: Optional[int] = None,
    technical_quality: Optional[int] = None,
    value_for_money: Optional[int] = None,
    difficulty_level: Optional[str] = None,
    learning_outcomes: Optional[str] = None
) -> FeedbackCategory:
    """
    Create feedback category
    
    Args:
        overall: Overall category
        content_quality: Content quality rating (1-5)
        instructor_rating: Instructor rating (1-5)
        technical_quality: Technical quality rating (1-5)
        value_for_money: Value for money rating (1-5)
        difficulty_level: Difficulty level
        learning_outcomes: Learning outcomes achievement
        
    Returns:
        FeedbackCategory object
    """
    return FeedbackCategory(
        overall=overall,
        content_quality=content_quality,
        instructor_rating=instructor_rating,
        technical_quality=technical_quality,
        value_for_money=value_for_money,
        difficulty_level=difficulty_level,
        learning_outcomes=learning_outcomes
    )


def calculate_overall_rating(
    content_quality: Optional[int] = None,
    instructor_rating: Optional[int] = None,
    technical_quality: Optional[int] = None,
    value_for_money: Optional[int] = None
) -> int:
    """
    Calculate overall rating from component ratings
    
    Args:
        content_quality: Content quality rating (1-5)
        instructor_rating: Instructor rating (1-5)
        technical_quality: Technical quality rating (1-5)
        value_for_money: Value for money rating (1-5)
        
    Returns:
        Overall rating (1-5)
    """
    ratings = []
    
    if content_quality:
        ratings.append(content_quality)
    if instructor_rating:
        ratings.append(instructor_rating)
    if technical_quality:
        ratings.append(technical_quality)
    if value_for_money:
        ratings.append(value_for_money)
    
    if not ratings:
        return 3  # Default rating
    
    # Calculate weighted average
    total = sum(ratings)
    count = len(ratings)
    
    return max(1, min(5, round(total / count)))