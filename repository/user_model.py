from typing import Optional


class User:
    def __init__(self, id: Optional[int], username: str, password: str, role: str):
        if role != 'Employee':
            raise ValueError("Role must be 'Employee'")
        self.id = id
        self.username = username
        self.password = password
        self.role = role
