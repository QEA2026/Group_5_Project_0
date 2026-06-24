import logging
import sqlite3
from typing import Optional

from exceptions import DatabaseError
from .expense_model import Expense
from .approval_model import Approval
from .database import DatabaseConnection

logger = logging.getLogger(__name__)


class ApprovalRepository:
    """Handles all database reads and writes for expense approvals."""

    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def find_by_expense_id(self, expense_id: int) -> Optional[Approval]:
        """Find approval by expense ID."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, expense_id, status, reviewer, comment, review_date "
                    "FROM approvals WHERE expense_id = ?",
                    (expense_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Approval(id=row['id'], expense_id=row['expense_id'],
                                    status=row['status'], reviewer=row['reviewer'],
                                    comment=row['comment'], review_date=row['review_date'])
            return None
        except sqlite3.Error as e:
            logger.exception("Failed to find approval for expense_id=%s", expense_id)
            raise DatabaseError(f"Failed to retrieve approval: {e}") from e

    def find_expenses_with_status_for_user(self, user_id: int) -> list[tuple]:
        """Find all expenses with their approval status for a user."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT e.id, e.amount, e.description, e.date,
                           a.id AS approval_id, a.status, a.reviewer, a.comment, a.review_date
                    FROM expenses e
                    JOIN approvals a ON e.id = a.expense_id
                    WHERE e.user_id = ?
                    ORDER BY e.date DESC
                ''', (user_id,))

                results = []
                for row in cursor.fetchall():
                    expense = Expense(id=row['id'], user_id=user_id,
                                      amount=row['amount'], description=row['description'],
                                      date=row['date'])
                    approval = Approval(id=row['approval_id'], expense_id=row['id'],
                                        status=row['status'], reviewer=row['reviewer'],
                                        comment=row['comment'], review_date=row['review_date'])
                    results.append((expense, approval))
                return results
        except sqlite3.Error as e:
            logger.exception("Failed to list expenses with status for user_id=%s", user_id)
            raise DatabaseError(f"Failed to retrieve expense history: {e}") from e

    def update_status(self, expense_id: int, status: str, reviewer_id: Optional[int] = None,
                      comment: Optional[str] = None, review_date: Optional[str] = None) -> bool:
        """Update approval status."""
        logger.debug("Updating approval status: expense_id=%s status=%s", expense_id, status)
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE approvals SET status = ?, reviewer = ?, comment = ?, review_date = ? "
                    "WHERE expense_id = ?",
                    (status, reviewer_id, comment, review_date, expense_id)
                )
                conn.commit()
            updated = cursor.rowcount > 0
            if updated:
                logger.info("Approval updated: expense_id=%s new_status=%s", expense_id, status)
            else:
                logger.warning("Approval update had no effect for expense_id=%s", expense_id)
            return updated
        except sqlite3.Error as e:
            logger.exception("Failed to update approval for expense_id=%s", expense_id)
            raise DatabaseError(f"Failed to update approval status: {e}") from e

    def find_all_expenses_with_status(self) -> list:
        """Return every expense in the system with its approval status."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT e.id, e.user_id, e.amount, e.description, e.date,
                           a.id AS approval_id, a.status, a.reviewer, a.comment, a.review_date
                    FROM expenses e
                    JOIN approvals a ON e.id = a.expense_id
                    ORDER BY e.user_id, e.date DESC
                ''')
                results = []
                for row in cursor.fetchall():
                    expense = Expense(id=row['id'], user_id=row['user_id'],
                                      amount=row['amount'], description=row['description'],
                                      date=row['date'])
                    approval = Approval(id=row['approval_id'], expense_id=row['id'],
                                        status=row['status'], reviewer=row['reviewer'],
                                        comment=row['comment'], review_date=row['review_date'])
                    results.append((expense, approval))
                return results
        except sqlite3.Error as e:
            logger.exception("Failed to retrieve all expenses with status")
            raise DatabaseError(f"Failed to retrieve all expenses: {e}") from e
