"""
JWT token manager implementation for Worker A.

This implementation follows worker_b_src pattern:
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
    
    This implementation follows worker_b_src pattern:
    - Stateless token generation with UUID and username
    - Token verification
    - No server-side session storage required
    - Suitable for distributed systems
    """

    def __init__(self, secret_key: str = "worker_a_secret_key", expires_in_hours: int = 24):
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