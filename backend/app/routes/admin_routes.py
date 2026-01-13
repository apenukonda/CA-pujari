"""
Admin Routes
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from firebase_admin import auth

from app.dependencies.auth import require_admin
from app.core.logging import get_logger
from app.utils.firestore_admin import (
    FirestoreAdmin,
    quick_database_health_check,
    generate_admin_dashboard_data
)

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# =========================
# MODELS
# =========================

class ExportRequest(BaseModel):
    collection: str
    format: str = Field(default="json", pattern="^(json|csv|ndjson)$")
    filter_conditions: Optional[Dict[str, Any]] = None


# =========================
# ADMIN UTILITIES
# =========================

@router.post("/make-admin/{uid}")
async def make_admin(uid: str):
    """
    Set Firebase custom claim role=admin for a user
    """
    try:
        auth.set_custom_user_claims(uid, {"role": "admin"})
        return {"message": f"{uid} is now admin"}
    except Exception as e:
        logger.error(f"Failed to set admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# HEALTH & STATS
# =========================

@router.get("/database/stats")
async def get_database_statistics(current_user: dict = Depends(require_admin)):
    try:
        admin = FirestoreAdmin()
        stats = await admin.get_database_statistics()
        return stats
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/quick")
async def quick_health_check_route():
    try:
        return await quick_database_health_check()
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# EXPORT
# =========================

@router.post("/export/data")
async def export_collection_data(
    request: ExportRequest,
    current_user: dict = Depends(require_admin)
):
    try:
        admin = FirestoreAdmin()
        exported_data = await admin.export_collection_data(request.collection, request.format)

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
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# DASHBOARD
# =========================

@router.get("/dashboard")
async def get_admin_dashboard_data(current_user: dict = Depends(require_admin)):
    try:
        dashboard_data = await generate_admin_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# MAINTENANCE
# =========================

@router.post("/maintenance/enable")
async def enable_maintenance_mode(
    duration_minutes: int = Query(30),
    current_user: dict = Depends(require_admin)
):
    return {
        "message": f"Maintenance mode enabled for {duration_minutes} minutes",
        "status": "enabled",
        "estimated_end": (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat()
    }


@router.post("/maintenance/disable")
async def disable_maintenance_mode(current_user: dict = Depends(require_admin)):
    return {
        "message": "Maintenance mode disabled",
        "status": "disabled",
        "timestamp": datetime.utcnow().isoformat()
    }
