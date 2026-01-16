"""
HTTP API application for Todo List system.

This application integrates authentication and todo management domains
using Flask as the HTTP framework.
"""

from flask import Flask, request, jsonify
from functools import wraps
from auth.auth_service import AuthService
from todos.todo_service import TodoService


app = Flask(__name__)

# Initialize services
auth_service = AuthService()
todo_service = TodoService()


def require_auth(f):
    """Decorator to require authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Format: "Bearer <token>"
            except IndexError:
                pass

        if not token:
            return jsonify({'error': 'Authentication required'}), 401

        username = auth_service.verify_token(token)
        if not username:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add username to request context
        request.current_user = username
        return f(*args, **kwargs)

    return decorated_function


# Authentication endpoints

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    success, error = auth_service.register(username, password)

    if success:
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': error or 'Registration failed'}), 400


@app.route('/api/login', methods=['POST'])
def login():
    """Login a user and get a token."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    success, token, error = auth_service.login(username, password)

    if success:
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': error or 'Login failed'}), 401


# Todo endpoints

@app.route('/api/todos', methods=['POST'])
@require_auth
def create_todo():
    """Create a new todo item."""
    data = request.get_json() or {}
    content = data.get('content')
    user_id = request.current_user

    success, todo, error = todo_service.create_todo(user_id, content)

    if success:
        return jsonify(todo), 201
    else:
        return jsonify({'error': error or 'Todo creation failed'}), 400


@app.route('/api/todos', methods=['GET'])
@require_auth
def list_todos():
    """List all todos for the authenticated user."""
    user_id = request.current_user
    todos = todo_service.list_todos(user_id)
    return jsonify({'todos': todos}), 200


# Health check endpoint

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
