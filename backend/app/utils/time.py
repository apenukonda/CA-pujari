"""
Time utilities for the E-Learning Platform
Provides common date/time operations and formatting
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
from zoneinfo import ZoneInfo
import pytz

from app.constants.statuses import (
    WebinarStatus, CourseStatus, PurchaseStatus
)


def get_current_utc_time() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


def get_current_timezone() -> ZoneInfo:
    """Get system timezone"""
    return ZoneInfo("Asia/Calcutta")  # Can be made configurable


def convert_to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC"""
    if dt.tzinfo is None:
        # Assume naive datetime is in system timezone
        tz = get_current_timezone()
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(timezone.utc)


def convert_from_utc(dt: datetime, timezone_name: str = "Asia/Calcutta") -> datetime:
    """Convert UTC datetime to specified timezone"""
    target_tz = ZoneInfo(timezone_name)
    return dt.astimezone(target_tz)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    if dt.tzinfo:
        dt = convert_from_utc(dt)
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string"""
    return datetime.strptime(date_str, format_str)


def is_webinar_active(start_time: datetime, end_time: datetime, buffer_minutes: int = 15) -> bool:
    """Check if webinar is currently active (with buffer)"""
    now = get_current_utc_time()
    start_buffer = start_time - timedelta(minutes=buffer_minutes)
    end_buffer = end_time + timedelta(minutes=buffer_minutes)
    
    return start_buffer <= now <= end_buffer


def is_webinar_upcoming(start_time: datetime, buffer_minutes: int = 30) -> bool:
    """Check if webinar is upcoming (within buffer time)"""
    now = get_current_utc_time()
    start_buffer = start_time - timedelta(minutes=buffer_minutes)
    
    return now < start_buffer and now >= start_buffer


def is_purchase_expired(purchase_date: datetime, validity_days: int) -> bool:
    """Check if purchase access has expired"""
    if validity_days <= 0:
        return False
    
    expiry_date = purchase_date + timedelta(days=validity_days)
    return get_current_utc_time() > expiry_date


def get_webinar_status(start_time: datetime, end_time: datetime) -> WebinarStatus:
    """Determine webinar status based on time"""
    now = get_current_utc_time()
    
    if now < start_time:
        return WebinarStatus.SCHEDULED
    elif start_time <= now <= end_time:
        return WebinarStatus.ONGOING
    elif now > end_time:
        return WebinarStatus.COMPLETED
    else:
        return WebinarStatus.CANCELLED


def get_course_status(start_date: Optional[datetime], end_date: Optional[datetime]) -> CourseStatus:
    """Determine course status based on dates"""
    now = get_current_utc_time()
    
    if not start_date and not end_date:
        return CourseStatus.DRAFT
    
    if start_date and now < start_date:
        return CourseStatus.UPCOMING
    
    if end_date and now > end_date:
        return CourseStatus.COMPLETED
    
    if start_date and end_date and start_date <= now <= end_date:
        return CourseStatus.ACTIVE
    
    return CourseStatus.DRAFT


def calculate_duration(start_time: datetime, end_time: datetime) -> timedelta:
    """Calculate duration between two datetimes"""
    return end_time - start_time


def format_duration(duration: timedelta) -> str:
    """Format duration to human readable string"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def get_time_until(target_time: datetime) -> timedelta:
    """Get time remaining until target datetime"""
    now = get_current_utc_time()
    return target_time - now


def is_business_hours(dt: Optional[datetime] = None, 
                     start_hour: int = 9, 
                     end_hour: int = 17) -> bool:
    """Check if datetime is within business hours"""
    if dt is None:
        dt = get_current_utc_time()
    
    local_time = convert_from_utc(dt)
    hour = local_time.hour
    
    return start_hour <= hour < end_hour


def get_week_boundaries(dt: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Get start and end of week (Monday to Sunday)"""
    if dt is None:
        dt = get_current_utc_time()
    
    # Get Monday (start of week)
    days_since_monday = dt.weekday()
    start_of_week = dt - timedelta(days=days_since_monday)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get Sunday (end of week)
    end_of_week = start_of_week + timedelta(days=6)
    end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_of_week, end_of_week


def get_month_boundaries(dt: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """Get start and end of month"""
    if dt is None:
        dt = get_current_utc_time()
    
    # First day of month
    start_of_month = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Last day of month
    if dt.month == 12:
        next_month = dt.replace(year=dt.year + 1, month=1, day=1)
    else:
        next_month = dt.replace(month=dt.month + 1, day=1)
    
    end_of_month = next_month - timedelta(days=1)
    end_of_month = end_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_of_month, end_of_month


def format_relative_time(target_time: datetime) -> str:
    """Format time as relative (e.g., '2 hours ago', 'in 3 days')"""
    now = get_current_utc_time()
    diff = target_time - now
    
    if diff.days > 30:
        return target_time.strftime("%B %d, %Y")
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} {'from now' if diff.days > 0 else 'ago'}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} {'from now' if hours > 0 else 'ago'}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} {'from now' if minutes > 0 else 'ago'}"
    else:
        return "just now" if abs(diff.seconds) < 10 else f"{abs(diff.seconds)} seconds {'from now' if diff.seconds > 0 else 'ago'}"