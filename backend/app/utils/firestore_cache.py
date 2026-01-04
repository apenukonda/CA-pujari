"""
Firestore Caching System

This module provides an intelligent caching system for Firestore data to improve performance
and reduce database load for frequently accessed content.
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import logging

from app.utils.logging_utils import get_logger

logger = get_logger(__name__)


class FirestoreCache:
    """
    Intelligent caching system for Firestore operations with automatic invalidation.
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        """
        Initialize the cache system.
        
        Args:
            default_ttl: Default time-to-live for cached items in seconds
        """
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
        self.access_patterns: Dict[str, int] = {}
        self.invalidation_rules: Dict[str, Callable] = {}
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }
    
    def _generate_cache_key(self, collection: str, operation: str, **kwargs) -> str:
        """
        Generate a unique cache key based on collection, operation, and parameters.
        
        Args:
            collection: Firestore collection name
            operation: Operation type (get, list, query)
            **kwargs: Parameters that affect the query result
            
        Returns:
            Unique cache key string
        """
        # Create a sorted representation of parameters
        params = sorted(kwargs.items())
        param_str = json.dumps(params, sort_keys=True)
        
        # Generate hash for the cache key
        key_data = f"{collection}:{operation}:{param_str}"
        cache_key = hashlib.md5(key_data.encode()).hexdigest()
        
        return cache_key
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            cache_entry: Cache entry dictionary
            
        Returns:
            True if expired, False otherwise
        """
        return time.time() > cache_entry['expires_at']
    
    def _evict_expired(self):
        """Remove all expired entries from the cache."""
        expired_keys = [
            key for key, entry in self.cache.items() 
            if self._is_expired(entry)
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats['evictions'] += 1
        
        if expired_keys:
            logger.debug(f"Evicted {len(expired_keys)} expired cache entries")
    
    def _update_access_pattern(self, key: str):
        """Update access pattern tracking for LRU eviction."""
        self.access_patterns[key] = self.access_patterns.get(key, 0) + 1
    
    def get(
        self, 
        collection: str, 
        operation: str, 
        ttl: Optional[int] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Retrieve data from cache.
        
        Args:
            collection: Firestore collection name
            operation: Operation type
            ttl: Custom TTL for this operation
            **kwargs: Parameters that were used to generate the cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_cache_key(collection, operation, **kwargs)
        
        # Check if entry exists and is not expired
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            
            if not self._is_expired(cache_entry):
                self._update_access_pattern(cache_key)
                self.stats['hits'] += 1
                logger.debug(f"Cache hit: {cache_key}")
                return cache_entry['data']
            else:
                # Remove expired entry
                del self.cache[cache_key]
                if cache_key in self.access_patterns:
                    del self.access_patterns[cache_key]
        
        self.stats['misses'] += 1
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    def set(
        self, 
        data: Any, 
        collection: str, 
        operation: str, 
        ttl: Optional[int] = None,
        **kwargs
    ):
        """
        Store data in cache.
        
        Args:
            data: Data to cache
            collection: Firestore collection name
            operation: Operation type
            ttl: Custom TTL for this operation
            **kwargs: Parameters that were used to generate the cache key
        """
        cache_key = self._generate_cache_key(collection, operation, **kwargs)
        ttl = ttl or self.default_ttl
        
        self.cache[cache_key] = {
            'data': data,
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'collection': collection,
            'operation': operation,
            'parameters': kwargs
        }
        
        # Initialize access pattern
        if cache_key not in self.access_patterns:
            self.access_patterns[cache_key] = 0
        
        logger.debug(f"Cached data: {cache_key}")
    
    def invalidate_collection(self, collection: str):
        """
        Invalidate all cache entries for a specific collection.
        
        Args:
            collection: Collection name to invalidate
        """
        keys_to_remove = [
            key for key, entry in self.cache.items() 
            if entry['collection'] == collection
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
            if key in self.access_patterns:
                del self.access_patterns[key]
        
        self.stats['invalidations'] += len(keys_to_remove)
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries for collection: {collection}")
    
    def invalidate_by_pattern(self, collection: str, **pattern_params):
        """
        Invalidate cache entries matching a specific pattern.
        
        Args:
            collection: Collection name
            **pattern_params: Parameters that must match for invalidation
        """
        keys_to_remove = []
        
        for key, entry in self.cache.items():
            if (entry['collection'] == collection and 
                entry['operation'] in ['get', 'list', 'query']):
                
                # Check if parameters match the pattern
                matches = True
                for param, value in pattern_params.items():
                    if param not in entry['parameters'] or entry['parameters'][param] != value:
                        matches = False
                        break
                
                if matches:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
            if key in self.access_patterns:
                del self.access_patterns[key]
        
        self.stats['invalidations'] += len(keys_to_remove)
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries for pattern: {collection}:{pattern_params}")
    
    def add_invalidation_rule(self, collection: str, rule_func: Callable):
        """
        Add a custom invalidation rule.
        
        Args:
            collection: Collection name
            rule_func: Function that determines when to invalidate cache
        """
        self.invalidation_rules[collection] = rule_func
        logger.debug(f"Added invalidation rule for collection: {collection}")
    
    def apply_invalidation_rules(self, collection: str, document_id: str, document_data: Dict):
        """
        Apply invalidation rules for a specific document change.
        
        Args:
            collection: Collection name
            document_id: Document ID that was modified
            document_data: Updated document data
        """
        if collection in self.invalidation_rules:
            try:
                should_invalidate = self.invalidation_rules[collection](document_id, document_data)
                if should_invalidate:
                    self.invalidate_collection(collection)
                    logger.debug(f"Invalidation rule triggered for {collection}:{document_id}")
            except Exception as e:
                logger.error(f"Error applying invalidation rule for {collection}: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'entries': len(self.cache),
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'stats': self.stats.copy(),
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> Dict[str, int]:
        """
        Estimate memory usage of the cache.
        
        Returns:
            Dictionary with memory usage estimates in bytes
        """
        total_size = 0
        entry_sizes = {}
        
        for key, entry in self.cache.items():
            entry_size = len(json.dumps(entry))
            entry_sizes[key] = entry_size
            total_size += entry_size
        
        return {
            'total_bytes': total_size,
            'avg_entry_bytes': total_size / len(self.cache) if self.cache else 0,
            'entry_count': len(self.cache)
        }
    
    def cleanup(self):
        """Perform cache cleanup and maintenance."""
        initial_size = len(self.cache)
        self._evict_expired()
        
        # Log cleanup results
        final_size = len(self.cache)
        cleaned = initial_size - final_size
        
        if cleaned > 0:
            logger.info(f"Cache cleanup: removed {cleaned} expired entries")
        
        # Update statistics
        self.stats['evictions'] += cleaned
        
        return {
            'initial_size': initial_size,
            'final_size': final_size,
            'cleaned_entries': cleaned
        }
    
    def clear_all(self):
        """Clear all cached data."""
        self.cache.clear()
        self.access_patterns.clear()
        logger.info("Cache cleared completely")


# Global cache instance
firestore_cache = FirestoreCache()


# Decorator for automatic caching

def cached_firestore_operation(
    collection: str,
    operation: str,
    ttl: Optional[int] = None,
    invalidate_on: Optional[List[str]] = None
):
    """
    Decorator to automatically cache Firestore operations.
    
    Args:
        collection: Collection name for caching
        operation: Operation type (get, list, query)
        ttl: Time-to-live for cached data
        invalidate_on: List of operations that should invalidate this cache
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_params = {
                'args': args[1:],  # Skip self/cls
                'kwargs': kwargs
            }
            
            # Try to get from cache first
            cached_result = firestore_cache.get(
                collection=collection,
                operation=operation,
                ttl=ttl,
                **cache_params
            )
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            if result is not None:  # Only cache non-None results
                firestore_cache.set(
                    data=result,
                    collection=collection,
                    operation=operation,
                    ttl=ttl,
                    **cache_params
                )
            
            return result
        return wrapper
    return decorator


