from typing import Optional


class Approval:
    def __init__(self, id: Optional[int], expense_id: int, status: str,
                 reviewer: Optional[int], comment: Optional[str],
                 review_date: Optional[str]):
        if status not in ('pending', 'approved', 'denied'):
            raise ValueError("Status must be 'pending', 'approved', or 'denied'")
        self.id = id
        self.expense_id = expense_id
        self.status = status
        self.reviewer = reviewer
        self.comment = comment
        self.review_date = review_date
