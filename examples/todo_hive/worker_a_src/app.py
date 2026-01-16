"""
HTTP API application for Worker A.

This application provides:
- User login with JWT token generation
- Todo list management (create and list)
Uses Flask as the HTTP framework.
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

        user_info = auth_service.verify_token(token)
        if not user_info:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add user information to request context
        request.current_user = user_info.get('username')
        request.current_user_id = user_info.get('user_id')
        return f(*args, **kwargs)

    return decorated_function


# Authentication endpoints

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login a user and receive JWT token.

    Request body:
    {
        "username": "string",
        "password": "string"
    }

    Response (200):
    {
        "user": {
            "id": "uuid",
            "username": "string",
            "created_at": "ISO 8601 string"
        },
        "token": "jwt_token_string"
    }

    Response (401):
    {
        "error": "error message"
    }
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    success, response_data, error = auth_service.login(username, password)

    if success:
        return jsonify(response_data), 200
    else:
        return jsonify({'error': error or 'Login failed'}), 401


@app.route('/api/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current authenticated user information.

    Requires: Bearer token in Authorization header

    Response (200):
    {
        "user": {
            "id": "uuid",
            "username": "string",
            "created_at": "ISO 8601 string"
        }
    }
    """
    user = auth_service.get_user_by_token(
        request.headers.get('Authorization', '').split(' ')[1]
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': user['id'],
        'username': user['username'],
        'created_at': user['created_at']
    }

    return jsonify({'user': user_data}), 200


# Todo endpoints

@app.route('/api/todos', methods=['POST'])
@require_auth
def create_todo():
    """
    Create a new todo item for the authenticated user.

    Requires: Bearer token in Authorization header

    Request body:
    {
        "content": "string"
    }

    Response (201):
    {
        "todo": {
            "id": "uuid",
            "content": "string",
            "user_id": "uuid",
            "created_at": "ISO 8601 string"
        }
    }

    Response (400):
    {
        "error": "error message"
    }
    """
    data = request.get_json() or {}
    content = data.get('content')
    user_id = request.current_user_id

    success, todo_data, error = todo_service.create_todo(content, user_id)

    if success:
        return jsonify({'todo': todo_data}), 201
    else:
        return jsonify({'error': error or 'Failed to create todo'}), 400


@app.route('/api/todos', methods=['GET'])
@require_auth
def list_todos():
    """
    List all todo items for the authenticated user.

    Requires: Bearer token in Authorization header

    Response (200):
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
    user_id = request.current_user_id

    success, todos_list, error = todo_service.list_todos(user_id)

    if success:
        return jsonify({'todos': todos_list or []}), 200
    else:
        return jsonify({'error': error or 'Failed to list todos'}), 400


# Health check endpoint

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Response (200):
    {
        "status": "healthy",
        "service": "Worker A API"
    }
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Worker A API'
    }), 200


# Root endpoint

@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint with API information.

    Response (200):
    {
        "service": "Worker A API",
        "version": "1.0.0",
        "endpoints": {
            "login": "POST /api/login",
            "me": "GET /api/me",
            "create_todo": "POST /api/todos",
            "list_todos": "GET /api/todos",
            "health": "GET /health"
        }
    }
    """
    return jsonify({
        'service': 'Worker A API',
        'version': '1.0.0',
        'endpoints': {
            'login': 'POST /api/login',
            'me': 'GET /api/me',
            'create_todo': 'POST /api/todos',
            'list_todos': 'GET /api/todos',
            'health': 'GET /health'
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)