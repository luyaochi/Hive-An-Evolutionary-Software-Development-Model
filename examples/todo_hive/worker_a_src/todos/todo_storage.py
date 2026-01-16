"""
File-based todo storage implementation for Worker A.

This implementation provides:
- JSON file format for data persistence
- UUID as todo identifier
- User association via user_id (UUID)
- Create and list operations
"""

import json
import os
import uuid
from typing import Optional, Dict, List
from datetime import datetime


class FileBasedTodoStorage:
    """
    File-based todo storage using JSON files with UUID identifiers.
    
    This implementation provides:
    - Persistent todo data storage in JSON format
    - UUID-based todo identification
    - User association via user_id
    - Create and list todo items
    - No update or delete operations

    Storage format:
    {
        "todos": [
            {
                "id": "uuid",
                "content": "string",
                "user_id": "uuid",
                "created_at": "ISO 8601 string"
            }
        ]
    }
    """

    def __init__(self, storage_file: str = "todos_a.json"):
        """
        Initialize file-based todo storage.

        Args:
            storage_file: Path to the JSON file for storing todos
        """
        self.storage_file = storage_file
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Ensure the storage file exists, create if not."""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({"todos": []}, f)

    def _load_todos(self) -> Dict:
        """Load todos from storage file."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure "todos" key exists
                if "todos" not in data:
                    data["todos"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"todos": []}

    def _save_todos(self, data: Dict):
        """Save todos to storage file."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_todo(self, content: str, user_id: str) -> Optional[Dict]:
        """
        Create a new todo item for a user.

        Args:
            content: Todo content/description
            user_id: User UUID who owns this todo

        Returns:
            Todo dictionary if creation successful, None otherwise
        """
        data = self._load_todos()
        todos = data.get("todos", [])

        # Generate UUID for todo
        todo_id = str(uuid.uuid4())

        # Create todo entry
        todo = {
            'id': todo_id,
            'content': content,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat()
        }

        todos.append(todo)
        data["todos"] = todos
        self._save_todos(data)

        return todo

    def get_todos_by_user_id(self, user_id: str) -> List[Dict]:
        """
        Get all todos for a specific user.

        Args:
            user_id: User UUID to filter todos

        Returns:
            List of todo dictionaries for the user
        """
        data = self._load_todos()
        todos = data.get("todos", [])

        # Filter todos by user_id
        user_todos = [todo for todo in todos if todo.get('user_id') == user_id]

        # Sort by created_at (newest first)
        user_todos.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return user_todos

    def get_todo_by_id(self, todo_id: str) -> Optional[Dict]:
        """
        Get a todo by ID.

        Args:
            todo_id: Todo UUID to look up

        Returns:
            Todo dictionary if found, None otherwise
        """
        data = self._load_todos()
        todos = data.get("todos", [])

        for todo in todos:
            if todo.get('id') == todo_id:
                return todo

        return None

    def get_all_todos(self) -> List[Dict]:
        """
        Get all todos (for debugging purposes).

        Returns:
            List of all todo dictionaries
        """
        data = self._load_todos()
        return data.get("todos", [])