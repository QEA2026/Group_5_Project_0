"""
Custom exceptions for the Employee Expense Manager.

Service/repository code raises these; Flask error handlers in api_server.py
map them to the right HTTP status codes and JSON responses.
"""


class AppError(Exception):
    """Base class for all app exceptions. Carries an HTTP status code and a
    user-facing message so the Flask error handler can respond without any
    extra logic."""
    status_code: int = 500
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class AuthenticationError(AppError):
    """Wrong username or password at login."""
    status_code = 401
    default_message = "Invalid username or password."


class TokenExpiredError(AppError):
    """JWT token is past its expiry time — user needs to log in again."""
    status_code = 401
    default_message = "Session has expired. Please log in again."


class TokenInvalidError(AppError):
    """JWT token is malformed or the signature doesn't match."""
    status_code = 401
    default_message = "Invalid authentication token."


class AccessDeniedError(AppError):
    """User is authenticated but doesn't have permission for this action."""
    status_code = 403
    default_message = "You do not have permission to perform this action."


class NotFoundError(AppError):
    """Generic 404 — the thing being asked for doesn't exist."""
    status_code = 404
    default_message = "The requested resource was not found."


class ExpenseNotFoundError(NotFoundError):
    """Expense ID doesn't exist or was already deleted."""
    default_message = "Expense not found."


class UserNotFoundError(NotFoundError):
    """No user with the given ID exists in the database."""
    default_message = "User not found."


class ExpenseOwnershipError(AccessDeniedError):
    """Expense exists but belongs to a different user."""
    default_message = "You do not have access to this expense."


class ExpenseAlreadyReviewedError(AppError):
    """Tried to edit or delete an expense that a manager already approved or denied."""
    status_code = 409
    default_message = "This expense has already been reviewed and cannot be modified."


class InvalidExpenseError(AppError):
    """Expense data failed a business rule — bad amount, missing description, invalid date, etc."""
    status_code = 400
    default_message = "Invalid expense data."


class DatabaseError(AppError):
    """Something went wrong at the SQLite level. The original exception is
    always chained so the log shows the full cause."""
    status_code = 500
    default_message = "A database error occurred."
