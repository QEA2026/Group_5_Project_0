from flask import request, jsonify, current_app
from service.authentication_service import AuthenticationService


def get_auth_service() -> AuthenticationService:
    return current_app.auth_service


def require_employee_auth(f):
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('jwt_token')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401

        auth_service = get_auth_service()
        user = auth_service.get_user_from_token(token)

        if not user or user.role != 'Employee':
            return jsonify({'error': 'Access denied'}), 403

        request.current_user = user
        return f(*args, **kwargs)

    # Flask uses function names as endpoint identifiers, so without this
    # every decorated route would clash under the name 'decorated_function'
    decorated_function.__name__ = f.__name__
    return decorated_function


def get_current_user():
    return getattr(request, 'current_user', None)
