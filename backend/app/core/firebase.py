"""
Firebase Admin SDK initialization and configuration
Handles Firebase authentication and Firestore database connection
"""

import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore import Client as FirestoreClient
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Firebase app instance
_firebase_app: Optional[firebase_admin.App] = None
_firestore_client: Optional[FirestoreClient] = None


def initialize_firebase() -> firebase_admin.App:
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    try:
        cred = credentials.Certificate("credentials/firebase_service_account.json")
        _firebase_app = firebase_admin.initialize_app(
            credential=cred
        )

        logger.info("Firebase Admin SDK initialized successfully")
        return _firebase_app

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise



def get_firebase_app() -> firebase_admin.App:
    """Get the Firebase app instance"""
    if _firebase_app is None:
        return initialize_firebase()
    return _firebase_app


def get_firestore_client() -> FirestoreClient:
    """Get the Firestore client instance"""
    global _firestore_client
    
    if _firestore_client is None:
        try:
            app = get_firebase_app()
            _firestore_client = firestore.client(app=app)
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise
    
    return _firestore_client


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token and return decoded claims
    
    Args:
        id_token: Firebase ID token to verify
        
    Returns:
        dict: Decoded token claims
        
    Raises:
        Exception: If token verification fails
    """
    try:
        decoded_token = auth.verify_id_token(id_token, app=get_firebase_app(),check_revoked=True)
        logger.debug(f"Token verified for user: {decoded_token.get('uid')}")
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise


def get_user_by_uid(uid: str) -> auth.UserRecord:
    """
    Get user record by UID
    
    Args:
        uid: User ID
        
    Returns:
        UserRecord: Firebase user record
        
    Raises:
        Exception: If user not found or other error occurs
    """
    try:
        user = auth.get_user(uid, app=get_firebase_app())
        return user
    except Exception as e:
        logger.error(f"Failed to get user {uid}: {e}")
        raise


def create_custom_token(uid: str, claims: Optional[dict] = None) -> str:
    """
    Create a custom Firebase token
    
    Args:
        uid: User ID
        claims: Additional claims to include
        
    Returns:
        str: Custom token
    """
    try:
        token = auth.create_custom_token(uid, claims, app=get_firebase_app())
        return token.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to create custom token for {uid}: {e}")
        raise


def set_custom_user_claims(uid: str, claims: dict) -> None:
    """
    Set custom claims for a user
    
    Args:
        uid: User ID
        claims: Custom claims to set
    """
    try:
        auth.set_custom_user_claims(uid, claims, app=get_firebase_app())
        logger.info(f"Custom claims set for user {uid}")
    except Exception as e:
        logger.error(f"Failed to set custom claims for {uid}: {e}")
        raise


def revoke_refresh_tokens(uid: str) -> None:
    """
    Revoke all refresh tokens for a user
    
    Args:
        uid: User ID
    """
    try:
        auth.revoke_refresh_tokens(uid, app=get_firebase_app())
        logger.info(f"Refresh tokens revoked for user {uid}")
    except Exception as e:
        logger.error(f"Failed to revoke refresh tokens for {uid}: {e}")
        raise


def delete_user(uid: str) -> None:
    """
    Delete a user from Firebase Auth
    
    Args:
        uid: User ID to delete
    """
    try:
        auth.delete_user(uid, app=get_firebase_app())
        logger.info(f"User {uid} deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete user {uid}: {e}")
        raise


class FirebaseError(Exception):
    """Base exception for Firebase-related errors"""
    pass


class TokenVerificationError(FirebaseError):
    """Raised when token verification fails"""
    pass


class UserNotFoundError(FirebaseError):
    """Raised when a user is not found"""
    pass


class CustomTokenCreationError(FirebaseError):
    """Raised when custom token creation fails"""
    pass


class CustomClaimsError(FirebaseError):
    """Raised when custom claims operation fails"""
    pass


class UserDeletionError(FirebaseError):
    """Raised when user deletion fails"""
    pass


# Utility functions for common Firebase operations
def is_admin_user(user_claims: dict) -> bool:
    """Check if user has admin role in custom claims"""
    return user_claims.get('role') == 'admin'


def is_verified_user(user_claims: dict) -> bool:
    """Check if user email is verified"""
    return user_claims.get('email_verified', False)


def get_user_role(user_claims: dict) -> str:
    """Get user role from custom claims"""
    return user_claims.get('role', 'user')


def has_permission(user_claims: dict, permission: str) -> bool:
    """Check if user has specific permission"""
    permissions = user_claims.get('permissions', [])
    return permission in permissions


def is_user_active(user_claims: dict) -> bool:
    """Check if user account is active"""
    return not user_claims.get('disabled', False)