"""
JSON file-based todo storage implementation.

This implements 方案 C2: JSON 檔案持久化 (JSON file persistence).
"""

import json
import os
import uuid
from typing import List, Dict, Optional
from datetime import datetime


class JSONTodoStorage:
    """
    JSON file-based todo storage.

    This implementation provides:
    - Persistent todo item storage
    - Read/write todo data
    - User association via user_id
    """

    def __init__(self, storage_file: str = "todos.json"):
        """
        Initialize JSON todo storage.

        Args:
            storage_file: Path to the JSON file for storing todos
        """
        self.storage_file = storage_file
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Ensure the storage file exists, create if not."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_todos(self) -> List[Dict]:
        """Load todos from storage file."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_todos(self, todos: List[Dict]):
        """Save todos to storage file."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)

    def create_todo(self, user_id: str, content: str) -> Dict:
        """
        Create a new todo item.

        Args:
            user_id: Username of the authenticated user
            content: Todo item content

        Returns:
            Created todo item dictionary
        """
        todos = self._load_todos()

        todo_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        todo = {
            'id': todo_id,
            'user_id': user_id,
            'content': content,
            'created_at': timestamp
        }

        todos.append(todo)
        self._save_todos(todos)

        return todo

    def list_todos(self, user_id: str) -> List[Dict]:
        """
        List all todos for a specific user.

        Args:
            user_id: Username to filter todos

        Returns:
            List of todo items for the user
        """
        todos = self._load_todos()
        return [todo for todo in todos if todo.get('user_id') == user_id]

    def get_todo(self, todo_id: str, user_id: str) -> Optional[Dict]:
        """
        Get a specific todo item by ID (if it belongs to the user).

        Args:
            todo_id: Todo item ID
            user_id: Username to verify ownership

        Returns:
            Todo item if found and belongs to user, None otherwise
        """
        todos = self._load_todos()
        for todo in todos:
            if todo.get('id') == todo_id and todo.get('user_id') == user_id:
                return todo
        return None
