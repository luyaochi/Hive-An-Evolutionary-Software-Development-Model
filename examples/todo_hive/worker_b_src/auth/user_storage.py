"""
File-based user storage implementation for Worker B.

This implements 方案 B1: 檔案基礎用戶存儲 (file-based user storage).

Design decisions:
- JSON file format for data persistence
- UUID as user identifier
- bcrypt for password hashing
- Simple file-based storage without external dependencies (except bcrypt for security)
"""

import json
import os
import uuid
from typing import Optional, Dict
import bcrypt


class FileBasedUserStorage:
    """
    File-based user storage using JSON files with UUID identifiers.

    This implementation provides:
    - Persistent user data storage in JSON format
    - UUID-based user identification
    - Password hashing using bcrypt
    - Read/write user information
    - User existence checking

    Storage format:
    {
        "users": [
            {
                "id": "uuid",
                "username": "string",
                "password_hash": "string",
                "created_at": "ISO 8601 string"
            }
        ]
    }
    """

    def __init__(self, storage_file: str = "users_b.json"):
        """
        Initialize file-based user storage.

        Args:
            storage_file: Path to the JSON file for storing users
        """
        self.storage_file = storage_file
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Ensure the storage file exists, create if not."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({"users": []}, f)

    def _load_users(self) -> Dict:
        """Load users from storage file."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure "users" key exists
                if "users" not in data:
                    data["users"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}

    def _save_users(self, data: Dict):
        """Save users to storage file."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def register_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Register a new user with UUID identifier.

        Args:
            username: Username
            password: Plain text password (will be hashed)

        Returns:
            User dictionary if registration successful, None if user already exists
        """
        data = self._load_users()
        users = data.get("users", [])

        # Check if username already exists
        if any(user.get('username') == username for user in users):
            return None

        # Generate UUID for user
        user_id = str(uuid.uuid4())

        # Hash password using bcrypt
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Create user entry
        from datetime import datetime
        user = {
            'id': user_id,
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat()
        }

        users.append(user)
        data["users"] = users
        self._save_users(data)

        return user

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get a user by username.

        Args:
            username: Username to look up

        Returns:
            User dictionary if found, None otherwise
        """
        data = self._load_users()
        users = data.get("users", [])

        for user in users:
            if user.get('username') == username:
                return user

        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get a user by UUID.

        Args:
            user_id: User UUID to look up

        Returns:
            User dictionary if found, None otherwise
        """
        data = self._load_users()
        users = data.get("users", [])

        for user in users:
            if user.get('id') == user_id:
                return user

        return None

    def username_exists(self, username: str) -> bool:
        """
        Check if a username already exists.

        Args:
            username: Username to check

        Returns:
            True if username exists, False otherwise
        """
        return self.get_user_by_username(username) is not None

    def verify_password(self, username: str, password: str) -> bool:
        """
        Verify a password for a user.

        Args:
            username: Username
            password: Plain text password to verify

        Returns:
            True if password is correct, False otherwise
        """
        user = self.get_user_by_username(username)
        if not user:
            return False

        stored_hash = user.get('password_hash', '')
        if not stored_hash:
            return False

        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )
        except Exception:
            return False
