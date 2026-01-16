"""
Todo list management domain module.

This module implements todo list management using:
- JSON file persistence (方案 C2)
"""

from .todo_storage import JSONTodoStorage
from .todo_service import TodoService

__all__ = ['JSONTodoStorage', 'TodoService']
