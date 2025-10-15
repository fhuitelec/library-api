"""Domain repositories for the library API."""

import uuid
from abc import ABC, abstractmethod
from typing import List

from library_api.domain.models import Book, Loan


class BookRepository(ABC):
    """Abstract base class for book repository."""

    @abstractmethod
    def get_by_id(self, book_id: uuid.UUID) -> Book | None:
        """Get a book by its ID."""
        ...

    @abstractmethod
    def list(self) -> List[Book]:
        """List all books."""
        ...

    @abstractmethod
    def create(self, book: Book) -> Book:
        """Create a new book."""
        ...


class LoanRepository(ABC):
    """Abstract base class for loan repository."""

    @abstractmethod
    def get_by_id(self, loan_id: uuid.UUID) -> Loan | None:
        """Get a loan by its ID."""
        ...

    @abstractmethod
    def list(self, user_id: str) -> List[Loan]:
        """List all loans, optionally filtered by user ID."""
        ...

    @abstractmethod
    def request(self, book_id: uuid.UUID, user_id: str) -> Loan:
        """Request a new loan."""
        ...

    @abstractmethod
    def approve(self, loan_id: uuid.UUID) -> Loan:
        """Approve a requested loan."""
        ...

    @abstractmethod
    def delete(self, loan_id: uuid.UUID) -> None:
        """Delete a loan by its ID."""
        ...

    @abstractmethod
    def return_(self, loan_id: uuid.UUID) -> Loan:
        """Return a loaned book."""
        ...
