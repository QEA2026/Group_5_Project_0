import logging
import sqlite3
import os
from typing import Optional

from exceptions import DatabaseError

logger = logging.getLogger(__name__)


class DatabaseConnection:

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'employees.db')

    def get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            logger.exception("Failed to open database at %s", self.db_path)
            raise DatabaseError(f"Cannot connect to database: {e}") from e

    def initialize_database(self):
        logger.info("Initialising database at %s", self.db_path)
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                ''')
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS approvals (
                        id INTEGER PRIMARY KEY,
                        expense_id INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        reviewer INTEGER,
                        comment TEXT,
                        review_date TEXT,
                        FOREIGN KEY (expense_id) REFERENCES expenses (id),
                        FOREIGN KEY (reviewer) REFERENCES users (id)
                    )
                ''')
                conn.commit()
            logger.info("Database ready.")
        except sqlite3.Error as e:
            logger.exception("Database initialisation failed")
            raise DatabaseError(f"Failed to initialise database: {e}") from e
