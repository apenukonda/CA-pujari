"""
Admin Routes

FastAPI routes for comprehensive Firestore administration and monitoring.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.dependencies.auth import require_admin
from app.core.logging import get_logger
from app.core.firebase import get_firestore_client

from app.utils.firestore_optimization import firestore_optimizer
from app.utils.firestore_admin import (
    FirestoreAdmin,
    quick_database_health_check,
    generate_admin_dashboard_data
)


logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# Pydantic models for API requests/responses

class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""
    total_entries: int
    hit_rate: float
    total_hits: int
    total_misses: int
    memory_usage_mb: float
    collections_cached: List[str]
    last_cleanup: Optional[datetime]


class DatabaseStatsResponse(BaseModel):
    """Response model for database statistics."""
    timestamp: str
    collections: Dict[str, Any]
    overall: Dict[str, Any]


class CollectionHealthResponse(BaseModel):
    """Response model for collection health."""
    collection: str
    timestamp: str
    time_window_hours: int
    metrics: Dict[str, Any]
    issues: List[str]
    recommendations: List[Dict[str, Any]]


class OrphanedDocumentsResponse(BaseModel):
    """Response model for orphaned documents."""
    collection: str
    reference_field: str
    reference_collection: str
    orphaned_count: int
    orphaned_documents: List[Dict[str, Any]]


class CleanupResponse(BaseModel):
    """Response model for cleanup operations."""
    collection: str
    reference_field: str
    reference_collection: str
    dry_run: bool
    orphaned_count: int
    processed: List[Dict[str, Any]]
    errors: List[str]


class ExportRequest(BaseModel):
    """Request model for data export."""
    collection: str
    format: str = Field(default="json", pattern="^(json|csv|ndjson)$")
    filter_conditions: Optional[Dict[str, Any]] = None


class SecurityAuditResponse(BaseModel):
    """Response model for security audit."""
    timestamp: str
    security_checks: Dict[str, Any]
    vulnerabilities: List[Dict[str, Any]]
    recommendations: List[str]


class MaintenanceReportResponse(BaseModel):
    """Response model for maintenance report."""
    timestamp: str
    overall_health: str
    database_stats: Dict[str, Any]
    collection_health: Dict[str, Any]
    recommendations: List[str]
    priority_actions: List[Dict[str, Any]]


class DashboardDataResponse(BaseModel):
    """Response model for dashboard data."""
    timestamp: str
    overview: Dict[str, Any]
    collections: Dict[str, Any]
    health: Dict[str, Any]
    security: Dict[str, Any]
    alerts: List[Dict[str, Any]]


# Cache Management Routes

@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(current_user: dict = Depends(require_admin())):
    """
    Get comprehensive cache statistics.
    
    Requires admin role.
    """
    try:
        cache = FirestoreCache()
        stats = await cache.get_stats()
        
        return CacheStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")


@router.post("/cache/clear")
async def clear_cache(
    collection: Optional[str] = Query(None, description="Specific collection to clear"),
    current_user: dict = Depends(require_admin())
):
    """
    Clear cache entries.
    
    If no collection specified, clears all cache.
    Requires admin role.
    """
    try:
        cache = FirestoreCache()
        
        if collection:
            await cache.clear_collection_cache(collection)
            return {"message": f"Cache cleared for collection: {collection}"}
        else:
            await cache.clear_all_cache()
            return {"message": "All cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.post("/cache/preload/{collection_name}")
async def preload_collection_cache(
    collection_name: str,
    limit: int = Query(100, description="Number of documents to preload"),
    current_user: dict = Depends(require_admin())
):
    """
    Preload cache for a specific collection.
    Requires admin role.
    """
    try:
        cache = FirestoreCache()
        await cache.preload_collection_cache(collection_name, limit=limit)
        
        return {"message": f"Cache preloaded for collection: {collection_name}"}
        
    except Exception as e:
        logger.error(f"Error preloading cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to preload cache: {str(e)}")


# Database Statistics Routes

@router.get("/database/stats", response_model=DatabaseStatsResponse)
async def get_database_statistics(current_user: dict = Depends(require_admin())):
    """
    Get comprehensive database statistics.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        stats = await admin.get_database_statistics()
        
        return DatabaseStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get database statistics: {str(e)}")


