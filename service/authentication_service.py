import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional

from exceptions import AuthenticationError, TokenExpiredError, TokenInvalidError, UserNotFoundError
from repository.user_model import User
from repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthenticationService:

    def __init__(self, user_repository: UserRepository, jwt_secret_key: str = 'your-secret-key'):
        self.user_repository = user_repository
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = 'HS256'
        self.token_expiry_hours = 24

    def authenticate_user(self, username: str, password: str) -> User:
        logger.debug("Auth attempt: username=%s", username)
        user = self.user_repository.find_by_username(username)
        if user and user.password == password:
            logger.info("Auth successful: username=%s", username)
            return user
        logger.warning("Auth failed: username=%s", username)
        raise AuthenticationError()

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            logger.warning("User not found: id=%s", user_id)
            raise UserNotFoundError(f"User {user_id} not found.")
        return user

    def generate_jwt_token(self, user: User) -> str:
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.now() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.now(),
        }
        return jwt.encode(payload, self.jwt_secret_key, algorithm=self.jwt_algorithm)

    def validate_jwt_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.jwt_secret_key, algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()

    def get_user_from_token(self, token: str) -> Optional[User]:
        """Returns None on any token failure — used by the auth decorator."""
        try:
            payload = self.validate_jwt_token(token)
            return self.user_repository.find_by_id(payload['user_id'])
        except (TokenExpiredError, TokenInvalidError):
            return None

    def get_all_users(self) -> list[User]:
        return self.user_repository.find_all()
