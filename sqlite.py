import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, password TEXT, role TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS expenses (id INTEGER, user_id INTEGER, amount REAL, description TEXT, date TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS approvals (id INTEGER, expense_id INTEGER, status TEXT, reviewer INTEGER, comment TEXT, review_date TEXT)""")

#c.execute("""INSERT INTO users VALUES (2,'Daniel', 'pw2', 'Employee')""")

c.execute("""SELECT username FROM users""")

rows = c.fetchall()

for row in rows:
    print(rows)


conn.commit()

conn.close