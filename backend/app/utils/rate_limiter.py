"""
Rate Limiting Utility
Supports both Redis-based and in-memory rate limiting for API protection
"""

import asyncio
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
import redis.asyncio as redis
from app.core.config import settings


class RateLimiter:
    """
    Rate limiter supporting both Redis and in-memory storage
    Provides sliding window and fixed window rate limiting strategies
    """
    
    def __init__(self, use_redis: bool = None):
        """
        Initialize rate limiter
        
        Args:
            use_redis: Whether to use Redis (auto-detect from config if None)
        """
        self.use_redis = use_redis if use_redis is not None else bool(settings.REDIS_URL)
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, deque] = defaultdict(deque)
        
        # Initialize Redis client if using Redis
        if self.use_redis:
            self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(settings.REDIS_URL)
        except Exception as e:
            print(f"Failed to initialize Redis: {e}. Falling back to in-memory storage.")
            self.use_redis = False
            self.redis_client = None
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 60,
        strategy: str = "sliding"
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Check if rate limit is exceeded
        
        Args:
            key: Unique identifier for rate limiting (e.g., user_id, IP)
            limit: Maximum requests allowed
            window: Time window in seconds
            strategy: Rate limiting strategy ("sliding" or "fixed")
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        current_time = int(time.time())
        
        if self.use_redis and self.redis_client:
            return await self._check_redis_rate_limit(
                key, limit, window, strategy, current_time
            )
        else:
            return await self._check_memory_rate_limit(
                key, limit, window, strategy, current_time
            )
    
    async def _check_redis_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        strategy: str,
        current_time: int
    ) -> Tuple[bool, Optional[Dict]]:
        """Check rate limit using Redis"""
        try:
            redis_key = f"rate_limit:{key}:{strategy}:{window}"
            
            if strategy == "sliding":
                return await self._sliding_window_redis(redis_key, limit, window, current_time)
            else:
                return await self._fixed_window_redis(redis_key, limit, window, current_time)
                
        except Exception as e:
            print(f"Redis rate limit check failed: {e}. Falling back to memory.")
            return await self._check_memory_rate_limit(key, limit, window, strategy, current_time)
    
    async def _check_memory_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        strategy: str,
        current_time: int
    ) -> Tuple[bool, Optional[Dict]]:
        """Check rate limit using in-memory storage"""
        deque_obj = self.memory_store[key]
        
        # Remove expired entries
        cutoff_time = current_time - window
        while deque_obj and deque_obj[0] < cutoff_time:
            deque_obj.popleft()
        
        current_requests = len(deque_obj)
        is_allowed = current_requests < limit
        
        if is_allowed:
            deque_obj.append(current_time)
        
        remaining = max(0, limit - current_requests - (1 if is_allowed else 0))
        reset_time = current_time + window
        
        rate_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": 0 if is_allowed else window
        }
        
        return is_allowed, rate_info
    
    async def _sliding_window_redis(
        self,
        redis_key: str,
        limit: int,
        window: int,
        current_time: int
    ) -> Tuple[bool, Optional[Dict]]:
        """Sliding window rate limiting with Redis"""
        pipeline = self.redis_client.pipeline()
        
        # Remove old entries
        cutoff = current_time - window
        pipeline.zremrangebyscore(redis_key, 0, cutoff)
        
        # Count current requests
        pipeline.zcard(redis_key)
        results = await pipeline.execute()
        current_requests = results[1]
        
        is_allowed = current_requests < limit
        
        if is_allowed:
            # Add current request
            pipeline.zadd(redis_key, {str(current_time): current_time})
            pipeline.expire(redis_key, window)
            await pipeline.execute()
        
        remaining = max(0, limit - current_requests - (1 if is_allowed else 0))
        reset_time = current_time + window
        
        rate_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": 0 if is_allowed else window
        }
        
        return is_allowed, rate_info
    
    async def _fixed_window_redis(
        self,
        redis_key: str,
        limit: int,
        window: int,
        current_time: int
    ) -> Tuple[bool, Optional[Dict]]:
        """Fixed window rate limiting with Redis"""
        window_key = f"{redis_key}:{current_time // window}"
        
        pipe = self.redis_client.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, window)
        results = await pipe.execute()
        
        current_requests = results[0]
        is_allowed = current_requests <= limit
        
        remaining = max(0, limit - current_requests + (1 if is_allowed else 0))
        reset_time = (current_time // window + 1) * window
        
        rate_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": 0 if is_allowed else (reset_time - current_time)
        }
        
        return is_allowed, rate_info
    
    async def get_rate_limit_status(
        self,
        key: str,
        limit: int,
        window: int = 60,
        strategy: str = "sliding"
    ) -> Dict:
        """Get current rate limit status without incrementing"""
        current_time = int(time.time())
        
        if self.use_redis and self.redis_client:
            return await self._get_redis_status(key, limit, window, strategy, current_time)
        else:
            return await self._get_memory_status(key, limit, window, strategy, current_time)
    
    async def _get_redis_status(
        self,
        key: str,
        limit: int,
        window: int,
        strategy: str,
        current_time: int
    ) -> Dict:
        """Get rate limit status from Redis"""
        try:
            redis_key = f"rate_limit:{key}:{strategy}:{window}"
            
            if strategy == "sliding":
                cutoff = current_time - window
                current_requests = await self.redis_client.zcount(redis_key, cutoff, current_time)
            else:
                window_key = f"{redis_key}:{current_time // window}"
                current_requests = await self.redis_client.get(window_key) or 0
                current_requests = int(current_requests)
            
            remaining = max(0, limit - current_requests)
            reset_time = current_time + window
            
            return {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": 0
            }
        except Exception as e:
            return await self._get_memory_status(key, limit, window, strategy, current_time)
    
    async def _get_memory_status(
        self,
        key: str,
        limit: int,
        window: int,
        strategy: str,
        current_time: int
    ) -> Dict:
        """Get rate limit status from memory"""
        deque_obj = self.memory_store[key]
        cutoff_time = current_time - window
        
        # Count non-expired entries
        current_requests = sum(1 for ts in deque_obj if ts >= cutoff_time)
        remaining = max(0, limit - current_requests)
        reset_time = current_time + window
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": 0
        }
    
    async def reset_rate_limit(self, key: str, strategy: str = None, window: int = None):
        """Reset rate limit for a specific key"""
        if strategy and window:
            redis_key = f"rate_limit:{key}:{strategy}:{window}"
            if self.use_redis and self.redis_client:
                await self.redis_client.delete(redis_key)
        
        # Clear from memory
        if key in self.memory_store:
            del self.memory_store[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


# Convenience functions for common use cases
async def check_user_rate_limit(user_id: str, endpoint: str, limit: int, window: int = 60) -> Tuple[bool, Optional[Dict]]:
    """Check rate limit for a user"""
    key = f"user:{user_id}:{endpoint}"
    return await rate_limiter.check_rate_limit(key, limit, window)


async def check_ip_rate_limit(ip_address: str, endpoint: str, limit: int, window: int = 60) -> Tuple[bool, Optional[Dict]]:
    """Check rate limit for an IP address"""
    key = f"ip:{ip_address}:{endpoint}"
    return await rate_limiter.check_rate_limit(key, limit, window)


# Rate limit decorators
def rate_limit(limit: int, window: int = 60, strategy: str = "sliding", key_func=None):
    """
    Rate limiting decorator for FastAPI endpoints
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        strategy: Rate limiting strategy
        key_func: Function to generate rate limit key from request
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            from fastapi import Request
            
            # Find request object in arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to get from kwargs
                request = kwargs.get('request')
            
            if not request:
                return await func(*args, **kwargs)
            
            # Generate rate limit key
            if key_func:
                key = key_func(request)
            else:
                # Default key: user_id if available, otherwise IP
                user_id = getattr(request.state, 'user_id', None)
                if user_id:
                    key = f"user:{user_id}:{request.url.path}"
                else:
                    key = f"ip:{request.client.host}:{request.url.path}"
            
            # Check rate limit
            is_allowed, rate_info = await rate_limiter.check_rate_limit(key, limit, window, strategy)
            
            if not is_allowed:
                from fastapi import HTTPException
                from fastapi.status import HTTP_429_TOO_MANY_REQUESTS
                
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": rate_info.get("retry_after", window) if rate_info else window
                    },
                    headers={"Retry-After": str(rate_info.get("retry_after", window))} if rate_info else None
                )
            
            # Add rate limit info to request state
            request.state.rate_limit_info = rate_info
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator