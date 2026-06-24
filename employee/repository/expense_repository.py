import logging
import sqlite3
from typing import Optional

from exceptions import DatabaseError
from .expense_model import Expense
from .database import DatabaseConnection

logger = logging.getLogger(__name__)


class ExpenseRepository:
    """Handles all database reads and writes for expenses."""

    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def create(self, expense: Expense) -> Expense:
        """Create a new expense and its initial approval record."""
        logger.debug("Creating expense for user_id=%s amount=%.2f", expense.user_id, expense.amount)
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO expenses (user_id, amount, description, date) VALUES (?, ?, ?, ?)",
                    (expense.user_id, expense.amount, expense.description, expense.date)
                )
                expense.id = cursor.lastrowid
                conn.execute(
                    "INSERT INTO approvals (expense_id, status) VALUES (?, 'pending')",
                    (expense.id,)
                )
                conn.commit()
            logger.info("Expense created: id=%s user_id=%s", expense.id, expense.user_id)
            return expense
        except sqlite3.Error as e:
            logger.exception("Failed to create expense for user_id=%s", expense.user_id)
            raise DatabaseError(f"Failed to create expense: {e}") from e

    def find_by_id(self, expense_id: int) -> Optional[Expense]:
        """Find an expense by ID."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, user_id, amount, description, date FROM expenses WHERE id = ?",
                    (expense_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Expense(id=row['id'], user_id=row['user_id'],
                                   amount=row['amount'], description=row['description'],
                                   date=row['date'])
            return None
        except sqlite3.Error as e:
            logger.exception("Failed to find expense id=%s", expense_id)
            raise DatabaseError(f"Failed to retrieve expense: {e}") from e

    def find_by_user_id(self, user_id: int) -> list[Expense]:
        """Find all expenses for a user."""
        try:
            with self.db_connection.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, user_id, amount, description, date FROM expenses "
                    "WHERE user_id = ? ORDER BY date DESC",
                    (user_id,)
                )
                return [
                    Expense(id=row['id'], user_id=row['user_id'],
                            amount=row['amount'], description=row['description'],
                            date=row['date'])
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as e:
            logger.exception("Failed to list expenses for user_id=%s", user_id)
            raise DatabaseError(f"Failed to retrieve expenses: {e}") from e

    def update(self, expense: Expense) -> Expense:
        """Update an existing expense."""
        logger.debug("Updating expense id=%s", expense.id)
        try:
            with self.db_connection.get_connection() as conn:
                conn.execute(
                    "UPDATE expenses SET amount = ?, description = ?, date = ? WHERE id = ?",
                    (expense.amount, expense.description, expense.date, expense.id)
                )
                conn.commit()
            logger.info("Expense updated: id=%s", expense.id)
            return expense
        except sqlite3.Error as e:
            logger.exception("Failed to update expense id=%s", expense.id)
            raise DatabaseError(f"Failed to update expense: {e}") from e

    def delete(self, expense_id: int) -> bool:
        """Delete an expense and its approval record."""
        logger.debug("Deleting expense id=%s", expense_id)
        try:
            with self.db_connection.get_connection() as conn:
                # approvals first — expenses has a FK that blocks deletion otherwise
                conn.execute("DELETE FROM approvals WHERE expense_id = ?", (expense_id,))
                cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info("Expense deleted: id=%s", expense_id)
            else:
                logger.warning("Delete had no effect for expense id=%s", expense_id)
            return deleted
        except sqlite3.Error as e:
            logger.exception("Failed to delete expense id=%s", expense_id)
            raise DatabaseError(f"Failed to delete expense: {e}") from e
