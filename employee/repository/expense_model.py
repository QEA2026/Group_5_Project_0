from typing import Optional


class Expense:
    def __init__(self, id: Optional[int], user_id: int, amount: float,
                 description: str, date: str):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.description = description
        self.date = date
