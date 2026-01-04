"""
FastAPI E-Learning Platform Backend
Main application entry point with configuration and route registration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging

# Import configuration and logging setup
from app.core.config import settings
from app.core.logging import setup_logging

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

# Import rate limiter
from app.utils.rate_limiter import RateLimiterMiddleware

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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "e-learning-backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "E-Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Register API routes
# Authentication routes
app.include_router(
    auth_routes.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# User management routes
app.include_router(
    user_routes.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

# Course management routes
app.include_router(
    course_routes.router,
    prefix="/api/v1/courses",
    tags=["Courses"]
)

# Webinar management routes
app.include_router(
    webinar_routes.router,
    prefix="/api/v1/webinars",
    tags=["Webinars"]
)

# Purchase and payment routes
app.include_router(
    purchase_routes.router,
    prefix="/api/v1/purchases",
    tags=["Purchases"]
)

# Feedback routes
app.include_router(
    feedback_routes.router,
    prefix="/api/v1/feedback",
    tags=["Feedback"]
)

# Doubt/Q&A routes
app.include_router(
    doubt_routes.router,
    prefix="/api/v1/doubts",
    tags=["Doubts"]
)

# Admin routes
app.include_router(
    admin_routes.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

# Webhook routes
app.include_router(
    payment_webhook.router,
    prefix="/webhooks",
    tags=["Webhooks"]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
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