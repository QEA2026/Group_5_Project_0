# Employee Expense Manager

A CLI expense tracking app where employees can submit, view, edit, and delete expense reports. Built with Flask (REST API) + SQLite on the backend, driven by a terminal UI.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

`main.py` auto-starts the Flask API (`api_server.py`) as a background process if it's not already running. No manual server setup needed.

## Test credentials

These are seeded automatically on first run:

| Username  | Password    |
|-----------|-------------|
| employee1 | password123 |
| employee2 | pass456     |
| employee3 | secure789   |

## Project structure

```
api/            Flask blueprints (auth, expenses)
repository/     SQLite models and data access
service/        Business logic
api_client.py   HTTP wrapper the CLI uses to talk to the API
api_server.py   Flask app factory + server entry point
app.py          CLI controller
cli.py          Terminal view / prompts
main.py         Entry point
```

## REST API

The server runs on `http://127.0.0.1:5000`. Authentication uses an httpOnly JWT cookie set on login.

```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/status

POST   /api/expenses
GET    /api/expenses?status=pending|approved|denied
GET    /api/expenses/<id>
PUT    /api/expenses/<id>
DELETE /api/expenses/<id>

GET    /api/health
```

## Logs

The server writes to `employee_expense.log` (rotating, 5 MB max). Set `LOG_LEVEL=DEBUG` to see per-query detail.
