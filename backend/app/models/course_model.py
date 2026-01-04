"""
Course Model for Firestore Database
Handles course creation, management, and enrollment tracking
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.constants.statuses import CourseStatus, CourseLevel


class CourseContent(BaseModel):
    """Course content structure"""
    title: str
    type: str  # video, text, quiz, assignment, etc.
    content_url: Optional[str] = None
    content_data: Optional[Dict[str, Any]] = None
    duration_minutes: Optional[int] = None
    order: int
    is_preview: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CourseRequirement(BaseModel):
    """Course prerequisites or requirements"""
    type: str  # course, skill, experience
    description: str
    is_required: bool = True
    course_id: Optional[str] = None  # If type is 'course'


class CourseLearningOutcome(BaseModel):
    """What students will learn"""
    description: str
    category: Optional[str] = None  # technical, soft_skill, etc.


class CourseInstructor(BaseModel):
    """Course instructor information"""
    uid: str
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    credentials: List[str] = []
    is_primary: bool = True


class CoursePricing(BaseModel):
    """Course pricing structure"""
    price: float = 0.0
    currency: str = "USD"
    discount_price: Optional[float] = None
    discount_valid_until: Optional[datetime] = None
    is_free: bool = False
    access_duration_days: Optional[int] = None  # Lifetime access if None


class CourseModel:
    """Course model for Firestore operations"""
    
    COLLECTION_NAME = "courses"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def create_course_data(
        self,
        title: str,
        description: str,
        instructor_uid: str,
        instructor_name: str,
        price: float = 0.0,
        is_free: bool = False,
        category: str = "",
        level: CourseLevel = CourseLevel.BEGINNER,
        status: CourseStatus = CourseStatus.DRAFT,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create course data structure
        
        Args:
            title: Course title
            description: Course description
            instructor_uid: Firebase UID of instructor
            instructor_name: Instructor name
            price: Course price
            is_free: Whether course is free
            category: Course category
            level: Course difficulty level
            status: Course status
            additional_data: Additional course data
            
        Returns:
            Dictionary with course data
        """
        course_data = {
            "id": "",  # Will be set when created
            "title": title,
            "slug": self._generate_slug(title),
            "description": description,
            "short_description": description[:200] + "..." if len(description) > 200 else description,
            "instructor": {
                "uid": instructor_uid,
                "name": instructor_name,
                "bio": "",
                "avatar_url": None,
                "credentials": [],
                "is_primary": True
            },
            "category": category,
            "level": level.value,
            "status": status.value,
            "pricing": {
                "price": price,
                "currency": "USD",
                "discount_price": None,
                "discount_valid_until": None,
                "is_free": is_free,
                "access_duration_days": None
            },
            "content": {
                "total_lessons": 0,
                "total_duration_minutes": 0,
                "lessons": [],
                "sections": []
            },
            "requirements": [],
            "learning_outcomes": [],
            "media": {
                "thumbnail_url": None,
                "preview_video_url": None,
                "gallery_images": []
            },
            "settings": {
                "is_published": status == CourseStatus.PUBLISHED,
                "allow_comments": True,
                "allow_downloads": False,
                "certificate_enabled": True,
                "completion_percentage": 100
            },
            "stats": {
                "enrolled_students": 0,
                "completed_students": 0,
                "average_rating": 0.0,
                "total_ratings": 0,
                "total_reviews": 0,
                "total_revenue": 0.0,
                "views": 0
            },
            "seo": {
                "meta_title": title,
                "meta_description": description[:160],
                "tags": [],
                "keywords": []
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "published_at": None if status != CourseStatus.PUBLISHED else datetime.utcnow(),
            "metadata": {}
        }
        
        if additional_data:
            course_data["metadata"].update(additional_data)
        
        return course_data
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        
        return slug
    
    async def create_course(
        self,
        title: str,
        description: str,
        instructor_uid: str,
        instructor_name: str,
        price: float = 0.0,
        is_free: bool = False,
        category: str = "",
        level: CourseLevel = CourseLevel.BEGINNER,
        status: CourseStatus = CourseStatus.DRAFT,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new course
        
        Args:
            title: Course title
            description: Course description
            instructor_uid: Firebase UID of instructor
            instructor_name: Instructor name
            price: Course price
            is_free: Whether course is free
            category: Course category
            level: Course difficulty level
            status: Course status
            additional_data: Additional course data
            
        Returns:
            Course ID
        """
        course_data = self.create_course_data(
            title, description, instructor_uid, instructor_name, 
            price, is_free, category, level, status, additional_data
        )
        
        # Create course document
        doc_ref = self.collection.document()
        course_data["id"] = doc_ref.id
        
        await doc_ref.set(course_data)
        
        return doc_ref.id
    
    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Get course by ID
        
        Args:
            course_id: Course ID
            
        Returns:
            Course data or None if not found
        """
        doc = self.collection.document(course_id).get()
        
        if doc.exists:
            course_data = doc.to_dict()
            course_data["id"] = doc.id
            return course_data
        
        return None
    
    async def get_course_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get course by slug
        
        Args:
            slug: Course slug
            
        Returns:
            Course data or None if not found
        """
        query = self.collection.where("slug", "==", slug).limit(1)
        docs = query.get()
        
        for doc in docs:
            course_data = doc.to_dict()
            course_data["id"] = doc.id
            return course_data
        
        return None
    
    async def update_course(
        self,
        course_id: str,
        updates: Dict[str, Any],
        update_timestamps: bool = True
    ) -> bool:
        """
        Update course data
        
        Args:
            course_id: Course ID
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
        
        # Clean up None values
        updates = {k: v for k, v in updates.items() if v is not None}
        
        if not updates:
            return False
        
        doc_ref = self.collection.document(course_id)
        await doc_ref.update(updates)
        
        return True
    
    async def update_course_status(self, course_id: str, status: CourseStatus) -> bool:
        """
        Update course status
        
        Args:
            course_id: Course ID
            status: New course status
            
        Returns:
            True if successful
        """
        updates = {
            "status": status.value,
            "settings.is_published": status == CourseStatus.PUBLISHED
        }
        
        if status == CourseStatus.PUBLISHED:
            updates["published_at"] = datetime.utcnow()
        
        return await self.update_course(course_id, updates, update_timestamps=False)
    
    async def update_course_pricing(self, course_id: str, pricing_data: Dict[str, Any]) -> bool:
        """
        Update course pricing
        
        Args:
            course_id: Course ID
            pricing_data: Pricing data to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(course_id).get()
        
        if not doc.exists:
            raise ValueError("Course not found")
        
        current_course = doc.to_dict()
        current_pricing = current_course.get("pricing", {})
        
        # Merge with existing pricing
        updated_pricing = {**current_pricing, **pricing_data}
        
        return await self.update_course(course_id, {"pricing": updated_pricing})
    
    async def add_course_content(self, course_id: str, content: CourseContent) -> bool:
        """
        Add content to course
        
        Args:
            course_id: Course ID
            content: Content to add
            
        Returns:
            True if successful
        """
        doc = self.collection.document(course_id).get()
        
        if not doc.exists:
            raise ValueError("Course not found")
        
        course_data = doc.to_dict()
        lessons = course_data.get("content", {}).get("lessons", [])
        
        # Add content and set order
        content_dict = content.dict()
        content_dict["created_at"] = datetime.utcnow()
        content_dict["order"] = len(lessons) + 1
        
        lessons.append(content_dict)
        
        # Update content stats
        total_duration = course_data.get("content", {}).get("total_duration_minutes", 0)
        if content.duration_minutes:
            total_duration += content.duration_minutes
        
        updates = {
            "content.lessons": lessons,
            "content.total_lessons": len(lessons),
            "content.total_duration_minutes": total_duration
        }
        
        return await self.update_course(course_id, updates, update_timestamps=False)
    
    async def update_course_stats(self, course_id: str, stats_updates: Dict[str, Any]) -> bool:
        """
        Update course statistics
        
        Args:
            course_id: Course ID
            stats_updates: Stats to update
            
        Returns:
            True if successful
        """
        doc = self.collection.document(course_id).get()
        
        if not doc.exists:
            return False
        
        current_course = doc.to_dict()
        current_stats = current_course.get("stats", {})
        
        # Handle numeric updates
        updated_stats = current_stats.copy()
        for key, value in stats_updates.items():
            if key in current_stats and isinstance(current_stats[key], (int, float)) and isinstance(value, (int, float)):
                updated_stats[key] = current_stats[key] + value
            else:
                updated_stats[key] = value
        
        return await self.update_course(course_id, {"stats": updated_stats})
    
    async def delete_course(self, course_id: str, soft_delete: bool = True) -> bool:
        """
        Delete course
        
        Args:
            course_id: Course ID
            soft_delete: Whether to soft delete
            
        Returns:
            True if successful
        """
        if soft_delete:
            # Soft delete - mark as deleted
            updates = {
                "status": CourseStatus.DELETED.value,
                "settings.is_published": False,
                "deleted_at": datetime.utcnow()
            }
            return await self.update_course(course_id, updates, update_timestamps=False)
        else:
            # Hard delete
            await self.collection.document(course_id).delete()
            return True
    
    async def search_courses(
        self,
        search_term: str = "",
        category: str = "",
        level: Optional[CourseLevel] = None,
        instructor_uid: str = "",
        status: Optional[CourseStatus] = None,
        is_free: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search courses with filters
        
        Args:
            search_term: Search term for title/description
            category: Filter by category
            level: Filter by difficulty level
            instructor_uid: Filter by instructor
            status: Filter by status
            is_free: Filter by free/paid
            min_price: Minimum price
            max_price: Maximum price
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            Dictionary with courses and pagination info
        """
        query = self.collection
        
        # Apply filters
        if status:
            query = query.where("status", "==", status.value)
        else:
            # Default to published courses only
            query = query.where("status", "==", CourseStatus.PUBLISHED.value)
        
        if level:
            query = query.where("level", "==", level.value)
        
        if instructor_uid:
            query = query.where("instructor.uid", "==", instructor_uid)
        
        if is_free is not None:
            query = query.where("pricing.is_free", "==", is_free)
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        
        if sort_by == "price":
            query = query.order_by("pricing.price", direction=direction)
        elif sort_by == "rating":
            query = query.order_by("stats.average_rating", direction=direction)
        elif sort_by == "popularity":
            query = query.order_by("stats.enrolled_students", direction=direction)
        else:
            query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        courses = []
        for doc in docs:
            course_data = doc.to_dict()
            course_data["id"] = doc.id
            
            # Apply additional filters
            skip = False
            
            # Category filter
            if category and course_data.get("category") != category:
                skip = True
            
            # Price range filter
            if not skip:
                price = course_data.get("pricing", {}).get("price", 0.0)
                if min_price is not None and price < min_price:
                    skip = True
                if max_price is not None and price > max_price:
                    skip = True
            
            # Search term filter
            if search_term and not skip:
                search_fields = [
                    course_data.get("title", ""),
                    course_data.get("description", ""),
                    course_data.get("short_description", "")
                ]
                
                if not any(search_term.lower() in field.lower() for field in search_fields if field):
                    skip = True
            
            if not skip:
                courses.append(course_data)
        
        # Get total count for pagination
        count_query = self.collection
        if status:
            count_query = count_query.where("status", "==", status.value)
        else:
            count_query = count_query.where("status", "==", CourseStatus.PUBLISHED.value)
        
        total_count = len(count_query.get())
        
        return {
            "courses": courses,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_featured_courses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get featured courses (high-rated and popular)
        
        Args:
            limit: Number of courses to return
            
        Returns:
            List of featured courses
        """
        query = self.collection \
            .where("status", "==", CourseStatus.PUBLISHED.value) \
            .where("stats.average_rating", ">=", 4.0) \
            .order_by("stats.average_rating", direction="DESCENDING") \
            .order_by("stats.enrolled_students", direction="DESCENDING") \
            .limit(limit)
        
        docs = query.get()
        courses = []
        
        for doc in docs:
            course_data = doc.to_dict()
            course_data["id"] = doc.id
            courses.append(course_data)
        
        return courses
    
    async def get_courses_by_instructor(self, instructor_uid: str) -> List[Dict[str, Any]]:
        """
        Get all courses by instructor
        
        Args:
            instructor_uid: Firebase UID of instructor
            
        Returns:
            List of courses by instructor
        """
        query = self.collection.where("instructor.uid", "==", instructor_uid)
        docs = query.get()
        
        courses = []
        for doc in docs:
            course_data = doc.to_dict()
            course_data["id"] = doc.id
            courses.append(course_data)
        
        return courses
    
    async def get_course_statistics(self) -> Dict[str, Any]:
        """
        Get overall course statistics
        
        Returns:
            Dictionary with course statistics
        """
        docs = self.collection.get()
        
        stats = {
            "total_courses": 0,
            "courses_by_status": {},
            "courses_by_level": {},
            "courses_by_category": {},
            "total_enrolled_students": 0,
            "total_revenue": 0.0,
            "average_rating": 0.0,
            "published_courses": 0,
            "draft_courses": 0
        }
        
        total_rating_sum = 0
        total_rating_count = 0
        
        for doc in docs:
            course_data = doc.to_dict()
            stats["total_courses"] += 1
            
            # Count by status
            status = course_data.get("status", "unknown")
            stats["courses_by_status"][status] = stats["courses_by_status"].get(status, 0) + 1
            
            if status == CourseStatus.PUBLISHED.value:
                stats["published_courses"] += 1
            elif status == CourseStatus.DRAFT.value:
                stats["draft_courses"] += 1
            
            # Count by level
            level = course_data.get("level", "unknown")
            stats["courses_by_level"][level] = stats["courses_by_level"].get(level, 0) + 1
            
            # Count by category
            category = course_data.get("category", "unknown")
            stats["courses_by_category"][category] = stats["courses_by_category"].get(category, 0) + 1
            
            # Aggregate stats
            course_stats = course_data.get("stats", {})
            stats["total_enrolled_students"] += course_stats.get("enrolled_students", 0)
            stats["total_revenue"] += course_stats.get("total_revenue", 0.0)
            
            # Calculate average rating
            avg_rating = course_stats.get("average_rating", 0.0)
            rating_count = course_stats.get("total_ratings", 0)
            
            if avg_rating > 0 and rating_count > 0:
                total_rating_sum += avg_rating * rating_count
                total_rating_count += rating_count
        
        if total_rating_count > 0:
            stats["average_rating"] = total_rating_sum / total_rating_count
        
        return stats


# Dependency for course operations
class CourseDependency:
    """Helper class for course-related dependencies"""
    
    def __init__(self):
        self.model = CourseModel()
    
    async def get_course_or_404(self, course_id: str) -> Dict[str, Any]:
        """Get course or raise exception"""
        course = await self.model.get_course(course_id)
        
        if not course:
            raise ValueError("Course not found")
        
        return course
    
    async def require_published_course(self, course_id: str) -> Dict[str, Any]:
        """Require published course"""
        course = await self.get_course_or_404(course_id)
        
        if course.get("status") != CourseStatus.PUBLISHED.value:
            raise ValueError("Course is not published")
        
        return course