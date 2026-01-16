"""
File-based user storage implementation.

This implements 方案 A2: 檔案基礎用戶存儲 (file-based user storage).
"""

import json
import os
from typing import Optional, Dict
import bcrypt


class FileUserStorage:
    """
    File-based user storage using JSON files.

    This implementation provides:
    - Persistent user data storage
    - Read/write user information
    - Password hashing using bcrypt
    """

    def __init__(self, storage_file: str = "users.json"):
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
                json.dump({}, f)

    def _load_users(self) -> Dict[str, Dict]:
        """Load users from storage file."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_users(self, users: Dict[str, Dict]):
        """Save users to storage file."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    def register_user(self, username: str, password: str) -> bool:
        """
        Register a new user.

        Args:
            username: Username
            password: Plain text password (will be hashed)

        Returns:
            True if registration successful, False if user already exists
        """
        users = self._load_users()

        if username in users:
            return False

        # Hash password using bcrypt
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        users[username] = {
            'username': username,
            'password_hash': password_hash
        }

        self._save_users(users)
        return True

    def verify_user(self, username: str, password: str) -> bool:
        """
        Verify user credentials.

        Args:
            username: Username
            password: Plain text password to verify

        Returns:
            True if credentials are valid, False otherwise
        """
        users = self._load_users()

        if username not in users:
            return False

        stored_hash = users[username]['password_hash']
        return bcrypt.checkpw(
            password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists.

        Args:
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        users = self._load_users()
        return username in users
