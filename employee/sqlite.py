"""
Quick utility to initialise the DB and list current users.
Usage: python sqlite.py
"""
from repository.database import DatabaseConnection


def list_users(db: DatabaseConnection) -> None:
    """Prints all users in the database. Handy for checking who's been
    seeded without having to open a SQLite client."""
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT id, username, role FROM users ORDER BY id"
        ).fetchall()

    if not rows:
        print(f"No users found in {db.db_path}.")
        return

    print(f"Users in {db.db_path}:")
    for row in rows:
        print(f"  [{row['id']}] {row['username']} ({row['role']})")


def main():
    """Creates the tables if they don't exist yet, then lists all users."""
    db = DatabaseConnection('employees.db')
    db.initialize_database()
    list_users(db)


if __name__ == '__main__':
    main()
