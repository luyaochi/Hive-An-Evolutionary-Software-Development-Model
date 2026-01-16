"""
Authentication module for Worker A.

This module provides user login functionality using file-based storage
and JWT token management (following worker_b_src pattern).
"""

from .user_storage import FileBasedUserStorage
from .token_manager import JWTTokenManager
from .auth_service import AuthService

__all__ = ['FileBasedUserStorage', 'JWTTokenManager', 'AuthService']