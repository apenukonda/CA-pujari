"""
Input validation and sanitization utilities for the E-Learning Platform
Provides comprehensive validation for user inputs and data integrity checks
"""

import re
import html
from typing import Any, Dict, List, Optional, Union, Type
from urllib.parse import urlparse
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

from app.constants.roles import UserRole
from app.constants.statuses import CourseStatus, WebinarStatus, PurchaseStatus


class ValidationError(Exception):
    """Custom validation error"""
    pass


class BaseValidator:
    """Base validator class with common validation methods"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML content to prevent XSS"""
        if not isinstance(text, str):
            return str(text)
        return html.escape(text.strip())
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not isinstance(filename, str):
            return "unnamed_file"
        
        # Remove dangerous characters and normalize
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        return sanitized[:255]  # Limit length
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present and not None"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = 1000, 
                             field_name: str = "field") -> str:
        """Validate string length and return sanitized value"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        value = value.strip()
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters")
        
        return value
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address"""
        if not isinstance(email, str):
            raise ValidationError("Email must be a string")
        
        email = email.strip().lower()
        try:
            validate_email(email)
            return email
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {str(e)}")
    
    @staticmethod
    def validate_phone_number(phone: str, country_code: str = "IN") -> str:
        """Validate phone number"""
        if not isinstance(phone, str):
            raise ValidationError("Phone number must be a string")
        
        phone = phone.strip()
        try:
            parsed_number = phonenumbers.parse(phone, country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Invalid phone number")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            raise ValidationError("Invalid phone number format")
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = None) -> str:
        """Validate URL format and scheme"""
        if not isinstance(url, str):
            raise ValidationError("URL must be a string")
        
        url = url.strip()
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValidationError("Invalid URL format")
            
            if allowed_schemes and parsed.scheme not in allowed_schemes:
                raise ValidationError(f"URL scheme '{parsed.scheme}' not allowed")
            
            return url
        except Exception:
            raise ValidationError("Invalid URL format")
    
    @staticmethod
    def validate_choice(value: Any, choices: List[Any], field_name: str = "field") -> Any:
        """Validate that value is in allowed choices"""
        if value not in choices:
            raise ValidationError(f"{field_name} must be one of: {', '.join(map(str, choices))}")
        return value
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: float = None, 
                              max_val: float = None, field_name: str = "field") -> Union[int, float]:
        """Validate numeric value is within range"""
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{field_name} must be a number")
        
        if min_val is not None and value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        if max_val is not None and value > max_val:
            raise ValidationError(f"{field_name} must not exceed {max_val}")
        
        return value
    
    @staticmethod
    def validate_date_format(date_str: str, formats: List[str] = None) -> str:
        """Validate date string format"""
        if not isinstance(date_str, str):
            raise ValidationError("Date must be a string")
        
        if not formats:
            formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]
        
        date_str = date_str.strip()
        for fmt in formats:
            try:
                from datetime import datetime
                datetime.strptime(date_str, fmt)
                return date_str
            except ValueError:
                continue
        
        raise ValidationError(f"Date must be in one of these formats: {', '.join(formats)}")


class UserValidator(BaseValidator):
    """User-specific validation"""
    
    def validate_user_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate user registration/update data"""
        validated_data = {}
        
        # Required fields for registration
        if not is_update:
            self.validate_required_fields(data, ['email', 'full_name'])
        
        # Email validation
        if 'email' in data:
            validated_data['email'] = self.validate_email(data['email'])
        
        # Full name validation
        if 'full_name' in data:
            validated_data['full_name'] = self.validate_string_length(
                data['full_name'], min_length=2, max_length=100, field_name="full_name"
            )
        
        # Phone validation (optional)
        if 'phone' in data and data['phone']:
            validated_data['phone'] = self.validate_phone_number(data['phone'])
        
        # Bio validation (optional)
        if 'bio' in data:
            validated_data['bio'] = self.validate_string_length(
                data['bio'], max_length=500, field_name="bio"
            )
        
        # Role validation (for admin operations)
        if 'role' in data:
            validated_data['role'] = self.validate_choice(
                data['role'], 
                [UserRole.ADMIN, UserRole.USER], 
                field_name="role"
            )
        
        return validated_data


class CourseValidator(BaseValidator):
    """Course-specific validation"""
    
    def validate_course_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate course creation/update data"""
        validated_data = {}
        
        # Required fields
        if not is_update:
            self.validate_required_fields(data, ['title', 'description', 'price'])
        
        # Title validation
        if 'title' in data:
            validated_data['title'] = self.validate_string_length(
                data['title'], min_length=3, max_length=200, field_name="title"
            )
        
        # Description validation
        if 'description' in data:
            validated_data['description'] = self.validate_string_length(
                data['description'], min_length=10, max_length=2000, field_name="description"
            )
        
        # Price validation
        if 'price' in data:
            validated_data['price'] = self.validate_numeric_range(
                data['price'], min_val=0, field_name="price"
            )
        
        # Duration validation (optional)
        if 'duration_hours' in data and data['duration_hours']:
            validated_data['duration_hours'] = self.validate_numeric_range(
                data['duration_hours'], min_val=0.5, max_val=1000, field_name="duration_hours"
            )
        
        # Status validation
        if 'status' in data:
            validated_data['status'] = self.validate_choice(
                data['status'],
                [CourseStatus.DRAFT, CourseStatus.PUBLISHED, CourseStatus.ARCHIVED],
                field_name="status"
            )
        
        # Prerequisites validation (optional)
        if 'prerequisites' in data and data['prerequisites']:
            if not isinstance(data['prerequisites'], list):
                raise ValidationError("Prerequisites must be a list")
            validated_data['prerequisites'] = [
                self.validate_string_length(prereq, max_length=200, field_name="prerequisite")
                for prereq in data['prerequisites']
            ]
        
        # Learning objectives validation (optional)
        if 'learning_objectives' in data and data['learning_objectives']:
            if not isinstance(data['learning_objectives'], list):
                raise ValidationError("Learning objectives must be a list")
            validated_data['learning_objectives'] = [
                self.validate_string_length(obj, max_length=300, field_name="learning_objective")
                for obj in data['learning_objectives']
            ]
        
        return validated_data


