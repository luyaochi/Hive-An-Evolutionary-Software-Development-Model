"""
Todo service for Worker A.

This service coordinates todo list management functionality:
- Create todo items with validation
- List todo items for authenticated users
- Error handling
"""

from typing import Tuple, Optional, Dict, List
from .todo_storage import FileBasedTodoStorage


class TodoService:
    """
    Todo service that coordinates todo list management.
    
    This implementation provides:
    - Create todo items with validation
    - List todo items for authenticated users
    - Error handling for various scenarios
    - Integration with file-based todo storage
    """

    def __init__(self, storage_file: str = "todos_a.json"):
        """
        Initialize todo service.

        Args:
            storage_file: Path to todo storage file
        """
        self.todo_storage = FileBasedTodoStorage(storage_file)

    def create_todo(self, content: str, user_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Create a new todo item for a user.

        Args:
            content: Todo content/description
            user_id: User UUID who owns this todo

        Returns:
            Tuple of (success, todo_data, error_message)
            - success: True if creation successful, False otherwise
            - todo_data: Todo dictionary if successful, None otherwise
            - error_message: Error message if failed, None if successful
        """
        # Validate input
        if not content or not content.strip():
            return False, None, "Todo content cannot be empty"

        if not user_id or not user_id.strip():
            return False, None, "User ID is required"

        # Normalize content (strip whitespace)
        content = content.strip()

        # Create todo
        todo = self.todo_storage.create_todo(content, user_id)

        if todo is None:
            return False, None, "Failed to create todo"

        # Return todo data
        todo_response = {
            'id': todo['id'],
            'content': todo['content'],
            'user_id': todo['user_id'],
            'created_at': todo['created_at']
        }

        return True, todo_response, None

    def list_todos(self, user_id: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        List all todos for a specific user.

        Args:
            user_id: User UUID to filter todos

        Returns:
            Tuple of (success, todos_list, error_message)
            - success: True if successful, False otherwise
            - todos_list: List of todo dictionaries if successful, None otherwise
            - error_message: Error message if failed, None if successful
        """
        if not user_id or not user_id.strip():
            return False, None, "User ID is required"

        # Get todos for user
        todos = self.todo_storage.get_todos_by_user_id(user_id)

        # Return todo data (without internal fields if any)
        todos_response = [
            {
                'id': todo['id'],
                'content': todo['content'],
                'user_id': todo['user_id'],
                'created_at': todo['created_at']
            }
            for todo in todos
        ]

        return True, todos_response, None

    def validate_content(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate todo content format.

        Args:
            content: Todo content to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Todo content cannot be empty"

        content = content.strip()

        # Basic validation: content should be reasonable length
        if len(content) < 1:
            return False, "Todo content cannot be empty"

        if len(content) > 1000:
            return False, "Todo content must be at most 1000 characters"

        return True, None