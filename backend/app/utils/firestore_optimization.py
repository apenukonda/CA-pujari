"""
Firestore Query Optimization and Indexing Utilities

This module provides utilities for optimizing Firestore queries, implementing proper indexing strategies,
and monitoring query performance for the backend application.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from collections import defaultdict
from functools import wraps
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, And, Or
from google.api_core import exceptions as google_exceptions

from app.utils.logging_utils import get_logger

logger = get_logger(__name__)


class FirestoreQueryOptimizer:
    """
    Handles Firestore query optimization, indexing strategies, and performance monitoring.
    """
    
    def __init__(self):
        self.db = firestore.Client()
        self.query_cache = {}
        self.performance_metrics = defaultdict(list)
        self.slow_query_threshold = 100  # milliseconds
    
    def create_composite_index_recommendations(self) -> Dict[str, List[str]]:
        """
        Generate composite index recommendations based on common query patterns.
        
        Returns:
            Dict mapping collection names to list of required composite indexes
        """
        recommendations = {
            'users': [
                # User queries with role and status filtering
                'role ASC, status ASC, created_at DESC',
                'email ASC, status ASC',
                'created_at DESC, role ASC',
                # Admin dashboard queries
                'created_at DESC, last_login_at DESC',
                'subscription_status ASC, created_at DESC'
            ],
            'courses': [
                # Course filtering and sorting
                'status ASC, created_at DESC',
                'category ASC, status ASC, created_at DESC',
                'price ASC, status ASC',
                'instructor_id ASC, status ASC, created_at DESC',
                # Public course queries
                'is_public ASC, status ASC, created_at DESC',
                'featured ASC, status ASC, created_at DESC'
            ],
            'webinars': [
                # Webinar scheduling and filtering
                'scheduled_at ASC, status ASC',
                'instructor_id ASC, status ASC, scheduled_at ASC',
                'category ASC, status ASC, scheduled_at DESC',
                # Registration queries
                'registration_deadline ASC, status ASC',
                'max_participants ASC, current_participants ASC'
            ],
            'purchases': [
                # Purchase tracking and analytics
                'user_id ASC, status ASC, created_at DESC',
                'course_id ASC, status ASC, created_at DESC',
                'webinar_id ASC, status ASC, created_at DESC',
                'payment_status ASC, created_at DESC',
                # Revenue analytics
                'created_at DESC, amount ASC',
                'user_id ASC, created_at DESC'
            ],
            'feedback': [
                # Feedback queries
                'user_id ASC, created_at DESC',
                'course_id ASC, rating ASC, created_at DESC',
                'webinar_id ASC, rating ASC, created_at DESC',
                'status ASC, created_at DESC',
                # Moderation queries
                'is_approved ASC, created_at DESC',
                'priority ASC, status ASC, created_at DESC'
            ],
            'doubts': [
                # Q&A system queries
                'user_id ASC, status ASC, created_at DESC',
                'course_id ASC, status ASC, priority ASC',
                'webinar_id ASC, status ASC, created_at DESC',
                # Admin moderation
                'assigned_to ASC, status ASC, created_at DESC',
                'is_resolved ASC, priority ASC, created_at DESC'
            ]
        }
        
        logger.info("Generated composite index recommendations for all collections")
        return recommendations
    
    def monitor_query_performance(self, collection: str, query_name: str):
        """
        Decorator to monitor Firestore query performance.
        
        Args:
            collection: Firestore collection name
            query_name: Name/identifier for the query
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Log performance metrics
                    self.performance_metrics[f"{collection}.{query_name}"].append({
                        'execution_time': execution_time,
                        'timestamp': time.time(),
                        'success': True
                    })
                    
                    # Alert on slow queries
                    if execution_time > self.slow_query_threshold:
                        logger.warning(
                            f"Slow query detected: {collection}.{query_name} - "
                            f"{execution_time:.2f}ms"
                        )
                    
                    return result
                    
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.performance_metrics[f"{collection}.{query_name}"].append({
                        'execution_time': execution_time,
                        'timestamp': time.time(),
                        'success': False,
                        'error': str(e)
                    })
                    
                    logger.error(
                        f"Query failed: {collection}.{query_name} - "
                        f"{execution_time:.2f}ms - Error: {str(e)}"
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def create_optimized_query(
        self, 
        collection: str,
        filters: Optional[List[Dict]] = None,
        order_by: Optional[List[Tuple[str, str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> firestore.CollectionReference:
        """
        Create an optimized Firestore query with proper filtering and ordering.
        
        Args:
            collection: Collection name
            filters: List of filter dictionaries with 'field', 'operator', 'value'
            order_by: List of (field, direction) tuples
            limit: Maximum number of results
            offset: Number of documents to skip
            
        Returns:
            Firestore query object
        """
        query = self.db.collection(collection)
        
        # Apply filters
        if filters:
            for filter_config in filters:
                query = query.where(
                    filter_config['field'],
                    filter_config['operator'],
                    filter_config['value']
                )
        
        # Apply ordering
        if order_by:
            for field, direction in order_by:
                query = query.order_by(field, direction=direction)
        
        # Apply pagination
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return query
    
    def batch_get_documents(
        self, 
        collection: str, 
        doc_ids: List[str],
        batch_size: int = 400
    ) -> Dict[str, Dict]:
        """
        Efficiently fetch multiple documents using batch operations.
        
        Args:
            collection: Collection name
            doc_ids: List of document IDs to fetch
            batch_size: Maximum documents per batch (Firestore limit is 400)
            
        Returns:
            Dictionary mapping document ID to document data
        """
        results = {}
        
        # Process in batches to avoid Firestore limits
        for i in range(0, len(doc_ids), batch_size):
            batch_ids = doc_ids[i:i + batch_size]
            
            try:
                # Use get_all() for batch document retrieval
                docs = self.db.collection(collection).get_all(batch_ids)
                
                for doc in docs:
                    if doc.exists:
                        results[doc.id] = doc.to_dict()
                    else:
                        logger.warning(f"Document {doc.id} not found in {collection}")
                        
            except google_exceptions.GoogleAPICallError as e:
                logger.error(f"Batch fetch failed for {collection}: {str(e)}")
                # Continue with other batches
                continue
        
        logger.info(
            f"Batch fetch completed: {len(results)}/{len(doc_ids)} documents retrieved from {collection}"
        )
        return results
    
    def create_efficient_pagination_query(
        self,
        collection: str,
        filters: Optional[List[Dict]] = None,
        order_by: List[Tuple[str, str]] = None,
        page_size: int = 20,
        cursor: Optional[str] = None,
        cursor_field: str = 'created_at'
    ) -> Tuple[firestore.Query, Optional[str]]:
        """
        Create an efficient pagination query using cursors.
        
        Args:
            collection: Collection name
            filters: List of filter dictionaries
            order_by: List of (field, direction) tuples
            page_size: Number of documents per page
            cursor: Cursor for pagination (document ID or timestamp)
            cursor_field: Field to use for cursor-based pagination
            
        Returns:
            Tuple of (query, next_cursor)
        """
        query = self.db.collection(collection)
        
        # Apply filters
        if filters:
            for filter_config in filters:
                query = query.where(
                    filter_config['field'],
                    filter_config['operator'],
                    filter_config['value']
                )
        
        # Add ordering for cursor pagination
        if order_by is None:
            order_by = [(cursor_field, firestore.Query.DESCENDING)]
        
        for field, direction in order_by:
            query = query.order_by(field, direction=direction)
        
        # Apply cursor if provided
        next_cursor = None
        if cursor:
            try:
                # Try to parse cursor as timestamp first
                if cursor_field == cursor_field:
                    cursor_time = firestore.SERVER_TIMESTAMP.from_json_dict(cursor)
                    if cursor_time:
                        query = query.start_after(cursor_time)
                        next_cursor = cursor
                    else:
                        # Fallback to document ID cursor
                        doc_ref = self.db.collection(collection).document(cursor)
                        query = query.start_after(doc_ref)
                        next_cursor = cursor
            except Exception:
                # Use document ID as fallback
                doc_ref = self.db.collection(collection).document(cursor)
                query = query.start_after(doc_ref)
                next_cursor = cursor
        
        # Apply limit
        query = query.limit(page_size)
        
        return query, next_cursor
    
    def optimize_collection_queries(self, collection: str) -> Dict[str, Any]:
        """
        Analyze and provide optimization recommendations for a collection.
        
        Args:
            collection: Collection name
            
        Returns:
            Dictionary with optimization recommendations
        """
        recommendations = {
            'collection': collection,
            'indexes': [],
            'query_patterns': [],
            'performance_tips': []
        }
        
        # Collection-specific optimizations
        if collection == 'users':
            recommendations.update({
                'indexes': [
                    {'fields': ['role', 'status', 'created_at'], 'direction': ['ASC', 'ASC', 'DESC']},
                    {'fields': ['email'], 'direction': ['ASC']},
                    {'fields': ['subscription_status', 'created_at'], 'direction': ['ASC', 'DESC']}
                ],
                'query_patterns': [
                    'Filter by role and status',
                    'Order by creation date',
                    'Search by email prefix'
                ],
                'performance_tips': [
                    'Use compound queries with role/status filters',
                    'Implement user caching for frequently accessed profiles',
                    'Use pagination for large user lists'
                ]
            })
        
        elif collection == 'courses':
            recommendations.update({
                'indexes': [
                    {'fields': ['status', 'category', 'created_at'], 'direction': ['ASC', 'ASC', 'DESC']},
                    {'fields': ['instructor_id', 'status', 'created_at'], 'direction': ['ASC', 'ASC', 'DESC']},
                    {'fields': ['is_public', 'status', 'featured'], 'direction': ['ASC', 'ASC', 'DESC']}
                ],
                'query_patterns': [
                    'Filter public courses by category',
                    'Instructor-specific course management',
                    'Featured course listings'
                ],
                'performance_tips': [
                    'Cache course content for public access',
                    'Use denormalized data for course statistics',
                    'Implement course search with text indexing'
                ]
            })
        
        elif collection == 'purchases':
            recommendations.update({
                'indexes': [
                    {'fields': ['user_id', 'status', 'created_at'], 'direction': ['ASC', 'ASC', 'DESC']},
                    {'fields': ['course_id', 'status', 'created_at'], 'direction': ['ASC', 'ASC', 'DESC']},
                    {'fields': ['payment_status', 'created_at'], 'direction': ['ASC', 'DESC']}
                ],
                'query_patterns': [
                    'User purchase history',
                    'Course revenue analytics',
                    'Payment status tracking'
                ],
                'performance_tips': [
                    'Use aggregation queries for analytics',
                    'Cache user access permissions',
                    'Implement purchase verification caching'
                ]
            })
        
        logger.info(f"Generated optimization recommendations for {collection}")
        return recommendations
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary containing performance metrics and recommendations
        """
        report = {
            'timestamp': time.time(),
            'query_metrics': {},
            'slow_queries': [],
            'recommendations': []
        }
        
        # Analyze performance metrics
        for query_name, metrics in self.performance_metrics.items():
            if not metrics:
                continue
                
            successful_metrics = [m for m in metrics if m['success']]
            if not successful_metrics:
                continue
                
            avg_time = sum(m['execution_time'] for m in successful_metrics) / len(successful_metrics)
            max_time = max(m['execution_time'] for m in successful_metrics)
            success_rate = len(successful_metrics) / len(metrics) * 100
            
            report['query_metrics'][query_name] = {
                'average_execution_time': avg_time,
                'max_execution_time': max_time,
                'success_rate': success_rate,
                'total_queries': len(metrics)
            }
            
            # Identify slow queries
            if avg_time > self.slow_query_threshold:
                report['slow_queries'].append({
                    'query': query_name,
                    'avg_time': avg_time,
                    'max_time': max_time
                })
        
        # Add optimization recommendations
        collections = ['users', 'courses', 'webinars', 'purchases', 'feedback', 'doubts']
        for collection in collections:
            report['recommendations'].append(
                self.optimize_collection_queries(collection)
            )
        
        logger.info("Generated Firestore performance report")
        return report
    
    def clear_cache(self):
        """Clear the query cache."""
        self.query_cache.clear()
        logger.info("Firestore query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cache_size': len(self.query_cache),
            'cached_queries': list(self.query_cache.keys()),
            'performance_metrics_count': sum(len(metrics) for metrics in self.performance_metrics.values())
        }


# Global optimizer instance
firestore_optimizer = FirestoreQueryOptimizer()


# Utility functions for common Firestore operations

def get_optimized_user_queries(
    filters: Optional[Dict] = None,
    order_by: str = 'created_at',
    limit: Optional[int] = None
) -> firestore.Query:
    """
    Create optimized user queries with proper indexing.
    
    Args:
        filters: Dictionary of field filters
        order_by: Field to order by
        limit: Maximum results
        
    Returns:
        Optimized Firestore query
    """
    return firestore_optimizer.create_optimized_query(
        collection='users',
        filters=[{'field': k, 'operator': '==', 'value': v} for k, v in (filters or {}).items()],
        order_by=[(order_by, firestore.Query.DESCENDING)],
        limit=limit
    )


def get_optimized_course_queries(
    filters: Optional[Dict] = None,
    order_by: str = 'created_at',
    limit: Optional[int] = None
) -> firestore.Query:
    """
    Create optimized course queries with proper indexing.
    
    Args:
        filters: Dictionary of field filters
        order_by: Field to order by
        limit: Maximum results
        
    Returns:
        Optimized Firestore query
    """
    return firestore_optimizer.create_optimized_query(
        collection='courses',
        filters=[{'field': k, 'operator': '==', 'value': v} for k, v in (filters or {}).items()],
        order_by=[(order_by, firestore.Query.DESCENDING)],
        limit=limit
    )


def get_optimized_purchase_queries(
    user_id: Optional[str] = None,
    course_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> firestore.Query:
    """
    Create optimized purchase queries with proper indexing.
    
    Args:
        user_id: Filter by user ID
        course_id: Filter by course ID
        status: Filter by purchase status
        limit: Maximum results
        
    Returns:
        Optimized Firestore query
    """
    filters = []
    if user_id:
        filters.append({'field': 'user_id', 'operator': '==', 'value': user_id})
    if course_id:
        filters.append({'field': 'course_id', 'operator': '==', 'value': course_id})
    if status:
        filters.append({'field': 'status', 'operator': '==', 'value': status})
    
    return firestore_optimizer.create_optimized_query(
        collection='purchases',
        filters=filters,
        order_by=[('created_at', firestore.Query.DESCENDING)],
        limit=limit
    )


def monitor_firestore_operation(collection: str, operation: str):
    """
    Decorator to monitor Firestore operations.
    
    Args:
        collection: Collection name
        operation: Operation type (get, create, update, delete)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            query_name = f"{operation}_{collection}"
            return firestore_optimizer.monitor_query_performance(collection, query_name)(func)(*args, **kwargs)
        return wrapper
    return decorator


# Index management functions

def create_single_field_indexes():
    """
    Create recommended single-field indexes.
    
    Returns:
        Dictionary of collections and their recommended single-field indexes
    """
    single_field_indexes = {
        'users': ['email', 'role', 'status', 'created_at', 'last_login_at'],
        'courses': ['title', 'category', 'status', 'instructor_id', 'price', 'created_at'],
        'webinars': ['title', 'category', 'status', 'instructor_id', 'scheduled_at', 'registration_deadline'],
        'purchases': ['user_id', 'course_id', 'webinar_id', 'status', 'payment_status', 'created_at'],
        'feedback': ['user_id', 'course_id', 'webinar_id', 'rating', 'status', 'created_at'],
        'doubts': ['user_id', 'course_id', 'webinar_id', 'status', 'priority', 'assigned_to', 'created_at']
    }
    
    logger.info("Generated single-field index recommendations")
    return single_field_indexes


def get_index_creation_commands() -> List[str]:
    """
    Generate Firebase CLI commands for creating recommended indexes.
    
    Returns:
        List of CLI commands for index creation
    """
    composite_indexes = firestore_optimizer.create_composite_index_recommendations()
    single_field_indexes = create_single_field_indexes()
    
    commands = []
    
    # Add composite index commands
    for collection, indexes in composite_indexes.items():
        for index in indexes:
            fields = index.split(', ')
            direction = 'asc' if 'ASC' in index else 'desc'
            
            # Extract field names (remove ASC/DESC)
            field_names = [field.split()[0] for field in fields]
            
            command = f"firebase firestore:indexes --collection={collection} --fields={','.join(field_names)}"
            commands.append(command)
    
    # Add single-field index commands
    for collection, fields in single_field_indexes.items():
        for field in fields:
            command = f"firebase firestore:indexes --collection={collection} --fields={field}"
            commands.append(command)
    
    logger.info(f"Generated {len(commands)} index creation commands")
    return commands