class WebinarValidator(BaseValidator):
    """Webinar-specific validation"""
    
    def validate_webinar_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate webinar creation/update data"""
        validated_data = {}
        
        # Required fields
        if not is_update:
            self.validate_required_fields(data, ['title', 'description', 'start_time', 'end_time'])
        
        # Title validation
        if 'title' in data:
            validated_data['title'] = self.validate_string_length(
                data['title'], min_length=3, max_length=200, field_name="title"
            )
        
        # Description validation
        if 'description' in data:
            validated_data['description'] = self.validate_string_length(
                data['description'], min_length=10, max_length=2000, field_name="description"
            )
        
        # Date/time validation
        for datetime_field in ['start_time', 'end_time']:
            if datetime_field in data:
                validated_data[datetime_field] = self.validate_date_format(data[datetime_field])
        
        # Time validation (start should be before end)
        if 'start_time' in validated_data and 'end_time' in validated_data:
            from datetime import datetime
            start_dt = datetime.fromisoformat(validated_data['start_time'])
            end_dt = datetime.fromisoformat(validated_data['end_time'])
            if start_dt >= end_dt:
                raise ValidationError("Start time must be before end time")
        
        # Price validation
        if 'price' in data:
            validated_data['price'] = self.validate_numeric_range(
                data['price'], min_val=0, field_name="price"
            )
        
        # Capacity validation (optional)
        if 'max_capacity' in data and data['max_capacity']:
            validated_data['max_capacity'] = self.validate_numeric_range(
                data['max_capacity'], min_val=1, max_val=10000, field_name="max_capacity"
            )
        
        # Meeting URL validation (optional)
        if 'meeting_url' in data and data['meeting_url']:
            validated_data['meeting_url'] = self.validate_url(
                data['meeting_url'], 
                allowed_schemes=['https', 'http']
            )
        
        # Status validation
        if 'status' in data:
            validated_data['status'] = self.validate_choice(
                data['status'],
                [WebinarStatus.SCHEDULED, WebinarStatus.CANCELLED, WebinarStatus.COMPLETED],
                field_name="status"
            )
        
        return validated_data


class PurchaseValidator(BaseValidator):
    """Purchase-specific validation"""
    
    def validate_purchase_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate purchase data"""
        validated_data = {}
        
        # Required fields
        if not is_update:
            self.validate_required_fields(data, ['user_id', 'item_type', 'item_id', 'amount'])
        
        # User ID validation
        if 'user_id' in data:
            validated_data['user_id'] = self.validate_string_length(
                data['user_id'], min_length=1, max_length=128, field_name="user_id"
            )
        
        # Item type validation
        if 'item_type' in data:
            validated_data['item_type'] = self.validate_choice(
                data['item_type'],
                ['course', 'webinar'],
                field_name="item_type"
            )
        
        # Item ID validation
        if 'item_id' in data:
            validated_data['item_id'] = self.validate_string_length(
                data['item_id'], min_length=1, max_length=128, field_name="item_id"
            )
        
        # Amount validation
        if 'amount' in data:
            validated_data['amount'] = self.validate_numeric_range(
                data['amount'], min_val=0.01, field_name="amount"
            )
        
        # Currency validation
        if 'currency' in data:
            validated_data['currency'] = self.validate_choice(
                data['currency'],
                ['USD', 'INR', 'EUR'],
                field_name="currency"
            )
        
        # Status validation
        if 'status' in data:
            validated_data['status'] = self.validate_choice(
                data['status'],
                [PurchaseStatus.PENDING, PurchaseStatus.COMPLETED, PurchaseStatus.FAILED, PurchaseStatus.REFUNDED],
                field_name="status"
            )
        
        return validated_data


