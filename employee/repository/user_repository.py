import logging
import sqlite3
from typing import Optional

from exceptions import DatabaseError
from .user_model import User
from .database import DatabaseConnection

logger = logging.getLogger(__name__)


class UserRepository:
    """Handles all database reads and writes for users."""

    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, username, password, role FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    return User(id=row['id'], username=row['username'],
                                password=row['password'], role=row['role'])
            return None
        except sqlite3.Error as e:
            logger.exception("Failed to find user by username=%s", username)
            raise DatabaseError(f"Failed to retrieve user: {e}") from e

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find a user by ID."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, username, password, role FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return User(id=row['id'], username=row['username'],
                                password=row['password'], role=row['role'])
            return None
        except sqlite3.Error as e:
            logger.exception("Failed to find user by id=%s", user_id)
            raise DatabaseError(f"Failed to retrieve user: {e}") from e

    def create(self, user: User) -> User:
        """Create a new user."""
        logger.debug("Creating user username=%s role=%s", user.username, user.role)
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (user.username, user.password, user.role)
                )
                user.id = cursor.lastrowid
                conn.commit()
            logger.info("User created: id=%s username=%s", user.id, user.username)
            return user
        except sqlite3.IntegrityError as e:
            logger.warning("Duplicate username=%s: %s", user.username, e)
            raise DatabaseError(f"Username '{user.username}' already exists.") from e
        except sqlite3.Error as e:
            logger.exception("Failed to create user username=%s", user.username)
            raise DatabaseError(f"Failed to create user: {e}") from e

    def find_all(self) -> list[User]:
        """Return all users."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, username, password, role FROM users ORDER BY id"
                )
                return [
                    User(id=row['id'], username=row['username'],
                         password=row['password'], role=row['role'])
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            logger.exception("Failed to list all users")
            raise DatabaseError(f"Failed to retrieve users: {e}") from e
