"""
Logging setup. Call configure_logging() once at startup; every other module
gets its logger with logging.getLogger(__name__).
"""
import logging
import logging.handlers
import os
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "employee_expense.log")

_FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    if root.handlers:
        return

    formatter = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(LOG_LEVEL)
    console.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file_handler)

    # Flask's request logger is noisy; keep it at WARNING
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
