"""
Authentication service that coordinates user storage and token management.
"""

from typing import Optional, Tuple
from .user_storage import FileUserStorage
from .token_manager import JWTTokenManager


class AuthService:
    """
    Authentication service that coordinates:
    - User registration and verification
    - Token generation and validation
    """

    def __init__(self, storage_file: str = "users.json"):
        """
        Initialize authentication service.

        Args:
            storage_file: Path to user storage file
        """
        self.user_storage = FileUserStorage(storage_file)
        self.token_manager = JWTTokenManager()

    def register(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Register a new user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, error_message)
            success: True if registration successful
            error_message: Error message if failed, None if successful
        """
        if not username or not password:
            return False, "Username and password are required"

        if self.user_storage.register_user(username, password):
            return True, None
        else:
            return False, "Username already exists"

    def login(self, username: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Login a user and generate a token.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, token, error_message)
            success: True if login successful
            token: JWT token if successful, None otherwise
            error_message: Error message if failed, None if successful
        """
        if not username or not password:
            return False, None, "Username and password are required"

        if not self.user_storage.verify_user(username, password):
            return False, None, "Invalid credentials"

        token = self.token_manager.generate_token(username)
        return True, token, None

    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify a token and return the username.

        Args:
            token: JWT token to verify

        Returns:
            Username if token is valid, None otherwise
        """
        return self.token_manager.verify_token(token)
