import atexit
import logging
import os
import subprocess
import sys
import time
from typing import Optional

from repository.user_model import User
from api_client import ApiClient, ApiClientError
from cli import EmployeeCliView

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000')
SERVER_START_TIMEOUT_SECONDS = 10


class EmployeeAppController:
    """Main controller for the CLI app. Starts the API server if needed,
    then drives the login and menu flow."""

    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.api_client = ApiClient(API_BASE_URL)
        self._ensure_server_running()
        self.current_user: Optional[User] = None

    def _ensure_server_running(self):
        """Checks if the API server is up. If not, starts it as a background
        process and waits up to SERVER_START_TIMEOUT_SECONDS for it to respond."""
        if self.api_client.health_check():
            return

        EmployeeCliView.print_info("Starting Employee Expense Manager API server...")

        server_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'api_server.py'
        )
        self.server_process = subprocess.Popen(
            [sys.executable, server_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        atexit.register(self._stop_server)

        deadline = time.time() + SERVER_START_TIMEOUT_SECONDS
        while time.time() < deadline:
            if self.api_client.health_check():
                return
            if self.server_process.poll() is not None:
                raise RuntimeError(
                    "API server process exited unexpectedly while starting up."
                )
            time.sleep(0.3)

        raise RuntimeError(
            f"Could not reach the API server at {API_BASE_URL} after "
            f"{SERVER_START_TIMEOUT_SECONDS}s."
        )

    def _stop_server(self):
        """Shuts down the server process on exit, but only if this process
        was the one that started it."""
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()

    def run(self):
        """Entry point — starts the login loop and handles top-level exits."""
        try:
            self._login_loop()
        except KeyboardInterrupt:
            EmployeeCliView.print_info("\nApplication interrupted by user.")
            sys.exit(0)
        except Exception as e:
            logger.exception("Unexpected error in application run")
            EmployeeCliView.print_error(f"Unexpected error: {str(e)}")
            sys.exit(1)

    def _login_loop(self):
        """Keeps prompting for credentials until the user logs in successfully
        or exits via Ctrl+C."""
        while True:
            try:
                username, password = EmployeeCliView.login_prompt()

                if not username or not password:
                    EmployeeCliView.print_error("Username and password cannot be empty.")
                    EmployeeCliView.input_pause()
                    continue

                user = self.api_client.login(username, password)
                if user:
                    self.current_user = user
                    EmployeeCliView.print_success("Login successful!")
                    EmployeeCliView.show_welcome(username)
                    EmployeeCliView.input_pause()
                    self._main_menu_loop()
                    self.current_user = None
                else:
                    EmployeeCliView.print_error("Invalid username or password. Please try again.")
                    EmployeeCliView.input_pause()
            except KeyboardInterrupt:
                raise
            except ApiClientError as e:
                EmployeeCliView.print_error(f"Login error: {str(e)}")
                EmployeeCliView.input_pause()
            except Exception as e:
                logger.exception("Unexpected error during login")
                EmployeeCliView.print_error(f"Login error: {str(e)}")
                EmployeeCliView.input_pause()

    def _main_menu_loop(self):
        """Runs the main menu for the duration of the user's session.
        Exits when the user logs out or quits."""
        while self.current_user:
            try:
                choice = EmployeeCliView.show_main_menu()

                if choice == 1:
                    self._submit_expense()
                elif choice == 2:
                    self._view_expenses()
                elif choice == 3:
                    self._view_history()
                elif choice == 4:
                    self._edit_expense()
                elif choice == 5:
                    self._delete_expense()
                elif choice == 6:
                    self.api_client.logout()
                    break
                elif choice == 7:
                    self.api_client.logout()
                    EmployeeCliView.show_goodbye()
                    sys.exit(0)
                else:
                    EmployeeCliView.print_error("Invalid option. Please select 1-7.")
                    EmployeeCliView.input_pause()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.exception("Unexpected error in main menu")
                EmployeeCliView.print_error(f"Error: {str(e)}")
                EmployeeCliView.input_pause()

    def _submit_expense(self):
        """Prompts for expense details and sends them to the API."""
        try:
            amount, description, date = EmployeeCliView.get_expense_input()
            expense = self.api_client.submit_expense(amount, description, date)
            EmployeeCliView.print_success(f"Expense submitted successfully! (ID: {expense.id})")
            EmployeeCliView.input_pause()
        except (ValueError, ApiClientError) as e:
            EmployeeCliView.print_error(str(e))
            EmployeeCliView.input_pause()
        except Exception as e:
            logger.exception("Unexpected error submitting expense")
            EmployeeCliView.print_error(f"Failed to submit expense: {str(e)}")
            EmployeeCliView.input_pause()

    def _view_expenses(self):
        """Fetches and displays all of the user's expenses with a summary at the bottom."""
        try:
            expenses_with_status = self.api_client.get_expenses()

            if expenses_with_status:
                EmployeeCliView.show_expenses(expenses_with_status)

                total = sum(e.amount for e, _ in expenses_with_status)
                pending = sum(1 for _, a in expenses_with_status if a.status == 'pending')
                approved = sum(1 for _, a in expenses_with_status if a.status == 'approved')
                denied = sum(1 for _, a in expenses_with_status if a.status == 'denied')

                print()
                EmployeeCliView.show_expense_summary(total, pending, approved, denied)
            else:
                EmployeeCliView.print_info("You have not submitted any expenses yet.")

            EmployeeCliView.input_pause()
        except ApiClientError as e:
            EmployeeCliView.print_error(str(e))
            EmployeeCliView.input_pause()
        except Exception as e:
            logger.exception("Unexpected error retrieving expenses")
            EmployeeCliView.print_error(f"Failed to retrieve expenses: {str(e)}")
            EmployeeCliView.input_pause()

    def _view_history(self):
        """Lets the user filter expenses by status and displays the results."""
        try:
            status_filter = EmployeeCliView.get_history_filter()
            expenses_with_status = self.api_client.get_expenses(status_filter)

            filter_title = {
                None: "All Expenses",
                'pending': "Pending Expenses",
                'approved': "Approved Expenses",
                'denied': "Denied Expenses"
            }.get(status_filter, "Expense History")

            if expenses_with_status:
                EmployeeCliView.show_expenses(expenses_with_status, title=filter_title)
            else:
                EmployeeCliView.print_info(f"No {filter_title.lower()} found.")

            EmployeeCliView.input_pause()
        except ApiClientError as e:
            EmployeeCliView.print_error(str(e))
            EmployeeCliView.input_pause()
        except Exception as e:
            logger.exception("Unexpected error retrieving history")
            EmployeeCliView.print_error(f"Failed to retrieve history: {str(e)}")
            EmployeeCliView.input_pause()

    def _edit_expense(self):
        """Shows pending expenses, asks the user which one to edit,
        then sends the updated values to the API."""
        try:
            expenses_with_status = self.api_client.get_expenses()
            pending_expenses = [(e, a) for e, a in expenses_with_status if a.status == 'pending']

            if not pending_expenses:
                EmployeeCliView.print_info("You have no pending expenses to edit.")
                EmployeeCliView.input_pause()
                return

            EmployeeCliView.show_expenses(pending_expenses, title="Pending Expenses")
            expense_id = EmployeeCliView.get_expense_id()

            selected_expense = next(
                ((e, a) for e, a in pending_expenses if e.id == expense_id), None
            )

            if not selected_expense:
                EmployeeCliView.print_error("Expense not found or is not pending.")
                EmployeeCliView.input_pause()
                return

            expense, approval = selected_expense
            EmployeeCliView.show_expense_details(expense, approval)

            confirm = input("\nDo you want to edit this expense? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                EmployeeCliView.input_pause()
                return

            amount, description, date = EmployeeCliView.get_edit_input(expense)
            self.api_client.update_expense(expense_id, amount, description, date)
            EmployeeCliView.print_success("Expense updated successfully!")
            EmployeeCliView.input_pause()
        except (ValueError, ApiClientError) as e:
            EmployeeCliView.print_error(str(e))
            EmployeeCliView.input_pause()
        except Exception as e:
            logger.exception("Unexpected error editing expense")
            EmployeeCliView.print_error(f"Failed to update expense: {str(e)}")
            EmployeeCliView.input_pause()

    def _delete_expense(self):
        """Shows pending expenses, asks the user which one to delete,
        confirms, then sends the delete request to the API."""
        try:
            expenses_with_status = self.api_client.get_expenses()
            pending_expenses = [(e, a) for e, a in expenses_with_status if a.status == 'pending']

            if not pending_expenses:
                EmployeeCliView.print_info("You have no pending expenses to delete.")
                EmployeeCliView.input_pause()
                return

            EmployeeCliView.show_expenses(pending_expenses, title="Pending Expenses")
            expense_id = EmployeeCliView.get_expense_id()

            selected_expense = next(
                ((e, a) for e, a in pending_expenses if e.id == expense_id), None
            )

            if not selected_expense:
                EmployeeCliView.print_error("Expense not found or is not pending.")
                EmployeeCliView.input_pause()
                return

            expense, approval = selected_expense
            EmployeeCliView.show_expense_details(expense, approval)

            if not EmployeeCliView.confirm_delete():
                EmployeeCliView.input_pause()
                return

            self.api_client.delete_expense(expense_id)
            EmployeeCliView.print_success("Expense deleted successfully!")
            EmployeeCliView.input_pause()
        except (ValueError, ApiClientError) as e:
            EmployeeCliView.print_error(str(e))
            EmployeeCliView.input_pause()
        except Exception as e:
            logger.exception("Unexpected error deleting expense")
            EmployeeCliView.print_error(f"Failed to delete expense: {str(e)}")
            EmployeeCliView.input_pause()


def main():
    app = EmployeeAppController()
    app.run()


if __name__ == '__main__':
    main()
