"""
Registration service for Worker B.

This service coordinates user registration functionality with proper
error handling and validation.
"""

from typing import Tuple, Optional, Dict
from .user_storage import FileBasedUserStorage


class RegistrationService:
    """
    Registration service that coordinates user registration.

    This implementation provides:
    - User registration with validation
    - Error handling for various scenarios
    - Integration with file-based user storage
    """

    def __init__(self, storage_file: str = "users_b.json"):
        """
        Initialize registration service.

        Args:
            storage_file: Path to user storage file
        """
        self.user_storage = FileBasedUserStorage(storage_file)

    def register(self, username: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Register a new user.

        Args:
            username: Username (must be non-empty)
            password: Plain text password (must be non-empty)

        Returns:
            Tuple of (success, user_data, error_message)
            - success: True if registration successful, False otherwise
            - user_data: User dictionary if successful, None otherwise
            - error_message: Error message if failed, None if successful
        """
        # Validate input
        if not username or not username.strip():
            return False, None, "Username cannot be empty"

        if not password or not password.strip():
            return False, None, "Password cannot be empty"

        # Normalize username (strip whitespace)
        username = username.strip()

        # Check if username already exists
        if self.user_storage.username_exists(username):
            return False, None, "Username already exists"

        # Register user
        user = self.user_storage.register_user(username, password)

        if user is None:
            return False, None, "Registration failed"

        # Return user data without password hash for security
        user_response = {
            'id': user['id'],
            'username': user['username'],
            'created_at': user['created_at']
        }

        return True, user_response, None

    def validate_username(self, username: str) -> Tuple[bool, Optional[str]]:
        """
        Validate username format.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or not username.strip():
            return False, "Username cannot be empty"

        username = username.strip()

        # Basic validation: username should be reasonable length
        if len(username) < 3:
            return False, "Username must be at least 3 characters"

        if len(username) > 50:
            return False, "Username must be at most 50 characters"

        # Check if username already exists
        if self.user_storage.username_exists(username):
            return False, "Username already exists"

        return True, None

    def validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password format.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password or not password.strip():
            return False, "Password cannot be empty"

        # Basic validation: password should be reasonable length
        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        if len(password) > 100:
            return False, "Password must be at most 100 characters"

        return True, None
