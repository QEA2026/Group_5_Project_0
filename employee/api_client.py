from typing import Optional

import requests
from requests.exceptions import RequestException

from repository.approval_model import Approval
from repository.expense_model import Expense
from repository.user_model import User


def _error_message(response: requests.Response, default: str) -> str:
    try:
        return response.json().get('error', default)
    except ValueError:
        return default


class ApiClientError(Exception):
    """Raised for connection problems or unexpected API errors."""


class ApiClientNotFoundError(ApiClientError):
    """Raised when the API returns 404 for a resource."""


class ApiClient:
    """HTTP client the CLI uses to talk to the Flask API."""

    def __init__(self, base_url: str = 'http://127.0.0.1:5000'):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.current_user: Optional[User] = None

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health_check(self, timeout: float = 1.0) -> bool:
        """Returns True if the API server is reachable."""
        try:
            response = self.session.get(self._url('/api/health'), timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # --- Auth ---

    def login(self, username: str, password: str) -> Optional[User]:
        """Returns the User on successful login, None on bad credentials."""
        try:
            response = self.session.post(
                self._url('/api/auth/login'),
                json={'username': username, 'password': password},
                timeout=5,
            )
        except RequestException as e:
            raise ApiClientError(f"Could not reach the API server ({e})") from e

        if response.status_code == 401:
            return None  # bad credentials — not an error, just a failed attempt
        if response.status_code != 200:
            raise ApiClientError(_error_message(response, 'Login failed'))

        user_data = response.json()['user']
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            password='',
            role=user_data['role'],
        )
        self.current_user = user
        return user

    def logout(self):
        """Clears the session cookie and forgets the current user."""
        try:
            self.session.post(self._url('/api/auth/logout'), timeout=5)
        except requests.exceptions.RequestException:
            pass
        self.session.cookies.clear()
        self.current_user = None

    # --- Expenses ---

    def submit_expense(self, amount: float, description: str, date: str = None) -> Expense:
        payload = {'amount': amount, 'description': description}
        if date:
            payload['date'] = date
        data = self._request('POST', '/api/expenses', json=payload)['expense']
        return self._to_expense(data)

    def get_expenses(self, status_filter: Optional[str] = None) -> list[tuple[Expense, Approval]]:
        params = {'status': status_filter} if status_filter else None
        data = self._request('GET', '/api/expenses', params=params)
        return [self._to_expense_approval(item) for item in data['expenses']]

    def update_expense(
        self, expense_id: int, amount: float, description: str, date: str
    ) -> Optional[Expense]:
        try:
            data = self._request(
                'PUT', f'/api/expenses/{expense_id}',
                json={'amount': amount, 'description': description, 'date': date},
            )['expense']
        except ApiClientNotFoundError:
            return None
        return self._to_expense(data)

    def delete_expense(self, expense_id: int) -> bool:
        try:
            self._request('DELETE', f'/api/expenses/{expense_id}')
            return True
        except ApiClientNotFoundError:
            return False

    # --- Internal helpers ---

    def _to_expense(self, data: dict) -> Expense:
        return Expense(
            id=data['id'],
            user_id=data['user_id'],
            amount=data['amount'],
            description=data['description'],
            date=data['date'],
        )

    def _to_expense_approval(self, item: dict) -> tuple[Expense, Approval]:
        expense = self._to_expense(item)
        approval = Approval(
            id=None,
            expense_id=item['id'],
            status=item['status'],
            reviewer=None,
            comment=item.get('comment'),
            review_date=item.get('review_date'),
        )
        return expense, approval

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = self.session.request(method, self._url(path), timeout=5, **kwargs)
        except RequestException as e:
            raise ApiClientError(f"Could not reach the API server ({e})") from e

        if response.status_code == 404:
            raise ApiClientNotFoundError(_error_message(response, 'Not found'))
        if response.status_code == 400:
            raise ValueError(_error_message(response, 'Bad request'))
        if response.status_code == 401:
            raise ApiClientError('Not authenticated')
        if not response.ok:
            raise ApiClientError(
                _error_message(response, f'Request failed ({response.status_code})')
            )

        return response.json()
