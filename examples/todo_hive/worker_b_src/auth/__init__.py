"""
Authentication module for Worker B.

This module provides user registration functionality using file-based storage
and JWT token management.
"""

from .user_storage import FileBasedUserStorage
from .registration_service import RegistrationService
from .token_manager import JWTTokenManager
from .auth_service import AuthService

__all__ = ['FileBasedUserStorage', 'RegistrationService', 'JWTTokenManager', 'AuthService']
