"""
JWT token manager implementation for Worker B.

This implements 方案 B1: 無狀態令牌 (stateless tokens) using JWT.

Design decisions:
- JWT tokens for stateless authentication
- Configurable expiration time
- User ID (UUID) and username in token payload
"""

import jwt
from typing import Optional, Dict
from datetime import datetime, timedelta


class JWTTokenManager:
    """
    JWT-based token manager for stateless authentication.

    This implementation provides:
    - Stateless token generation with UUID and username
    - Token verification
    - No server-side session storage required
    - Suitable for distributed systems
    """

    def __init__(self, secret_key: str = "worker_b_secret_key", expires_in_hours: int = 24):
        """
        Initialize JWT token manager.

        Args:
            secret_key: Secret key for signing tokens
            expires_in_hours: Token expiration time in hours
        """
        self.secret_key = secret_key
        self.expires_in_hours = expires_in_hours
        self.algorithm = 'HS256'

    def generate_token(self, user_id: str, username: str) -> str:
        """
        Generate a JWT token for a user.

        Args:
            user_id: User UUID
            username: Username

        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expiration = now + timedelta(hours=self.expires_in_hours)

        payload = {
            'user_id': user_id,
            'username': username,
            'iat': now,
            'exp': expiration
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, str]]:
        """
        Verify and extract user information from a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            Dictionary with 'user_id' and 'username' if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return {
                'user_id': payload.get('user_id'),
                'username': payload.get('username')
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def is_token_valid(self, token: str) -> bool:
        """
        Check if a token is valid.

        Args:
            token: JWT token string to check

        Returns:
            True if token is valid, False otherwise
        """
        return self.verify_token(token) is not None

    def get_username_from_token(self, token: str) -> Optional[str]:
        """
        Extract username from token (convenience method).

        Args:
            token: JWT token string

        Returns:
            Username if token is valid, None otherwise
        """
        user_info = self.verify_token(token)
        if user_info:
            return user_info.get('username')
        return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID (UUID) from token (convenience method).

        Args:
            token: JWT token string

        Returns:
            User ID (UUID) if token is valid, None otherwise
        """
        user_info = self.verify_token(token)
        if user_info:
            return user_info.get('user_id')
        return None
