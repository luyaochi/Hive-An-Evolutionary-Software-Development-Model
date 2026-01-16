"""
Authentication service for Worker A.

This service coordinates user login with credential verification
following worker_b_src pattern.
"""

from typing import Tuple, Optional, Dict
from .user_storage import FileBasedUserStorage
from .token_manager import JWTTokenManager


class AuthService:
    """
    Authentication service that coordinates:
    - User login with credential verification
    - JWT token generation and validation
    
    This implementation follows worker_b_src pattern.
    """

    def __init__(self, storage_file: str = "users_a.json"):
        """
        Initialize authentication service.

        Args:
            storage_file: Path to user storage file
        """
        self.user_storage = FileBasedUserStorage(storage_file)
        self.token_manager = JWTTokenManager()

    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Login a user and generate a token.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, response_data, error_message)
            - success: True if login successful
            - response_data: Dictionary with 'user' and 'token' if successful, None otherwise
            - error_message: Error message if failed, None if successful
        """
        if not username or not password:
            return False, None, "Username and password are required"

        # Verify password
        if not self.user_storage.verify_password(username, password):
            return False, None, "Invalid credentials"

        # Get user information
        user = self.user_storage.get_user_by_username(username)
        if not user:
            return False, None, "User not found"

        # Generate JWT token
        token = self.token_manager.generate_token(
            user_id=user['id'],
            username=user['username']
        )

        # Return user data (without password hash) and token
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'created_at': user['created_at']
        }

        response_data = {
            'user': user_data,
            'token': token
        }

        return True, response_data, None

    def verify_token(self, token: str) -> Optional[Dict[str, str]]:
        """
        Verify a token and return user information.

        Args:
            token: JWT token to verify

        Returns:
            Dictionary with 'user_id' and 'username' if token is valid, None otherwise
        """
        return self.token_manager.verify_token(token)

    def get_user_by_token(self, token: str) -> Optional[Dict]:
        """
        Get user information from token.

        Args:
            token: JWT token

        Returns:
            User dictionary if token is valid, None otherwise
        """
        user_info = self.verify_token(token)
        if not user_info:
            return None

        user_id = user_info.get('user_id')
        if user_id:
            return self.user_storage.get_user_by_id(user_id)

        return None