"""
Firestore Admin Tools

This module provides comprehensive tools for Firestore database administration,
including monitoring, maintenance, backup, and security management.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict, Counter
import logging
import hashlib
import csv
import io

from google.cloud import firestore
from google.cloud.firestore import SERVER_TIMESTAMP, Increment
from google.api_core import exceptions as gcp_exceptions

from app.utils.logging_utils import get_logger
from app.core.firebase import get_firestore_client


logger = get_logger(__name__)


class FirestoreAdmin:
    """
    Comprehensive Firestore administration and monitoring tools.
    """
    
    def __init__(self):
        """Initialize the Firestore admin tools."""
        self.db = get_firestore_client()
        self.collections_info = {}
        
    async def get_database_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        logger.info("Starting database statistics collection")
        
        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'collections': {},
            'overall': {
                'total_documents': 0,
                'total_collections': 0,
                'estimated_storage': 0,
                'indexes': {}
            }
        }
        
        try:
            # Get all root-level collections
            root_collections = self.db.collections()
            
            for collection in root_collections:
                collection_name = collection.id
                logger.debug(f"Analyzing collection: {collection_name}")
                
                collection_stats = await self._analyze_collection(collection_name)
                stats['collections'][collection_name] = collection_stats
                stats['overall']['total_documents'] += collection_stats['document_count']
            
            stats['overall']['total_collections'] = len(stats['collections'])
            
            # Add index information
            try:
                # Note: This would require additional setup for index management
                stats['overall']['indexes'] = {
                    'managed_indexes': 0,  # Would need Firestore Admin API
                    'custom_indexes': 0    # Would need Firestore Admin API
                }
            except Exception as e:
                logger.warning(f"Could not fetch index information: {str(e)}")
            
            logger.info(f"Database statistics collected: {stats['overall']['total_documents']} documents in {stats['overall']['total_collections']} collections")
            
        except Exception as e:
            logger.error(f"Error collecting database statistics: {str(e)}")
            raise
        
        return stats
    
    async def _analyze_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Analyze a single collection for statistics.
        
        Args:
            collection_name: Name of the collection to analyze
            
        Returns:
            Dictionary with collection statistics
        """
        collection = self.db.collection(collection_name)
        
        stats = {
            'document_count': 0,
            'field_analysis': {},
            'size_estimates': {},
            'indexes': [],
            'last_updated': datetime.utcnow().isoformat()
        }
        
        try:
            # Count documents and analyze fields
            field_counter = Counter()
            size_counter = 0
            
            async for doc in collection.stream():
                stats['document_count'] += 1
                
                # Analyze document fields
                for field, value in doc.to_dict().items():
                    field_counter[field] += 1
                    
                    # Estimate document size
                    try:
                        doc_size = len(json.dumps(doc.to_dict()))
                        size_counter += doc_size
                    except:
                        pass
            
            # Calculate field statistics
            for field, count in field_counter.items():
                coverage = (count / stats['document_count']) * 100 if stats['document_count'] > 0 else 0
                stats['field_analysis'][field] = {
                    'count': count,
                    'coverage_percentage': round(coverage, 2)
                }
            
            # Size estimates
            if stats['document_count'] > 0:
                stats['size_estimates'] = {
                    'total_bytes': size_counter,
                    'average_bytes_per_doc': size_counter // stats['document_count'],
                    'estimated_storage_mb': round(size_counter / 1024 / 1024, 2)
                }
            
        except Exception as e:
            logger.error(f"Error analyzing collection {collection_name}: {str(e)}")
            stats['error'] = str(e)
        
        return stats
    
    async def monitor_collection_health(self, collection_name: str, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Monitor the health of a specific collection.
        
        Args:
            collection_name: Name of the collection to monitor
            time_window_hours: Time window for monitoring in hours
            
        Returns:
            Dictionary with health metrics
        """
        logger.info(f"Monitoring health of collection: {collection_name}")
        
        health_report = {
            'collection': collection_name,
            'timestamp': datetime.utcnow().isoformat(),
            'time_window_hours': time_window_hours,
            'metrics': {},
            'issues': [],
            'recommendations': []
        }
        
        try:
            collection = self.db.collection(collection_name)
            
            # Calculate time threshold
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Recent activity metrics
            recent_docs = 0
            recent_updates = 0
            field_issues = []
            
            async for doc in collection.stream():
                doc_data = doc.to_dict()
                
                # Check for update timestamps
                update_time = None
                if 'updated_at' in doc_data:
                    update_time = doc_data['updated_at']
                elif hasattr(doc, 'update_time'):
                    update_time = doc.update_time
                
                if update_time:
                    try:
                        if isinstance(update_time, datetime):
                            update_dt = update_time
                        else:
                            update_dt = update_time.replace(tzinfo=None)
                        
                        if update_dt > cutoff_time:
                            recent_updates += 1
                            recent_docs += 1
                    except:
                        field_issues.append(f"Invalid timestamp format in document {doc.id}")
                else:
                    # Check if document is old (potential zombie)
                    if hasattr(doc, 'create_time'):
                        try:
                            create_time = doc.create_time
                            if isinstance(create_time, datetime):
                                age = datetime.utcnow() - create_time.replace(tzinfo=None)
                                if age.days > 30:  # Old document with no updates
                                    field_issues.append(f"Potentially stale document: {doc.id} (age: {age.days} days)")
                        except:
                            pass
            
            # Analyze field coverage and consistency
            field_coverage = await self._analyze_field_coverage(collection_name)
            
            health_report['metrics'] = {
                'recent_activity': {
                    'recent_documents': recent_docs,
                    'recent_updates': recent_updates,
                    'activity_rate': f"{(recent_docs / time_window_hours):.2f} docs/hour"
                },
                'field_coverage': field_coverage,
                'data_quality': {
                    'issues_found': len(field_issues),
                    'issues': field_issues[:10]  # Limit to first 10 issues
                }
            }
            
            # Generate recommendations
            if recent_docs == 0:
                health_report['recommendations'].append({
                    'type': 'low_activity',
                    'message': 'No recent activity detected in the collection',
                    'priority': 'medium'
                })
            
            if len(field_issues) > 0:
                health_report['recommendations'].append({
                    'type': 'data_quality',
                    'message': f'Found {len(field_issues)} data quality issues',
                    'priority': 'high'
                })
            
            # Check for missing required fields
            required_fields = self._get_required_fields_for_collection(collection_name)
            missing_fields = []
            for field in required_fields:
                if field not in field_coverage or field_coverage[field]['coverage'] < 95:
                    missing_fields.append(field)
            
            if missing_fields:
                health_report['recommendations'].append({
                    'type': 'missing_fields',
                    'message': f'Required fields with low coverage: {missing_fields}',
                    'priority': 'high'
                })
            
        except Exception as e:
            logger.error(f"Error monitoring collection health: {str(e)}")
            health_report['error'] = str(e)
        
        return health_report
    
    async def _analyze_field_coverage(self, collection_name: str) -> Dict[str, Any]:
        """
        Analyze field coverage in a collection.
        
        Args:
            collection_name: Name of the collection to analyze
            
        Returns:
            Dictionary with field coverage statistics
        """
        collection = self.db.collection(collection_name)
        field_stats = defaultdict(int)
        total_docs = 0
        
        async for doc in collection.stream():
            total_docs += 1
            doc_data = doc.to_dict()
            
            # Count each field present in the document
            for field in doc_data.keys():
                field_stats[field] += 1
        
        # Calculate coverage percentages
        coverage = {}
        for field, count in field_stats.items():
            coverage[field] = {
                'count': count,
                'coverage': round((count / total_docs) * 100, 2) if total_docs > 0 else 0
            }
        
        return coverage
    
    def _get_required_fields_for_collection(self, collection_name: str) -> List[str]:
        """
        Get the list of required fields for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of required field names
        """
        required_fields_map = {
            'users': ['email', 'role', 'created_at'],
            'courses': ['title', 'description', 'price', 'status', 'created_at'],
            'webinars': ['title', 'description', 'scheduled_at', 'price', 'status', 'created_at'],
            'purchases': ['user_id', 'course_id', 'amount', 'status', 'created_at'],
            'feedback': ['user_id', 'course_id', 'rating', 'created_at'],
            'doubts': ['user_id', 'question', 'status', 'created_at']
        }
        
        return required_fields_map.get(collection_name, [])
    
    async def find_orphaned_documents(self, collection_name: str, reference_field: str, reference_collection: str) -> List[Dict[str, Any]]:
        """
        Find documents that reference non-existent documents in another collection.
        
        Args:
            collection_name: Collection to check for orphaned documents
            reference_field: Field in the collection that contains the reference ID
            reference_collection: Collection that should contain the referenced documents
            
        Returns:
            List of orphaned documents with their details
        """
        logger.info(f"Finding orphaned documents in {collection_name} referencing {reference_collection}")
        
        orphaned_docs = []
        
        try:
            # Get all valid IDs from the reference collection
            valid_ids = set()
            ref_collection = self.db.collection(reference_collection)
            
            async for doc in ref_collection.stream():
                valid_ids.add(doc.id)
            
            logger.info(f"Found {len(valid_ids)} valid references in {reference_collection}")
            
            # Check each document in the source collection
            source_collection = self.db.collection(collection_name)
            
            async for doc in source_collection.stream():
                doc_data = doc.to_dict()
                
                if reference_field in doc_data:
                    ref_id = doc_data[reference_field]
                    
                    # Check if the referenced document exists
                    if ref_id not in valid_ids:
                        orphaned_docs.append({
                            'document_id': doc.id,
                            'document_data': doc_data,
                            'missing_reference': ref_id,
                            'reference_field': reference_field
                        })
            
            logger.info(f"Found {len(orphaned_docs)} orphaned documents")
            
        except Exception as e:
            logger.error(f"Error finding orphaned documents: {str(e)}")
            raise
        
        return orphaned_docs
    
    async def cleanup_orphaned_documents(self, collection_name: str, reference_field: str, reference_collection: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up orphaned documents (with option for dry run).
        
        Args:
            collection_name: Collection containing orphaned documents
            reference_field: Field containing the reference ID
            reference_collection: Collection that should contain referenced documents
            dry_run: If True, only report orphaned documents without deleting
            
        Returns:
            Dictionary with cleanup results
        """
        logger.info(f"Starting cleanup of orphaned documents in {collection_name} (dry_run={dry_run})")
        
        orphaned_docs = await self.find_orphaned_documents(collection_name, reference_field, reference_collection)
        
        cleanup_result = {
            'collection': collection_name,
            'reference_field': reference_field,
            'reference_collection': reference_collection,
            'dry_run': dry_run,
            'orphaned_count': len(orphaned_docs),
            'processed': [],
            'errors': []
        }
        
        if dry_run:
            logger.info(f"Dry run: Found {len(orphaned_docs)} orphaned documents to potentially delete")
            cleanup_result['orphaned_documents'] = orphaned_docs
        else:
            # Actually delete orphaned documents
            collection = self.db.collection(collection_name)
            
            for orphan in orphaned_docs:
                try:
                    doc_ref = collection.document(orphan['document_id'])
                    doc_ref.delete()
                    
                    cleanup_result['processed'].append({
                        'document_id': orphan['document_id'],
                        'action': 'deleted',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"Deleted orphaned document: {orphan['document_id']}")
                    
                except Exception as e:
                    error_msg = f"Failed to delete document {orphan['document_id']}: {str(e)}"
                    cleanup_result['errors'].append(error_msg)
                    logger.error(error_msg)
        
        return cleanup_result
    
    async def export_collection_data(self, collection_name: str, output_format: str = 'json') -> Union[str, bytes]:
        """
        Export collection data to various formats.
        
        Args:
            collection_name: Name of the collection to export
            output_format: Output format ('json', 'csv', 'ndjson')
            
        Returns:
            Exported data as string or bytes
        """
        logger.info(f"Exporting collection {collection_name} in {output_format} format")
        
        try:
            collection = self.db.collection(collection_name)
            documents = []
            
            # Collect all documents
            async for doc in collection.stream():
                doc_data = doc.to_dict()
                doc_data['_id'] = doc.id  # Include document ID
                documents.append(doc_data)
            
            if output_format == 'json':
                return json.dumps(documents, indent=2, default=str)
            
            elif output_format == 'ndjson':
                return '\n'.join(json.dumps(doc, default=str) for doc in documents)
            
            elif output_format == 'csv':
                if not documents:
                    return ""
                
                # Convert to CSV
                output = io.StringIO()
                fieldnames = set()
                for doc in documents:
                    fieldnames.update(doc.keys())
                
                writer = csv.DictWriter(output, fieldnames=sorted(fieldnames))
                writer.writeheader()
                
                for doc in documents:
                    # Convert non-serializable values to strings
                    row = {}
                    for key, value in doc.items():
                        if isinstance(value, (datetime, SERVER_TIMESTAMP)):
                            row[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                        else:
                            row[key] = value
                    writer.writerow(row)
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
        except Exception as e:
            logger.error(f"Error exporting collection data: {str(e)}")
            raise
    
    async def get_collection_schema(self, collection_name: str, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Analyze and infer the schema of a collection.
        
        Args:
            collection_name: Name of the collection to analyze
            sample_size: Number of documents to sample for schema analysis
            
        Returns:
            Dictionary with inferred schema information
        """
        logger.info(f"Analyzing schema for collection {collection_name}")
        
        schema_info = {
            'collection': collection_name,
            'timestamp': datetime.utcnow().isoformat(),
            'sample_size': 0,
            'fields': {},
            'types': {},
            'statistics': {}
        }
        
        try:
            collection = self.db.collection(collection_name)
            field_types = defaultdict(set)
            field_counts = defaultdict(int)
            sample_docs = []
            
            # Sample documents
            async for doc in collection.stream():
                if len(sample_docs) >= sample_size:
                    break
                
                sample_docs.append(doc)
                doc_data = doc.to_dict()
                
                # Analyze each field
                for field, value in doc_data.items():
                    field_counts[field] += 1
                    
                    # Track types for this field
                    if isinstance(value, str):
                        field_types[field].add('string')
                    elif isinstance(value, int):
                        field_types[field].add('integer')
                    elif isinstance(value, float):
                        field_types[field].add('float')
                    elif isinstance(value, bool):
                        field_types[field].add('boolean')
                    elif isinstance(value, list):
                        field_types[field].add('array')
                    elif isinstance(value, dict):
                        field_types[field].add('object')
                    elif value is None:
                        field_types[field].add('null')
                    elif hasattr(value, 'isoformat'):  # datetime-like
                        field_types[field].add('datetime')
                    else:
                        field_types[field].add('unknown')
            
            schema_info['sample_size'] = len(sample_docs)
            
            # Build field information
            for field in field_counts:
                coverage = (field_counts[field] / schema_info['sample_size']) * 100
                schema_info['fields'][field] = {
                    'count': field_counts[field],
                    'coverage': round(coverage, 2),
                    'types': list(field_types[field])
                }
            
            # Field type statistics
            all_types = set()
            for types in field_types.values():
                all_types.update(types)
            
            schema_info['types'] = {
                'all_detected': list(all_types),
                'field_type_distribution': {
                    field: list(types) for field, types in field_types.items()
                }
            }
            
            # Additional statistics
            schema_info['statistics'] = {
                'total_fields': len(field_counts),
                'fields_per_doc_avg': sum(field_counts.values()) / len(sample_docs) if sample_docs else 0,
                'most_common_fields': sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing collection schema: {str(e)}")
            schema_info['error'] = str(e)
        
        return schema_info
    
    async def get_slow_queries_report(self) -> Dict[str, Any]:
        """
        Generate a report of potentially slow queries.
        
        Returns:
            Dictionary with slow query analysis
        """
        logger.info("Generating slow queries report")
        
        # Note: This is a simplified version. Real slow query detection
        # would require Firestore query logging and analysis
        
        slow_queries_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'potential_issues': [],
            'recommendations': []
        }
        
        try:
            # Check for collections without proper indexes
            collections_to_check = ['users', 'courses', 'webinars', 'purchases', 'feedback', 'doubts']
            
            for collection_name in collections_to_check:
                collection = self.db.collection(collection_name)
                
                # Check for potential issues
                issues = []
                
                # Check for large collections that might need indexing
                doc_count = 0
                async for _ in collection.stream():
                    doc_count += 1
                    if doc_count > 1000:  # Threshold for potential indexing needs
                        break
                
                if doc_count > 1000:
                    issues.append(f"Large collection ({doc_count}+ docs) - ensure proper indexes")
                
                # Check for fields that might benefit from indexing
                schema = await self.get_collection_schema(collection_name, sample_size=100)
                
                # Common fields that should be indexed
                index_candidates = ['email', 'status', 'created_at', 'updated_at', 'user_id', 'course_id']
                
                for field in schema.get('fields', {}):
                    if field in index_candidates:
                        coverage = schema['fields'][field].get('coverage', 0)
                        if coverage > 50:  # Field is used in majority of documents
                            issues.append(f"Field '{field}' should be indexed (coverage: {coverage}%)")
                
                if issues:
                    slow_queries_report['potential_issues'].append({
                        'collection': collection_name,
                        'issues': issues
                    })
            
            # Generate recommendations
            slow_queries_report['recommendations'] = [
                "Implement composite indexes for multi-field queries",
                "Use query cursors for large result sets",
                "Consider denormalization for frequently queried data",
                "Implement caching for read-heavy operations",
                "Monitor query performance with Cloud Monitoring"
            ]
            
        except Exception as e:
            logger.error(f"Error generating slow queries report: {str(e)}")
            slow_queries_report['error'] = str(e)
        
        return slow_queries_report
    
    async def security_audit(self) -> Dict[str, Any]:
        """
        Perform a security audit of the Firestore database.
        
        Returns:
            Dictionary with security audit results
        """
        logger.info("Performing Firestore security audit")
        
        audit_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'security_checks': {},
            'vulnerabilities': [],
            'recommendations': []
        }
        
        try:
            # Check for collections with potentially sensitive data
            sensitive_collections = ['users', 'purchases', 'feedback']
            
            for collection_name in sensitive_collections:
                collection = self.db.collection(collection_name)
                
                security_check = {
                    'collection': collection_name,
                    'document_count': 0,
                    'sensitive_fields': [],
                    'data_classification': 'unknown'
                }
                
                # Sample documents to check for sensitive fields
                sample_count = 0
                async for doc in collection.stream():
                    if sample_count >= 10:  # Sample first 10 documents
                        break
                    
                    sample_count += 1
                    security_check['document_count'] += 1
                    
                    doc_data = doc.to_dict()
                    
                    # Check for sensitive fields
                    sensitive_patterns = {
                        'password': ['password', 'pwd', 'pass'],
                        'personal_info': ['ssn', 'social_security', 'national_id'],
                        'financial': ['credit_card', 'card_number', 'cvv', 'bank_account'],
                        'authentication': ['token', 'api_key', 'secret', 'auth']
                    }
                    
                    for field_name in doc_data.keys():
                        field_lower = field_name.lower()
                        for category, patterns in sensitive_patterns.items():
                            if any(pattern in field_lower for pattern in patterns):
                                security_check['sensitive_fields'].append({
                                    'field': field_name,
                                    'category': category,
                                    'document_id': doc.id
                                })
                
                audit_results['security_checks'][collection_name] = security_check
            
            # Generate security recommendations
            audit_results['recommendations'] = [
                "Enable Firestore Security Rules to restrict access",
                "Use Firebase Authentication for user identity verification",
                "Implement field-level encryption for sensitive data",
                "Regularly audit access patterns and permissions",
                "Use least-privilege principle for service account access",
                "Implement data retention policies",
                "Enable audit logging for sensitive operations"
            ]
            
            # Check for potential vulnerabilities
            for collection_name, check in audit_results['security_checks'].items():
                if check['sensitive_fields']:
                    audit_results['vulnerabilities'].append({
                        'collection': collection_name,
                        'issue': 'Sensitive fields detected without encryption',
                        'fields': check['sensitive_fields'],
                        'severity': 'high'
                    })
        
        except Exception as e:
            logger.error(f"Error performing security audit: {str(e)}")
            audit_results['error'] = str(e)
        
        return audit_results
    
    async def maintenance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive maintenance report.
        
        Returns:
            Dictionary with maintenance recommendations and status
        """
        logger.info("Generating maintenance report")
        
        maintenance_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_health': 'unknown',
            'database_stats': {},
            'collection_health': {},
            'recommendations': [],
            'priority_actions': []
        }
        
        try:
            # Get overall database statistics
            db_stats = await self.get_database_statistics()
            maintenance_report['database_stats'] = db_stats
            
            # Monitor each collection
            collections = ['users', 'courses', 'webinars', 'purchases', 'feedback', 'doubts']
            
            for collection_name in collections:
                try:
                    health_report = await self.monitor_collection_health(collection_name, time_window_hours=24)
                    maintenance_report['collection_health'][collection_name] = health_report
                except Exception as e:
                    logger.warning(f"Could not monitor collection {collection_name}: {str(e)}")
            
            # Determine overall health
            issues_count = 0
            for collection_name, health in maintenance_report['collection_health'].items():
                if 'issues' in health and health['issues']:
                    issues_count += len(health['issues'])
            
            if issues_count == 0:
                maintenance_report['overall_health'] = 'healthy'
            elif issues_count <= 3:
                maintenance_report['overall_health'] = 'good'
            elif issues_count <= 10:
                maintenance_report['overall_health'] = 'needs_attention'
            else:
                maintenance_report['overall_health'] = 'critical'
            
            # Generate recommendations based on analysis
            if db_stats['overall']['total_documents'] > 100000:
                maintenance_report['priority_actions'].append({
                    'action': 'Consider database sharding',
                    'priority': 'high',
                    'reason': 'Large number of documents detected'
                })
            
            # Check for collections with high activity
            for collection_name, health in maintenance_report['collection_health'].items():
                if 'metrics' in health and 'recent_activity' in health['metrics']:
                    activity_rate = health['metrics']['recent_activity'].get('activity_rate', '0')
                    if float(activity_rate.split()[0]) > 100:  # More than 100 docs/hour
                        maintenance_report['priority_actions'].append({
                            'action': f'Optimize {collection_name} queries',
                            'priority': 'high',
                            'reason': 'High write activity detected'
                        })
            
            # General recommendations
            maintenance_report['recommendations'] = [
                "Implement automated backup procedures",
                "Set up monitoring and alerting for performance metrics",
                "Regular database optimization and cleanup",
                "Review and optimize Firestore Security Rules",
                "Implement data archiving for old records",
                "Monitor storage costs and usage patterns"
            ]
            
        except Exception as e:
            logger.error(f"Error generating maintenance report: {str(e)}")
            maintenance_report['error'] = str(e)
        
        return maintenance_report


# Global admin instance
firestore_admin = FirestoreAdmin()


# Utility functions for common admin tasks

async def quick_database_health_check() -> Dict[str, Any]:
    """
    Perform a quick health check of the database.
    
    Returns:
        Dictionary with health check results
    """
    logger.info("Performing quick database health check")
    
    health_check = {
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'unknown',
        'collections_checked': 0,
        'total_documents': 0,
        'errors': []
    }
    
    try:
        admin = FirestoreAdmin()
        
        # Check basic connectivity by listing collections
        collections = admin.db.collections()
        collection_count = 0
        
        for collection in collections:
            collection_count += 1
            collection_name = collection.id
            
            # Count documents in each collection (with limit to avoid timeout)
            doc_count = 0
            async for _ in collection.stream():
                doc_count += 1
                if doc_count >= 1000:  # Limit for quick check
                    break
            
            health_check['total_documents'] += doc_count
            
            # Check for obvious issues
            if doc_count == 0:
                health_check['errors'].append(f"Empty collection: {collection_name}")
        
        health_check['collections_checked'] = collection_count
        
        # Determine status
        if not health_check['errors']:
            health_check['status'] = 'healthy'
        elif len(health_check['errors']) <= 2:
            health_check['status'] = 'warning'
        else:
            health_check['status'] = 'error'
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        health_check['status'] = 'error'
        health_check['errors'].append(f"Health check failed: {str(e)}")
    
    return health_check


async def generate_admin_dashboard_data() -> Dict[str, Any]:
    """
    Generate data suitable for an admin dashboard.
    
    Returns:
        Dictionary with dashboard metrics
    """
    logger.info("Generating admin dashboard data")
    
    try:
        admin = FirestoreAdmin()
        
        # Get database statistics
        db_stats = await admin.get_database_statistics()
        
        # Get maintenance report
        maintenance = await admin.maintenance_report()
        
        # Get security audit
        security = await admin.security_audit()
        
        dashboard_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'overview': {
                'total_documents': db_stats['overall']['total_documents'],
                'total_collections': db_stats['overall']['total_collections'],
                'overall_health': maintenance['overall_health'],
                'security_status': 'secure' if not security['vulnerabilities'] else 'vulnerable'
            },
            'collections': db_stats['collections'],
            'health': {
                'collection_health': maintenance['collection_health'],
                'maintenance_needed': len(maintenance['priority_actions']) > 0
            },
            'security': {
                'vulnerabilities': security['vulnerabilities'],
                'security_score': max(0, 100 - len(security['vulnerabilities']) * 20)
            },
            'alerts': []
        }
        
        # Generate alerts
        if maintenance['overall_health'] in ['needs_attention', 'critical']:
            dashboard_data['alerts'].append({
                'type': 'maintenance',
                'message': f"Database health is {maintenance['overall_health']}",
                'priority': 'high' if maintenance['overall_health'] == 'critical' else 'medium'
            })
        
        if security['vulnerabilities']:
            dashboard_data['alerts'].append({
                'type': 'security',
                'message': f"Found {len(security['vulnerabilities'])} security vulnerabilities",
                'priority': 'high'
            })
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e),
            'status': 'error'
        }


# Export admin functions for easy access

__all__ = [
    'FirestoreAdmin',
    'firestore_admin',
    'quick_database_health_check',
    'generate_admin_dashboard_data'
]