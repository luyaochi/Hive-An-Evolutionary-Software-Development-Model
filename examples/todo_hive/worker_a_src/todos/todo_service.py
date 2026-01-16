"""
Todo service that manages todo operations.
"""

from typing import List, Dict, Tuple, Optional
from .todo_storage import JSONTodoStorage


class TodoService:
    """
    Todo service that handles todo item operations.
    """

    def __init__(self, storage_file: str = "todos.json"):
        """
        Initialize todo service.

        Args:
            storage_file: Path to todo storage file
        """
        self.todo_storage = JSONTodoStorage(storage_file)

    def create_todo(self, user_id: str, content: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Create a new todo item.

        Args:
            user_id: Username of the authenticated user
            content: Todo item content

        Returns:
            Tuple of (success, todo, error_message)
            success: True if creation successful
            todo: Created todo item if successful, None otherwise
            error_message: Error message if failed, None if successful
        """
        if not content or not content.strip():
            return False, None, "Todo content is required"

        todo = self.todo_storage.create_todo(user_id, content.strip())
        return True, todo, None

    def list_todos(self, user_id: str) -> List[Dict]:
        """
        List all todos for a user.

        Args:
            user_id: Username to filter todos

        Returns:
            List of todo items for the user
        """
        return self.todo_storage.list_todos(user_id)
