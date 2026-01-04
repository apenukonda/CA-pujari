"""
Logging configuration for the E-Learning Platform API
Provides structured logging with different formats and levels
"""

import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'execution_time'):
            log_entry["execution_time"] = record.execution_time
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the message
        formatted = f"{color}[{timestamp}] {record.levelname:8} {record.name}: {record.getMessage()}{reset}"
        
        # Add file info for debugging
        if record.levelname == 'DEBUG':
            formatted += f" ({record.module}:{record.lineno})"
        
        return formatted


def setup_logging() -> None:
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    if settings.LOG_FILE:
        log_file_path = Path(settings.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Logging configuration
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "colored": {
                "()": ColoredFormatter,
            },
            "standard": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "colored" if settings.is_development else "json",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        },
        "root": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL
        }
    }
    
    # Add file handler if configured
    if settings.LOG_FILE:
        log_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "json",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8"
        }
        log_config["root"]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(log_config)
    
    # Set up specific loggers
    setup_application_loggers()


def setup_application_loggers() -> None:
    """Setup application-specific loggers"""
    
    # Database logger
    db_logger = logging.getLogger("app.database")
    db_logger.setLevel(logging.INFO)
    
    # Firebase logger
    firebase_logger = logging.getLogger("app.firebase")
    firebase_logger.setLevel(logging.INFO)
    
    # Security logger
    security_logger = logging.getLogger("app.security")
    security_logger.setLevel(logging.WARNING)
    
    # API logger
    api_logger = logging.getLogger("app.api")
    api_logger.setLevel(logging.INFO)
    
    # Payment logger
    payment_logger = logging.getLogger("app.payment")
    payment_logger.setLevel(logging.INFO)
    
    # Email logger
    email_logger = logging.getLogger("app.email")
    email_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(f"app.{name}")


def log_request(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    execution_time: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log API request details
    
    Args:
        logger: Logger instance
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        execution_time: Request execution time in seconds
        user_id: User ID (optional)
        request_id: Request ID (optional)
    """
    extra = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "execution_time": execution_time
    }
    
    if user_id:
        extra["user_id"] = user_id
    if request_id:
        extra["request_id"] = request_id
    
    if status_code >= 400:
        logger.warning(
            f"HTTP {status_code} {method} {endpoint} - {execution_time:.3f}s",
            extra=extra
        )
    else:
        logger.info(
            f"HTTP {status_code} {method} {endpoint} - {execution_time:.3f}s",
            extra=extra
        )


def log_auth_event(
    logger: logging.Logger,
    event: str,
    user_id: str,
    success: bool,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log authentication events
    
    Args:
        logger: Logger instance
        event: Auth event type (login, logout, token_verify, etc.)
        user_id: User ID
        success: Whether the operation was successful
        details: Additional event details
    """
    extra = {
        "event": event,
        "user_id": user_id,
        "success": success
    }
    
    if details:
        extra.update(details)
    
    level = logging.INFO if success else logging.WARNING
    status = "success" if success else "failed"
    
    logger.log(
        level,
        f"Auth event: {event} - {status}",
        extra=extra
    )


def log_payment_event(
    logger: logging.Logger,
    event: str,
    user_id: str,
    purchase_id: str,
    amount: float,
    currency: str,
    status: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log payment events
    
    Args:
        logger: Logger instance
        event: Payment event type
        user_id: User ID
        purchase_id: Purchase ID
        amount: Payment amount
        currency: Currency code
        status: Payment status
        details: Additional event details
    """
    extra = {
        "event": event,
        "user_id": user_id,
        "purchase_id": purchase_id,
        "amount": amount,
        "currency": currency,
        "status": status
    }
    
    if details:
        extra.update(details)
    
    logger.info(
        f"Payment event: {event} - {purchase_id} - {amount} {currency} - {status}",
        extra=extra
    )


def log_security_event(
    logger: logging.Logger,
    event: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log security events
    
    Args:
        logger: Logger instance
        event: Security event type
        user_id: User ID (optional)
        ip_address: Client IP address (optional)
        user_agent: User agent (optional)
        details: Additional event details
    """
    extra = {
        "event": event,
        "security": True
    }
    
    if user_id:
        extra["user_id"] = user_id
    if ip_address:
        extra["ip_address"] = ip_address
    if user_agent:
        extra["user_agent"] = user_agent
    if details:
        extra.update(details)
    
    logger.warning(
        f"Security event: {event}",
        extra=extra
    )


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__module__)


def create_request_logger(request_id: str) -> logging.Logger:
    """Create a logger with request context"""
    logger = logging.getLogger("app.request")
    logger = logging.LoggerAdapter(logger, {"request_id": request_id})
    return logger


def create_user_logger(user_id: str) -> logging.Logger:
    """Create a logger with user context"""
    logger = logging.getLogger("app.user")
    logger = logging.LoggerAdapter(logger, {"user_id": user_id})
    return logger