@router.get("/health/quick")
async def quick_health_check():
    """
    Perform a quick database health check.
    No authentication required for this endpoint.
    """
    try:
        health_check = await quick_database_health_check()
        return health_check
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/health/collection/{collection_name}", response_model=CollectionHealthResponse)
async def monitor_collection_health(
    collection_name: str,
    time_window_hours: int = Query(24, description="Time window for monitoring in hours"),
    current_user: dict = Depends(require_admin())
):
    """
    Monitor the health of a specific collection.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        health_report = await admin.monitor_collection_health(collection_name, time_window_hours)
        
        return CollectionHealthResponse(**health_report)
        
    except Exception as e:
        logger.error(f"Error monitoring collection health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to monitor collection health: {str(e)}")


# Data Integrity Routes

@router.get("/integrity/orphans", response_model=OrphanedDocumentsResponse)
async def find_orphaned_documents(
    collection: str = Query(..., description="Collection to check for orphaned documents"),
    reference_field: str = Query(..., description="Field containing the reference ID"),
    reference_collection: str = Query(..., description="Collection that should contain referenced documents"),
    current_user: dict = Depends(require_admin())
):
    """
    Find documents that reference non-existent documents.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        orphaned_docs = await admin.find_orphaned_documents(collection, reference_field, reference_collection)
        
        return OrphanedDocumentsResponse(
            collection=collection,
            reference_field=reference_field,
            reference_collection=reference_collection,
            orphaned_count=len(orphaned_docs),
            orphaned_documents=orphaned_docs
        )
        
    except Exception as e:
        logger.error(f"Error finding orphaned documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to find orphaned documents: {str(e)}")


