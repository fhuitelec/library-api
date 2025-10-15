"""Domain models for the library API."""

import uuid
from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class Book:
    """Book model."""

    id: uuid.UUID
    issue: int
    isbn: str
    title: str
    author: str


class LoanStatus(StrEnum):
    """Enumeration of loan statuses."""

    REQUESTED = "requested"
    APPROVED = "approved"
    RETURNED = "returned"


@dataclass(frozen=True)
class Loan:
    """Loan model."""

    id: uuid.UUID
    book_id: uuid.UUID
    user_id: str
    status: LoanStatus

    @staticmethod
    def request(book_id: uuid.UUID, user_id: str) -> "Loan":
        """Approve the loan."""
        return Loan(
            id=uuid.uuid4(),
            book_id=book_id,
            user_id=user_id,
            status=LoanStatus.REQUESTED,
        )

    def approve(self) -> "Loan":
        """Approve the loan."""
        return Loan(
            id=self.id,
            book_id=self.book_id,
            user_id=self.user_id,
            status=LoanStatus.APPROVED,
        )

    def return_loan(self) -> "Loan":
        """Return the loan."""
        return Loan(
            id=self.id,
            book_id=self.book_id,
            user_id=self.user_id,
            status=LoanStatus.RETURNED,
        )
