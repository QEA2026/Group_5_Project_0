import logging
from datetime import datetime

from exceptions import ExpenseNotFoundError, ExpenseOwnershipError, ExpenseAlreadyReviewedError, InvalidExpenseError;

from repository.expense_model import Expense
from repository.approval_model import Approval
from repository.expense_repository import ExpenseRepository
from repository.approval_repository import ApprovalRepository

logger = logging.getLogger(__name__)


class ExpenseService:

    def __init__(self, expense_repository: ExpenseRepository, approval_repository: ApprovalRepository):
        self.expense_repository = expense_repository
        self.approval_repository = approval_repository

    def _validate_date(self, date_str: str) -> str:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise InvalidExpenseError("Date must be a valid date in YYYY-MM-DD format.")
        return date_str

    def submit_expense(self, user_id: int, amount: float, description: str, date: str = None) -> Expense:
        if amount <= 0:
            raise InvalidExpenseError("Amount must be greater than 0.")
        if not description or not description.strip():
            raise InvalidExpenseError("Description is required.")

        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        else:
            self._validate_date(date)

        expense = Expense(id=None, user_id=user_id, amount=amount,
                          description=description.strip(), date=date)
        result = self.expense_repository.create(expense)
        logger.info("Expense submitted: id=%s user_id=%s amount=%.2f", result.id, user_id, amount)
        return result

    def get_user_expenses_with_status(self, user_id: int) -> list[tuple[Expense, Approval]]:
        return self.approval_repository.find_expenses_with_status_for_user(user_id)

    def get_expense_by_id(self, expense_id: int, user_id: int) -> Expense:
        expense = self.expense_repository.find_by_id(expense_id)
        if not expense:
            logger.warning("Expense not found: id=%s", expense_id)
            raise ExpenseNotFoundError(f"Expense {expense_id} not found.")
        if expense.user_id != user_id:
            logger.warning("Ownership violation: expense_id=%s owner=%s requester=%s",
                           expense_id, expense.user_id, user_id)
            raise ExpenseOwnershipError()
        return expense

    def get_expense_with_status(self, expense_id: int, user_id: int) -> tuple[Expense, Approval]:
        expense = self.get_expense_by_id(expense_id, user_id)
        approval = self.approval_repository.find_by_expense_id(expense_id)
        if not approval:
            # Shouldn't happen — every expense gets an approval row on creation
            logger.error("Missing approval record for expense_id=%s", expense_id)
            raise ExpenseNotFoundError(f"Approval record missing for expense {expense_id}.")
        return expense, approval

    def update_expense(self, expense_id: int, user_id: int, amount: float,
                       description: str, date: str) -> Expense:
        expense, approval = self.get_expense_with_status(expense_id, user_id)

        if approval.status != 'pending':
            raise ExpenseAlreadyReviewedError()
        if amount <= 0:
            raise InvalidExpenseError("Amount must be greater than 0.")
        if not description or not description.strip():
            raise InvalidExpenseError("Description is required.")
        self._validate_date(date)

        expense.amount = amount
        expense.description = description.strip()
        expense.date = date

        result = self.expense_repository.update(expense)
        logger.info("Expense updated: id=%s user_id=%s", expense_id, user_id)
        return result

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        _, approval = self.get_expense_with_status(expense_id, user_id)

        if approval.status != 'pending':
            raise ExpenseAlreadyReviewedError()

        deleted = self.expense_repository.delete(expense_id)
        if deleted:
            logger.info("Expense deleted: id=%s user_id=%s", expense_id, user_id)
        return deleted

    def get_expense_history(self, user_id: int, status_filter: str = None) -> list[tuple[Expense, Approval]]:
        all_expenses = self.get_user_expenses_with_status(user_id)
        if status_filter in ('pending', 'approved', 'denied'):
            return [(e, a) for e, a in all_expenses if a.status == status_filter]
        return all_expenses

    def get_all_expenses_with_status(self) -> list[tuple[Expense, Approval]]:
        return self.approval_repository.find_all_expenses_with_status()