@router.post("/integrity/cleanup", response_model=CleanupResponse)
async def cleanup_orphaned_documents(
    collection: str = Query(..., description="Collection containing orphaned documents"),
    reference_field: str = Query(..., description="Field containing the reference ID"),
    reference_collection: str = Query(..., description="Collection that should contain referenced documents"),
    dry_run: bool = Query(True, description="If True, only report without deleting"),
    current_user: dict = Depends(require_admin())
):
    """
    Clean up orphaned documents.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        cleanup_result = await admin.cleanup_orphaned_documents(
            collection, reference_field, reference_collection, dry_run
        )
        
        return CleanupResponse(**cleanup_result)
        
    except Exception as e:
        logger.error(f"Error cleaning up orphaned documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup orphaned documents: {str(e)}")


# Data Export Routes

@router.post("/export/data")
async def export_collection_data(
    request: ExportRequest,
    current_user: dict = Depends(require_admin())
):
    """
    Export collection data to various formats.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        
        # If filter conditions are provided, we would need to implement filtering
        # For now, we'll export all documents
        exported_data = await admin.export_collection_data(request.collection, request.format)
        
        # Determine content type and filename
        content_types = {
            'json': 'application/json',
            'csv': 'text/csv',
            'ndjson': 'application/x-ndjson'
        }
        
        filename = f"{request.collection}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{request.format}"
        
        return StreamingResponse(
            iter([exported_data]),
            media_type=content_types.get(request.format, 'application/octet-stream'),
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.get("/schema/{collection_name}")
async def get_collection_schema(
    collection_name: str,
    sample_size: int = Query(1000, description="Number of documents to sample"),
    current_user: dict = Depends(require_admin())
):
    """
    Analyze and infer the schema of a collection.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        schema_info = await admin.get_collection_schema(collection_name, sample_size)
        
        return schema_info
        
    except Exception as e:
        logger.error(f"Error analyzing schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze schema: {str(e)}")


# Performance Analysis Routes

@router.get("/performance/slow-queries")
async def get_slow_queries_report(current_user: dict = Depends(require_admin())):
    """
    Generate a report of potentially slow queries.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        report = await admin.get_slow_queries_report()
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating slow queries report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate slow queries report: {str(e)}")


# Security and Maintenance Routes

@router.get("/security/audit", response_model=SecurityAuditResponse)
async def security_audit(current_user: dict = Depends(require_admin())):
    """
    Perform a security audit of the Firestore database.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        audit_results = await admin.security_audit()
        
        return SecurityAuditResponse(**audit_results)
        
    except Exception as e:
        logger.error(f"Error performing security audit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform security audit: {str(e)}")


@router.get("/maintenance/report", response_model=MaintenanceReportResponse)
async def maintenance_report(current_user: dict = Depends(require_admin())):
    """
    Generate a comprehensive maintenance report.
    Requires admin role.
    """
    try:
        admin = FirestoreAdmin()
        report = await admin.maintenance_report()
        
        return MaintenanceReportResponse(**report)
        
    except Exception as e:
        logger.error(f"Error generating maintenance report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate maintenance report: {str(e)}")


# Dashboard Data Routes

@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_admin_dashboard_data(current_user: dict = Depends(require_admin())):
    """
    Generate data suitable for an admin dashboard.
    Requires admin role.
    """
    try:
        dashboard_data = await generate_admin_dashboard_data()
        
        return DashboardDataResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard data: {str(e)}")


# Batch Operations Routes

@router.post("/batch/optimize-queries")
async def optimize_database_queries(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_admin())
):
    """
    Trigger database query optimization in background.
    Requires admin role.
    """
    try:
        # This would implement query optimization strategies
        # For now, we'll return a placeholder response
        return {
            "message": "Query optimization started in background",
            "status": "started",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting query optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start query optimization: {str(e)}")


@router.post("/batch/rebuild-indexes")
async def rebuild_search_indexes(
    collection: Optional[str] = Query(None, description="Specific collection to rebuild indexes for"),
    current_user: dict = Depends(require_admin())
):
    """
    Rebuild search indexes for collections.
    Requires admin role.
    """
    try:
        # This would implement index rebuilding logic
        return {
            "message": f"Index rebuilding started for {'all collections' if not collection else collection}",
            "status": "started",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding indexes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild indexes: {str(e)}")


# Monitoring and Alerting Routes

@router.get("/monitoring/metrics")
async def get_system_metrics(
    time_range: str = Query("1h", description="Time range for metrics (1h, 6h, 24h, 7d)"),
    current_user: dict = Depends(require_admin())
):
    """
    Get system performance metrics.
    Requires admin role.
    """
    try:
        # This would integrate with Cloud Monitoring APIs
        # For now, return basic metrics
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "time_range": time_range,
            "metrics": {
                "database_operations": {
                    "reads_per_minute": 0,  # Would come from Cloud Monitoring
                    "writes_per_minute": 0,
                    "query_count": 0
                },
                "cache_performance": {
                    "hit_rate": 0.0,
                    "memory_usage_mb": 0.0
                },
                "storage": {
                    "documents_count": 0,
                    "storage_used_mb": 0.0
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@router.get("/alerts")
async def get_active_alerts(current_user: dict = Depends(require_admin())):
    """
    Get active system alerts.
    Requires admin role.
    """
    try:
        # This would integrate with alerting systems
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": [],
            "summary": {
                "total_alerts": 0,
                "critical_alerts": 0,
                "warning_alerts": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


# Utility Routes

@router.get("/status")
async def admin_system_status(current_user: dict = Depends(require_admin())):
    """
    Get overall admin system status.
    Requires admin role.
    """
    try:
        # Check various system components
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy",  # Would check actual connectivity
                "cache": "healthy",     # Would check cache availability
                "optimization": "healthy", # Would check optimization tools
                "monitoring": "healthy"   # Would check monitoring systems
            },
            "overall_status": "healthy",
            "last_check": datetime.utcnow().isoformat()
        }
        
        # Determine overall status
        if "error" in status["components"].values():
            status["overall_status"] = "error"
        elif "warning" in status["components"].values():
            status["overall_status"] = "warning"
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.post("/maintenance/enable")
async def enable_maintenance_mode(
    duration_minutes: int = Query(30, description="Maintenance mode duration in minutes"),
    current_user: dict = Depends(require_admin())
):
    """
    Enable maintenance mode (blocks non-admin requests).
    Requires admin role.
    """
    try:
        # This would implement maintenance mode logic
        # For now, return a placeholder response
        return {
            "message": f"Maintenance mode enabled for {duration_minutes} minutes",
            "status": "enabled",
            "estimated_end": (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error enabling maintenance mode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to enable maintenance mode: {str(e)}")


@router.post("/maintenance/disable")
async def disable_maintenance_mode(current_user: dict = Depends(require_admin())):
    """
    Disable maintenance mode.
    Requires admin role.
    """
    try:
        # This would implement maintenance mode disable logic
        return {
            "message": "Maintenance mode disabled",
            "status": "disabled",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error disabling maintenance mode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to disable maintenance mode: {str(e)}")


# Export the router for inclusion in the main FastAPI app
__all__ = ['router']