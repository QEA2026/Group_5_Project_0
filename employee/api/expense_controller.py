"""
Expense management endpoints.
"""
from flask import Blueprint, request, jsonify, current_app

from api.auth import require_employee_auth, get_current_user
from service.expense_service import ExpenseService

expense_bp = Blueprint('expense', __name__, url_prefix='/api/expenses')


def get_expense_service() -> ExpenseService:
    return current_app.expense_service


@expense_bp.route('', methods=['POST'])
@require_employee_auth
def submit_expense():
    """Submit a new expense."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400

    amount = data.get('amount')
    description = data.get('description')
    date = data.get('date')

    if amount is None or description is None:
        return jsonify({'error': 'Amount and description are required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Amount must be a valid number'}), 400

    current_user = get_current_user()
    expense = get_expense_service().submit_expense(
        user_id=current_user.id,
        amount=amount,
        description=description,
        date=date,
    )

    return jsonify({
        'message': 'Expense submitted successfully',
        'expense': {
            'id': expense.id,
            'user_id': expense.user_id,
            'amount': expense.amount,
            'description': expense.description,
            'date': expense.date,
            'status': 'pending',
        },
    }), 201


@expense_bp.route('', methods=['GET'])
@require_employee_auth
def get_expenses():
    """Get all expenses for the current user."""
    status_filter = request.args.get('status')
    current_user = get_current_user()

    expenses_with_status = get_expense_service().get_expense_history(
        user_id=current_user.id,
        status_filter=status_filter,
    )

    expenses_data = [
        {
            'id': expense.id,
            'user_id': expense.user_id,
            'amount': expense.amount,
            'description': expense.description,
            'date': expense.date,
            'status': approval.status,
            'comment': approval.comment,
            'review_date': approval.review_date,
        }
        for expense, approval in expenses_with_status
    ]

    return jsonify({'expenses': expenses_data, 'count': len(expenses_data)})


@expense_bp.route('/<int:expense_id>', methods=['GET'])
@require_employee_auth
def get_expense(expense_id):
    """Get a specific expense by ID."""
    current_user = get_current_user()
    expense, approval = get_expense_service().get_expense_with_status(expense_id, current_user.id)

    return jsonify({
        'expense': {
            'id': expense.id,
            'user_id': expense.user_id,
            'amount': expense.amount,
            'description': expense.description,
            'date': expense.date,
            'status': approval.status,
            'comment': approval.comment,
            'review_date': approval.review_date,
        }
    })


@expense_bp.route('/<int:expense_id>', methods=['PUT'])
@require_employee_auth
def update_expense(expense_id):
    """Update an existing expense (only if pending)."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON data required'}), 400

    amount = data.get('amount')
    description = data.get('description')
    date = data.get('date')

    if amount is None or description is None or date is None:
        return jsonify({'error': 'Amount, description, and date are required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Amount must be a valid number'}), 400

    current_user = get_current_user()
    updated_expense = get_expense_service().update_expense(
        expense_id=expense_id,
        user_id=current_user.id,
        amount=amount,
        description=description,
        date=date,
    )

    return jsonify({
        'message': 'Expense updated successfully',
        'expense': {
            'id': updated_expense.id,
            'user_id': updated_expense.user_id,
            'amount': updated_expense.amount,
            'description': updated_expense.description,
            'date': updated_expense.date,
        },
    })


@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
@require_employee_auth
def delete_expense(expense_id):
    """Delete an expense (only if pending)."""
    current_user = get_current_user()
    get_expense_service().delete_expense(expense_id, current_user.id)
    return jsonify({'message': 'Expense deleted successfully'})
