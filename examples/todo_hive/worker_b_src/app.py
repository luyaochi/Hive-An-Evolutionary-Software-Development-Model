"""
HTTP API application for Worker B.

This application provides user registration with JWT token generation.
Uses Flask as the HTTP framework.
"""

from flask import Flask, request, jsonify
from functools import wraps
from auth.auth_service import AuthService


app = Flask(__name__)

# Initialize authentication service
auth_service = AuthService()


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

@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user and receive JWT token.

    Request body:
    {
        "username": "string",
        "password": "string"
    }

    Response (201):
    {
        "user": {
            "id": "uuid",
            "username": "string",
            "created_at": "ISO 8601 string"
        },
        "token": "jwt_token_string"
    }

    Response (400):
    {
        "error": "error message"
    }
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    success, response_data, error = auth_service.register(username, password)

    if success:
        return jsonify(response_data), 201
    else:
        return jsonify({'error': error or 'Registration failed'}), 400


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


@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    """
    Verify a JWT token.

    Request body:
    {
        "token": "jwt_token_string"
    }

    Response (200):
    {
        "valid": true,
        "user": {
            "user_id": "uuid",
            "username": "string"
        }
    }

    Response (200, invalid token):
    {
        "valid": false,
        "error": "error message"
    }
    """
    data = request.get_json() or {}
    token = data.get('token')

    if not token:
        return jsonify({'valid': False, 'error': 'Token is required'}), 400

    user_info = auth_service.verify_token(token)

    if user_info:
        return jsonify({
            'valid': True,
            'user': user_info
        }), 200
    else:
        return jsonify({
            'valid': False,
            'error': 'Invalid or expired token'
        }), 200


# Health check endpoint

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Response (200):
    {
        "status": "healthy",
        "service": "Worker B Authentication API"
    }
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Worker B Authentication API'
    }), 200


# Root endpoint

@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint with API information.

    Response (200):
    {
        "service": "Worker B Authentication API",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /api/register",
            "login": "POST /api/login",
            "me": "GET /api/me",
            "verify_token": "POST /api/verify-token",
            "health": "GET /health"
        }
    }
    """
    return jsonify({
        'service': 'Worker B Authentication API',
        'version': '1.0.0',
        'endpoints': {
            'register': 'POST /api/register',
            'login': 'POST /api/login',
            'me': 'GET /api/me',
            'verify_token': 'POST /api/verify-token',
            'health': 'GET /health'
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001)
