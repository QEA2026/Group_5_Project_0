from typing import Optional
from repository.expense_model import Expense
from repository.approval_model import Approval


class EmployeeCliView:

    @staticmethod
    def clear_screen():
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_header(title: str):
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)

    @staticmethod
    def print_success(message: str):
        print(f"{message}")

    @staticmethod
    def print_error(message: str):
        print(f"{message}")

    @staticmethod
    def print_info(message: str):
        print(f"{message}")

    @staticmethod
    def print_warning(message: str):
        print(f"{message}")

    @staticmethod
    def login_prompt() -> tuple[str, str]:
        EmployeeCliView.print_header("Employee Login")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        return username, password

    @staticmethod
    def show_main_menu() -> int:
        EmployeeCliView.print_header("Main Menu")
        print("1. Submit New Expense")
        print("2. View My Expenses")
        print("3. View Expense History")
        print("4. Edit Pending Expense")
        print("5. Delete Pending Expense")
        print("6. Logout")
        print("7. Exit Application")
        print()

        try:
            choice = int(input("Select option (1-7): ").strip())
            return choice
        except ValueError:
            return -1

    @staticmethod
    def get_expense_input() -> tuple[float, str, str]:
        EmployeeCliView.print_header("Submit New Expense")

        try:
            amount = float(input("Amount ($): ").strip())
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")

            description = input("Description: ").strip()
            if not description:
                raise ValueError("Description is required")

            date_input = input("Date (YYYY-MM-DD, or press Enter for today): ").strip()
            if not date_input:
                from datetime import datetime
                date_input = datetime.now().strftime('%Y-%m-%d')

            return amount, description, date_input
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    def show_expenses(expenses_with_status: list[tuple[Expense, Approval]],
                     title: str = "My Expenses"):
        EmployeeCliView.print_header(title)

        if not expenses_with_status:
            print("No expenses found.")
            return

        print(f"{'ID':<5} {'Date':<12} {'Amount':<10} {'Status':<12} {'Description':<30}")
        print("-" * 80)

        for expense, approval in expenses_with_status:
            status_display = approval.status.upper()
            print(f"{expense.id:<5} {expense.date:<12} ${expense.amount:<9.2f} "
                  f"{status_display:<12} {expense.description[:30]:<30}")

            if approval.comment:
                print(f"         Comment: {approval.comment}")

    @staticmethod
    def show_expense_details(expense: Expense, approval: Approval):
        EmployeeCliView.print_header(f"Expense Details (ID: {expense.id})")
        print(f"Amount:      ${expense.amount:.2f}")
        print(f"Description: {expense.description}")
        print(f"Date:        {expense.date}")
        print(f"Status:      {approval.status.upper()}")
        if approval.comment:
            print(f"Reviewer Comment: {approval.comment}")
        if approval.review_date:
            print(f"Review Date: {approval.review_date}")

    @staticmethod
    def get_expense_id() -> int:
        try:
            return int(input("Enter expense ID: ").strip())
        except ValueError:
            return -1

    @staticmethod
    def get_edit_input(current_expense: Expense) -> tuple[float, str, str]:
        EmployeeCliView.print_header("Edit Expense")
        print(f"Current Amount: ${current_expense.amount:.2f}")
        print(f"Current Description: {current_expense.description}")
        print(f"Current Date: {current_expense.date}\n")

        try:
            amount_input = input(f"New Amount (press Enter to keep ${current_expense.amount:.2f}): ").strip()
            amount = float(amount_input) if amount_input else current_expense.amount
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")

            description = input("New Description (press Enter to keep current): ").strip()
            if not description:
                description = current_expense.description

            date_input = input(f"New Date (press Enter to keep {current_expense.date}): ").strip()
            if not date_input:
                date_input = current_expense.date

            return amount, description, date_input
        except ValueError as e:
            raise ValueError(str(e))

    @staticmethod
    def confirm_delete() -> bool:
        response = input("Are you sure you want to delete this expense? (yes/no): ").strip().lower()
        return response in ['yes', 'y']

    @staticmethod
    def show_welcome(username: str):
        EmployeeCliView.print_header(f"Welcome, {username}!")
        EmployeeCliView.print_info("You are logged in as an Employee")

    @staticmethod
    def show_goodbye():
        EmployeeCliView.print_info("Thank you for using Employee Expense Manager. Goodbye!")

    @staticmethod
    def get_history_filter() -> Optional[str]:
        EmployeeCliView.print_header("View Expense History")
        print("1. All expenses")
        print("2. Pending expenses")
        print("3. Approved expenses")
        print("4. Denied expenses")
        print()

        try:
            choice = int(input("Select filter (1-4): ").strip())
            filter_map = {1: None, 2: 'pending', 3: 'approved', 4: 'denied'}
            return filter_map.get(choice)
        except ValueError:
            return None

    @staticmethod
    def show_expense_summary(total: float, pending: int, approved: int, denied: int):
        EmployeeCliView.print_header("Expense Summary")
        print(f"Total Expenses: ${total:.2f}")
        print(f"Pending:  {pending}")
        print(f"Approved: {approved}")
        print(f"Denied:   {denied}")

    @staticmethod
    def input_pause():
        input("\nPress Enter to continue...")
