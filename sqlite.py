import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

c.execute("""CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

c.execute("""CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    reviewer INTEGER,
    comment TEXT,
    review_date TEXT,
    FOREIGN KEY(expense_id) REFERENCES expenses(id),
    FOREIGN KEY(reviewer) REFERENCES users(id)
)
""")

#c.execute("""INSERT INTO users VALUES (1,'Ryan', 'pw913', 'Employee')""")

c.execute("""SELECT username FROM users""")

rows = c.fetchall()

for row in rows:
    print(row)


conn.commit()

conn.close