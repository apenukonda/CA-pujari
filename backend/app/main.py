"""
FastAPI E-Learning Platform Backend
Main application entry point with configuration and route registration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from datetime import datetime

from firebase_admin import auth

# Import configuration and logging setup
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.firebase import get_firestore_client

# Import route modules
from app.routes import auth_routes
from app.routes import user_routes
from app.routes import course_routes
from app.routes import webinar_routes
from app.routes import purchase_routes
from app.routes import feedback_routes
from app.routes import doubt_routes
from app.routes import admin_routes

# Import webhook handlers
from app.webhooks import payment_webhook

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="E-Learning Platform API",
    description="Backend API for comprehensive e-learning platform with courses, webinars, and payments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# ========================
# HEALTH + ROOT
# ========================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "e-learning-backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    return {
        "message": "E-Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ========================
# REGISTER ROUTES
# ========================

app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(course_routes.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(webinar_routes.router, prefix="/api/v1/webinars", tags=["Webinars"])
app.include_router(purchase_routes.router, prefix="/api/v1/purchases", tags=["Purchases"])
app.include_router(feedback_routes.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(doubt_routes.router, prefix="/api/v1/doubts", tags=["Doubts"])
app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(payment_webhook.router, prefix="/webhooks", tags=["Webhooks"])

# ========================
# TEST / DEV ENDPOINTS
# ========================

@app.post("/test-add-admin-user")
async def test_add_admin_user():
    db = get_firestore_client()

    email = "amaan@test.com"
    password = "Test@12345"
    name = "Amaan"

    # 1. Create user in Firebase Auth
    user_record = auth.create_user(
        email=email,
        password=password,
        display_name=name
    )

    # 2. Set custom claim as admin 🔥
    auth.set_custom_user_claims(user_record.uid, {"role": "admin"})

    # 3. Save profile in Firestore
    user_data = {
        "name": name,
        "email": email,
        "role": "admin",
        "created_at": datetime.utcnow(),
        "firebase_uid": user_record.uid
    }

    db.collection("users").document(user_record.uid).set(user_data)

    return {
        "message": "Admin user created successfully",
        "firebase_uid": user_record.uid
    }


@app.post("/test-add-normal-user")
async def test_add_normal_user():
    db = get_firestore_client()

    email = "user1@test.com"
    password = "User@12345"
    name = "Normal User"

    user_record = auth.create_user(
        email=email,
        password=password,
        display_name=name
    )

    # normal user → no custom claims
    user_data = {
        "name": name,
        "email": email,
        "role": "user",
        "created_at": datetime.utcnow(),
        "firebase_uid": user_record.uid
    }

    db.collection("users").document(user_record.uid).set(user_data)

    return {
        "message": "Normal user created successfully",
        "firebase_uid": user_record.uid
    }


@app.get("/test-get-users")
async def test_get_users():
    db = get_firestore_client()
    users_ref = db.collection("users").stream()

    users = []
    for doc in users_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        users.append(data)

    return {
        "count": len(users),
        "users": users
    }


# ========================
# GLOBAL ERROR HANDLER
# ========================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