# Common invalidation rules

def user_invalidation_rule(document_id: str, document_data: Dict) -> bool:
    """
    Invalidation rule for user-related cache entries.
    """
    # Invalidate cache if user role, status, or profile data changes
    critical_fields = ['role', 'status', 'email', 'subscription_status']
    return any(field in document_data for field in critical_fields)


def course_invalidation_rule(document_id: str, document_data: Dict) -> bool:
    """
    Invalidation rule for course-related cache entries.
    """
    # Invalidate cache if course content, pricing, or availability changes
    critical_fields = ['title', 'description', 'price', 'status', 'is_public', 'category']
    return any(field in document_data for field in critical_fields)


def purchase_invalidation_rule(document_id: str, document_data: Dict) -> bool:
    """
    Invalidation rule for purchase-related cache entries.
    """
    # Always invalidate purchase cache when status changes
    return 'status' in document_data


# Initialize invalidation rules
firestore_cache.add_invalidation_rule('users', user_invalidation_rule)
firestore_cache.add_invalidation_rule('courses', course_invalidation_rule)
firestore_cache.add_invalidation_rule('purchases', purchase_invalidation_rule)
firestore_cache.add_invalidation_rule('webinars', course_invalidation_rule)  # Similar to courses


# Specialized cache decorators for common operations

def cache_user_profile(ttl: int = 300):
    """Cache user profile data."""
    return cached_firestore_operation(
        collection='users',
        operation='profile',
        ttl=ttl
    )


