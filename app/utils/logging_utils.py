"""
Logging and monitoring utilities for request/response tracking.
Includes structured logging, performance monitoring, and security audit logging.
"""

import time
import json
import logging
import asyncio
from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone
from functools import wraps
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from ..core.logging import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with security considerations.
    """
    
    def __init__(self, app, logger_name: str = "request_logger"):
        super().__init__(app)
        self.logger = get_logger(logger_name)
        # Skip logging for these endpoints to avoid log spam
        self.skip_paths = {"/health", "/metrics", "/favicon.ico", "/docs", "/redoc"}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health checks and static endpoints
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        
        # Start timing
        start_time = time.time()
        
        # Extract request information
        request_info = self._extract_request_info(request, request_id)
        
        # Log incoming request
        self.logger.info("Incoming request", extra={
            "event_type": "request_start",
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request_info["client_ip"],
            "user_agent": request_info["user_agent"],
            "headers": self._sanitize_headers(dict(request.headers))
        })
        
        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            self.logger.info("Request completed successfully", extra={
                "event_type": "request_success",
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "response_size": self._get_response_size(response)
            })
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time
            
            # Log error with context
            self.logger.error("Request failed with exception", extra={
                "event_type": "request_error",
                "request_id": request_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "process_time_ms": round(process_time * 1000, 2)
            }, exc_info=True)
            
            raise
    
    def _extract_request_info(self, request: Request, request_id: str) -> Dict[str, Any]:
        """Extract relevant information from request."""
        # Get client IP (considering proxy headers)
        client_ip = request.client.host if request.client else "unknown"
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
        
        # Get user agent
        user_agent = request.headers.get("user-agent", "unknown")
        
        return {
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_id": request_id
        }
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers from logging."""
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "x-amz-security-token", "x-goog-authuser"
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_response_size(self, response: Response) -> Optional[int]:
        """Get response size in bytes."""
        if hasattr(response, 'body') and response.body:
            return len(response.body)
        return None


