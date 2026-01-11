"""
Course Schemas - Pydantic models for course-related requests and responses
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class CourseStatus(str, Enum):
    """Course status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"

class CourseVisibility(str, Enum):
    """Course visibility enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"

class CourseLevel(str, Enum):
    """Course difficulty level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CourseBase(BaseModel):
    """Base course schema with common fields"""
    title: str = Field(..., min_length=3, max_length=200, description="Course title")
    description: Optional[str] = Field(None, max_length=2000, description="Course description")
    short_description: Optional[str] = Field(None, max_length=500, description="Brief course summary")
    
    # Course content
    content: Optional[str] = Field(None, description="Course content/material")
    objectives: Optional[List[str]] = Field(default_factory=list, description="Learning objectives")
    prerequisites: Optional[List[str]] = Field(default_factory=list, description="Prerequisites")
    
    # Course metadata
    category: Optional[str] = Field(None, max_length=100, description="Course category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Course tags")
    level: CourseLevel = Field(default=CourseLevel.BEGINNER, description="Course difficulty level")
    
    # Course settings
    status: CourseStatus = Field(default=CourseStatus.DRAFT, description="Course status")
    visibility: CourseVisibility = Field(default=CourseVisibility.PUBLIC, description="Course visibility")
    is_featured: bool = Field(default=False, description="Whether course is featured")
    is_free: bool = Field(default=False, description="Whether course is free")
    
    # Pricing
    price: float = Field(default=0.0, ge=0, description="Course price")
    discount_price: Optional[float] = Field(None, ge=0, description="Discounted price")
    
    # Media
    thumbnail_url: Optional[str] = Field(None, description="Course thumbnail URL")
    preview_video_url: Optional[str] = Field(None, description="Preview video URL")
    
    # Schedule
    duration_hours: Optional[int] = Field(None, gt=0, description="Course duration in hours")
    start_date: Optional[datetime] = Field(None, description="Course start date")
    end_date: Optional[datetime] = Field(None, description="Course end date")
    
    # Enrollment settings
    max_enrollment: Optional[int] = Field(None, gt=0, description="Maximum enrollment limit")
    enrollment_start: Optional[datetime] = Field(None, description="Enrollment start date")
    enrollment_end: Optional[datetime] = Field(None, description="Enrollment end date")
    
    @validator('discount_price')
    def validate_discount_price(cls, v, values):
        if v is not None and 'price' in values and v >= values['price']:
            raise ValueError('Discount price must be less than regular price')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date'] and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('enrollment_end')
    def validate_enrollment_end(cls, v, values):
        if v and 'enrollment_start' in values and values['enrollment_start'] and v <= values['enrollment_start']:
            raise ValueError('Enrollment end date must be after enrollment start date')
        return v

class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    pass

class CourseUpdate(BaseModel):
    """Schema for updating an existing course"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    short_description: Optional[str] = Field(None, max_length=500)
    
    content: Optional[str] = None
    objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    level: Optional[CourseLevel] = None
    
    status: Optional[CourseStatus] = None
    visibility: Optional[CourseVisibility] = None
    is_featured: Optional[bool] = None
    is_free: Optional[bool] = None
    
    price: Optional[float] = Field(None, ge=0)
    discount_price: Optional[float] = Field(None, ge=0)
    
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    
    duration_hours: Optional[int] = Field(None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    max_enrollment: Optional[int] = Field(None, gt=0)
    enrollment_start: Optional[datetime] = None
    enrollment_end: Optional[datetime] = None
    
    @validator('discount_price')
    def validate_discount_price(cls, v, values):
        if v is not None and 'price' in values and values['price'] is not None and v >= values['price']:
            raise ValueError('Discount price must be less than regular price')
        return v

class CourseResponse(CourseBase):
    """Schema for course response"""
    id: str = Field(..., description="Course ID")
    instructor_id: str = Field(..., description="Instructor user ID")
    instructor_name: Optional[str] = Field(None, description="Instructor name")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Statistics
    enrollment_count: int = Field(default=0, description="Number of enrolled students")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    review_count: int = Field(default=0, description="Number of reviews")
    
    # Completion and progress
    completion_rate: Optional[float] = Field(None, ge=0, le=100, description="Course completion rate")
    
    class Config:
        from_attributes = True

class CourseListItem(BaseModel):
    """Schema for course list items"""
    id: str
    title: str
    short_description: Optional[str]
    thumbnail_url: Optional[str]
    price: float
    discount_price: Optional[float]
    is_free: bool
    level: CourseLevel
    category: Optional[str]
    tags: List[str]
    instructor_name: Optional[str]
    enrollment_count: int
    rating: Optional[float]
    review_count: int
    created_at: datetime
    status: CourseStatus
    visibility: CourseVisibility

class CourseEnrollment(BaseModel):
    """Schema for course enrollment"""
    course_id: str
    enrolled_at: datetime
    progress: float = Field(default=0.0, ge=0, le=100, description="Completion progress percentage")
    completed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    is_active: bool = Field(default=True, description="Whether enrollment is still active")

class CourseAnalytics(BaseModel):
    """Schema for course analytics data"""
    total_courses: int
    published_courses: int
    draft_courses: int
    archived_courses: int
    
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    
    total_revenue: float
    average_rating: float
    total_reviews: int
    
    # Category breakdown
    courses_by_category: dict
    enrollments_by_category: dict
    revenue_by_category: dict
    
    # Level breakdown
    courses_by_level: dict
    enrollments_by_level: dict
    
    # Monthly statistics
    monthly_enrollments: dict
    monthly_revenue: dict

class CourseSearchFilters(BaseModel):
    """Schema for course search filters"""
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = None
    level: Optional[CourseLevel] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    is_free: Optional[bool] = None
    is_featured: Optional[bool] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    tags: Optional[List[str]] = None
    
    # Sort options
    sort_by: Optional[str] = Field(
        default="created_at",
        description="Sort field"
    )
    sort_order: Optional[str] = Field(
        default="desc",
        description="Sort order (asc/desc)"
    )
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

class CourseSearchResult(BaseModel):
    """Schema for course search results"""
    courses: List[CourseListItem]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    # Available filters for frontend
    available_categories: List[str]
    available_tags: List[str]
    price_range: dict
    rating_range: dict