def cache_course_list(ttl: int = 600):
    """Cache course listings."""
    return cached_firestore_operation(
        collection='courses',
        operation='list',
        ttl=ttl
    )


def cache_user_purchases(ttl: int = 300):
    """Cache user purchase history."""
    return cached_firestore_operation(
        collection='purchases',
        operation='user_purchases',
        ttl=ttl
    )


def cache_course_statistics(ttl: int = 1800):
    """Cache course statistics (longer TTL as statistics change less frequently)."""
    return cached_firestore_operation(
        collection='courses',
        operation='statistics',
        ttl=ttl
    )


def cache_webinar_list(ttl: int = 600):
    """Cache webinar listings."""
    return cached_firestore_operation(
        collection='webinars',
        operation='list',
        ttl=ttl
    )


# Cache management utilities

def invalidate_user_cache(user_id: str):
    """
    Invalidate all cache entries related to a specific user.
    
    Args:
        user_id: User ID to invalidate cache for
    """
    firestore_cache.invalidate_by_pattern('users', **{'user_id': user_id})
    firestore_cache.invalidate_by_pattern('purchases', **{'user_id': user_id})
    firestore_cache.invalidate_by_pattern('feedback', **{'user_id': user_id})
    firestore_cache.invalidate_by_pattern('doubts', **{'user_id': user_id})
    logger.info(f"Invalidated cache for user: {user_id}")


def invalidate_course_cache(course_id: str):
    """
    Invalidate all cache entries related to a specific course.
    
    Args:
        course_id: Course ID to invalidate cache for
    """
    firestore_cache.invalidate_by_pattern('courses', **{'course_id': course_id})
    firestore_cache.invalidate_by_pattern('purchases', **{'course_id': course_id})
    firestore_cache.invalidate_by_pattern('feedback', **{'course_id': course_id})
    firestore_cache.invalidate_by_pattern('doubts', **{'course_id': course_id})
    logger.info(f"Invalidated cache for course: {course_id}")


def invalidate_webinar_cache(webinar_id: str):
    """
    Invalidate all cache entries related to a specific webinar.
    
    Args:
        webinar_id: Webinar ID to invalidate cache for
    """
    firestore_cache.invalidate_by_pattern('webinars', **{'webinar_id': webinar_id})
    firestore_cache.invalidate_by_pattern('purchases', **{'webinar_id': webinar_id})
    firestore_cache.invalidate_by_pattern('feedback', **{'webinar_id': webinar_id})
    firestore_cache.invalidate_by_pattern('doubts', **{'webinar_id': webinar_id})
    logger.info(f"Invalidated cache for webinar: {webinar_id}")


def get_cache_health_report() -> Dict[str, Any]:
    """
    Generate a comprehensive cache health report.
    
    Returns:
        Dictionary with cache health metrics and recommendations
    """
    stats = firestore_cache.get_cache_stats()
    
    recommendations = []
    
    # Analyze hit rate
    if stats['hit_rate'] < 70:
        recommendations.append({
            'type': 'low_hit_rate',
            'message': f"Cache hit rate is {stats['hit_rate']:.1f}%. Consider increasing TTL or improving cache key strategy.",
            'priority': 'high'
        })
    
    # Analyze memory usage
    memory_usage = stats['memory_usage']
    if memory_usage['total_bytes'] > 50 * 1024 * 1024:  # 50MB threshold
        recommendations.append({
            'type': 'high_memory_usage',
            'message': f"Cache is using {memory_usage['total_bytes'] / 1024 / 1024:.1f}MB. Consider implementing LRU eviction.",
            'priority': 'medium'
        })
    
    # Check for stale entries
    firestore_cache._evict_expired()
    if stats['evictions'] > 0:
        recommendations.append({
            'type': 'stale_entries',
            'message': f"{stats['evictions']} entries were evicted. Consider adjusting TTL values.",
            'priority': 'low'
        })
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'stats': stats,
        'recommendations': recommendations,
        'cache_size': len(firestore_cache.cache),
        'health_status': 'healthy' if not recommendations else 'needs_attention'
    }


# Background cache maintenance

def setup_cache_maintenance():
    """Setup background cache maintenance tasks."""
    import threading
    import schedule
    
    def maintenance_task():
        """Periodic cache maintenance task."""
        try:
            report = firestore_cache.cleanup()
            if report['cleaned_entries'] > 0:
                logger.info(f"Cache maintenance completed: {report}")
        except Exception as e:
            logger.error(f"Cache maintenance failed: {str(e)}")
    
    # Schedule maintenance every 5 minutes
    schedule.every(5).minutes.do(maintenance_task)
    
    # Run maintenance in background thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    logger.info("Cache maintenance scheduler started")