class SecurityAuditLogger:
    """
    Specialized logger for security-related events and audit trails.
    """
    
    def __init__(self):
        self.logger = get_logger("security_audit")
        self.failed_login_attempts = {}  # In-memory for demo, use Redis in production
        self.suspicious_ips = set()
    
    def log_authentication_attempt(self, email: str, success: bool, 
                                 client_ip: str, user_agent: str, 
                                 request_id: str):
        """Log authentication attempts for security monitoring."""
        event_data = {
            "event_type": "authentication_attempt",
            "email": email,
            "success": success,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if success:
            self.logger.info("User authentication successful", extra=event_data)
            # Reset failed attempts on successful login
            if email in self.failed_login_attempts:
                del self.failed_login_attempts[email]
        else:
            self.logger.warning("User authentication failed", extra=event_data)
            self._track_failed_attempt(email, client_ip)
    
    def log_authorization_failure(self, user_id: str, action: str, 
                                resource: str, client_ip: str, request_id: str):
        """Log authorization failures for access control monitoring."""
        self.logger.warning("Authorization failure", extra={
            "event_type": "authorization_failure",
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "client_ip": client_ip,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def log_admin_action(self, admin_id: str, action: str, target_resource: str,
                        details: Dict[str, Any], client_ip: str, request_id: str):
        """Log administrative actions for audit trails."""
        self.logger.info("Admin action performed", extra={
            "event_type": "admin_action",
            "admin_id": admin_id,
            "action": action,
            "target_resource": target_resource,
            "details": details,
            "client_ip": client_ip,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def log_payment_event(self, user_id: str, event_type: str, 
                         payment_details: Dict[str, Any], request_id: str):
        """Log payment-related events for financial audit."""
        self.logger.info("Payment event", extra={
            "event_type": "payment_event",
            "payment_event_type": event_type,
            "user_id": user_id,
            "payment_details": self._sanitize_payment_info(payment_details),
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def _track_failed_attempt(self, email: str, client_ip: str):
        """Track failed login attempts for rate limiting."""
        current_time = time.time()
        
        # Track by email
        if email not in self.failed_login_attempts:
            self.failed_login_attempts[email] = []
        
        self.failed_login_attempts[email].append(current_time)
        
        # Clean old attempts (older than 1 hour)
        cutoff_time = current_time - 3600
        self.failed_login_attempts[email] = [
            attempt for attempt in self.failed_login_attempts[email] 
            if attempt > cutoff_time
        ]
        
        # Flag suspicious activity
        if len(self.failed_login_attempts[email]) >= 5:
            self.suspicious_ips.add(client_ip)
            self.logger.warning("Suspicious login activity detected", extra={
                "event_type": "suspicious_activity",
                "email": email,
                "client_ip": client_ip,
                "failed_attempts_count": len(self.failed_login_attempts[email]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    def _sanitize_payment_info(self, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive payment information from logs."""
        sanitized = payment_details.copy()
        sensitive_keys = {"card_number", "cvv", "password", "pin"}
        
        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = "[REDACTED]"
        
        return sanitized
    
    def is_suspicious_ip(self, client_ip: str) -> bool:
        """Check if an IP is flagged for suspicious activity."""
        return client_ip in self.suspicious_ips


def log_function_call(func):
    """
    Decorator to log function calls with timing and parameters.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        func_logger = get_logger("function_calls")
        start_time = time.time()
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function call start
        func_logger.debug(f"Function called: {func_name}", extra={
            "event_type": "function_call_start",
            "function_name": func_name,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys())
        })
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log successful completion
            func_logger.debug(f"Function completed: {func_name}", extra={
                "event_type": "function_call_success",
                "function_name": func_name,
                "execution_time_ms": round(execution_time * 1000, 2)
            })
            
            return result
            
        except Exception as exc:
            execution_time = time.time() - start_time
            
            # Log error
            func_logger.error(f"Function failed: {func_name}", extra={
                "event_type": "function_call_error",
                "function_name": func_name,
                "execution_time_ms": round(execution_time * 1000, 2),
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }, exc_info=True)
            
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        func_logger = get_logger("function_calls")
        start_time = time.time()
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function call start
        func_logger.debug(f"Function called: {func_name}", extra={
            "event_type": "function_call_start",
            "function_name": func_name,
            "args_count": len(args),
            "kwargs_keys": list(kwargs.keys())
        })
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log successful completion
            func_logger.debug(f"Function completed: {func_name}", extra={
                "event_type": "function_call_success",
                "function_name": func_name,
                "execution_time_ms": round(execution_time * 1000, 2)
            })
            
            return result
            
        except Exception as exc:
            execution_time = time.time() - start_time
            
            # Log error
            func_logger.error(f"Function failed: {func_name}", extra={
                "event_type": "function_call_error",
                "function_name": func_name,
                "execution_time_ms": round(execution_time * 1000, 2),
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }, exc_info=True)
            
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class PerformanceMonitor:
    """
    Monitor and track application performance metrics.
    """
    
    def __init__(self):
        self.logger = get_logger("performance")
        self.request_times = []
        self.slow_requests = []
    
    def record_request_time(self, endpoint: str, method: str, 
                          execution_time: float, status_code: int):
        """Record request execution time for performance monitoring."""
        self.request_times.append({
            "endpoint": endpoint,
            "method": method,
            "execution_time": execution_time,
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Log slow requests (>2 seconds)
        if execution_time > 2.0:
            self.slow_requests.append({
                "endpoint": endpoint,
                "method": method,
                "execution_time": execution_time,
                "status_code": status_code,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            self.logger.warning("Slow request detected", extra={
                "event_type": "slow_request",
                "endpoint": endpoint,
                "method": method,
                "execution_time_ms": round(execution_time * 1000, 2),
                "status_code": status_code
            })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.request_times:
            return {"message": "No request data available"}
        
        execution_times = [req["execution_time"] for req in self.request_times]
        
        return {
            "total_requests": len(self.request_times),
            "average_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "slow_requests_count": len(self.slow_requests),
            "recent_slow_requests": self.slow_requests[-10:]  # Last 10 slow requests
        }
    
    def cleanup_old_data(self, hours: int = 24):
        """Clean up old performance data."""
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter recent requests
        self.request_times = [
            req for req in self.request_times
            if datetime.fromisoformat(req["timestamp"].replace("Z", "+00:00")).timestamp() > cutoff_time
        ]
        
        self.slow_requests = [
            req for req in self.slow_requests
            if datetime.fromisoformat(req["timestamp"].replace("Z", "+00:00")).timestamp() > cutoff_time
        ]


# Global instances
security_audit_logger = SecurityAuditLogger()
performance_monitor = PerformanceMonitor()


def get_request_logger() -> logging.Logger:
    """Get the request logger instance."""
    return get_logger("request_logger")


def get_security_logger() -> SecurityAuditLogger:
    """Get the security audit logger instance."""
    return security_audit_logger


def get_performance_monitor() -> PerformanceMonitor:
    """Get the performance monitor instance."""
    return performance_monitor