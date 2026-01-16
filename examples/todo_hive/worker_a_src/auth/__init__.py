"""
Authentication domain module.

This module implements user authentication using:
- File-based user storage (方案 A2)
- JWT stateless tokens (方案 B1)
"""

from .user_storage import FileUserStorage
from .token_manager import JWTTokenManager
from .auth_service import AuthService

__all__ = ['FileUserStorage', 'JWTTokenManager', 'AuthService']