class FeedbackValidator(BaseValidator):
    """Feedback-specific validation"""
    
    def validate_feedback_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate feedback data"""
        validated_data = {}
        
        # Required fields
        if not is_update:
            self.validate_required_fields(data, ['user_id', 'item_type', 'item_id', 'rating'])
        
        # User ID validation
        if 'user_id' in data:
            validated_data['user_id'] = self.validate_string_length(
                data['user_id'], min_length=1, max_length=128, field_name="user_id"
            )
        
        # Item type validation
        if 'item_type' in data:
            validated_data['item_type'] = self.validate_choice(
                data['item_type'],
                ['course', 'webinar'],
                field_name="item_type"
            )
        
        # Item ID validation
        if 'item_id' in data:
            validated_data['item_id'] = self.validate_string_length(
                data['item_id'], min_length=1, max_length=128, field_name="item_id"
            )
        
        # Rating validation
        if 'rating' in data:
            validated_data['rating'] = self.validate_numeric_range(
                data['rating'], min_val=1, max_val=5, field_name="rating"
            )
        
        # Comment validation (optional)
        if 'comment' in data:
            validated_data['comment'] = self.validate_string_length(
                data['comment'], max_length=1000, field_name="comment"
            )
        
        return validated_data


class DoubtValidator(BaseValidator):
    """Doubt/Q&A-specific validation"""
    
    def validate_doubt_data(self, data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate doubt data"""
        validated_data = {}
        
        # Required fields
        if not is_update:
            self.validate_required_fields(data, ['user_id', 'title', 'description'])
        
        # User ID validation
        if 'user_id' in data:
            validated_data['user_id'] = self.validate_string_length(
                data['user_id'], min_length=1, max_length=128, field_name="user_id"
            )
        
        # Title validation
        if 'title' in data:
            validated_data['title'] = self.validate_string_length(
                data['title'], min_length=5, max_length=200, field_name="title"
            )
        
        # Description validation
        if 'description' in data:
            validated_data['description'] = self.validate_string_length(
                data['description'], min_length=10, max_length=2000, field_name="description"
            )
        
        # Item type validation (optional)
        if 'item_type' in data and data['item_type']:
            validated_data['item_type'] = self.validate_choice(
                data['item_type'],
                ['course', 'webinar', 'general'],
                field_name="item_type"
            )
        
        # Item ID validation (optional)
        if 'item_id' in data and data['item_id']:
            validated_data['item_id'] = self.validate_string_length(
                data['item_id'], min_length=1, max_length=128, field_name="item_id"
            )
        
        # Priority validation (optional)
        if 'priority' in data and data['priority']:
            validated_data['priority'] = self.validate_choice(
                data['priority'],
                ['low', 'medium', 'high', 'urgent'],
                field_name="priority"
            )
        
        # Status validation (optional)
        if 'status' in data and data['status']:
            validated_data['status'] = self.validate_choice(
                data['status'],
                ['open', 'in_progress', 'resolved', 'closed'],
                field_name="status"
            )
        
        return validated_data


# Create validator instances
user_validator = UserValidator()
course_validator = CourseValidator()
webinar_validator = WebinarValidator()
purchase_validator = PurchaseValidator()
feedback_validator = FeedbackValidator()
doubt_validator = DoubtValidator()


def validate_pagination_params(skip: int = 0, limit: int = 10, max_limit: int = 100) -> tuple[int, int]:
    """Validate pagination parameters"""
    if not isinstance(skip, int) or skip < 0:
        raise ValidationError("Skip must be a non-negative integer")
    if not isinstance(limit, int) or limit < 1:
        raise ValidationError("Limit must be a positive integer")
    if limit > max_limit:
        raise ValidationError(f"Limit cannot exceed {max_limit}")
    
    return skip, limit


def validate_search_query(query: str, max_length: int = 100) -> str:
    """Validate search query"""
    if not isinstance(query, str):
        raise ValidationError("Search query must be a string")
    
    query = query.strip()
    if len(query) > max_length:
        raise ValidationError(f"Search query cannot exceed {max_length} characters")
    
    # Sanitize search query
    query = re.sub(r'[<>"\']', '', query)
    return query


def validate_sort_params(sort_by: str, sort_order: str = "asc", allowed_fields: List[str] = None) -> tuple[str, str]:
    """Validate sorting parameters"""
    if not isinstance(sort_by, str) or not sort_by.strip():
        raise ValidationError("Sort field is required")
    
    if sort_order not in ["asc", "desc"]:
        raise ValidationError("Sort order must be 'asc' or 'desc'")
    
    if allowed_fields and sort_by not in allowed_fields:
        raise ValidationError(f"Sort field must be one of: {', '.join(allowed_fields)}")
    
    return sort_by.strip(), sort_order