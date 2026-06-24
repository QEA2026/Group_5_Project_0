import logging
from flask import Blueprint, request, jsonify, make_response, current_app

from service.authentication_service import AuthenticationService

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_auth_service() -> AuthenticationService:
    return current_app.auth_service


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = get_auth_service().authenticate_user(username, password)
    token = get_auth_service().generate_jwt_token(user)
    logger.info("Login: user_id=%s username=%s", user.id, user.username)

    response = make_response(jsonify({
        'message': 'Login successful',
        'user': {'id': user.id, 'username': user.username, 'role': user.role},
    }))
    response.set_cookie('jwt_token', token, httponly=True, secure=False,
                        samesite='Lax', max_age=24 * 60 * 60)
    return response


@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Logout successful'}))
    response.set_cookie('jwt_token', '', httponly=True, secure=False,
                        samesite='Lax', expires=0)
    return response


@auth_bp.route('/status', methods=['GET'])
def status():
    token = request.cookies.get('jwt_token')
    if not token:
        return jsonify({'authenticated': False}), 200

    user = get_auth_service().get_user_from_token(token)
    if user:
        return jsonify({
            'authenticated': True,
            'user': {'id': user.id, 'username': user.username, 'role': user.role},
        })
    return jsonify({'authenticated': False}), 200
