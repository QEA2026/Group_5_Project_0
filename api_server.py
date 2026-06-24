#!/usr/bin/env python3
"""
Flask API server for the Employee Expense Manager.

Run directly (`python api_server.py`) or let main.py start it automatically.
"""
import logging

from flask import Flask, jsonify

from logging_config import configure_logging
from exceptions import AppError
from repository import (
    DatabaseConnection,
    UserRepository,
    ExpenseRepository,
    ApprovalRepository,
    User,
)
from service import AuthenticationService, ExpenseService
from api import auth_bp, expense_bp, admin_bp

configure_logging()
logger = logging.getLogger(__name__)


def _seed_sample_users(user_repository: UserRepository) -> None:
    if user_repository.find_by_username('employee1'):
        return

    sample_users = [
        User(id=None, username='employee1', password='password123', role='Employee'),
        User(id=None, username='employee2', password='pass456', role='Employee'),
        User(id=None, username='employee3', password='secure789', role='Employee'),
    ]
    for user in sample_users:
        user_repository.create(user)
    logger.info("Seeded %d sample users.", len(sample_users))


def create_app(db_path: str = None) -> Flask:
    app = Flask(__name__)

    db_connection = DatabaseConnection(db_path)
    db_connection.initialize_database()

    user_repository = UserRepository(db_connection)
    expense_repository = ExpenseRepository(db_connection)
    approval_repository = ApprovalRepository(db_connection)

    _seed_sample_users(user_repository)

    app.auth_service = AuthenticationService(
        user_repository,
        jwt_secret_key='employee-api-secret-key',
    )
    app.expense_service = ExpenseService(expense_repository, approval_repository)

    app.register_blueprint(auth_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(admin_bp)

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        logger.warning("AppError [%s]: %s", type(error).__name__, error.message)
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({'error': 'Endpoint not found.'}), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({'error': 'Method not allowed.'}), 405

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        logger.exception("Unhandled exception")
        return jsonify({'error': 'An unexpected server error occurred.'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    logger.info("Starting on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
