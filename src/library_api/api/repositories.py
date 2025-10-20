"""Fake in-memory repositories for testing purposes."""

import uuid
from http import HTTPStatus
from typing import List, Optional, Dict

from fastapi import HTTPException

from library_api.domain.models import Book, Loan, LoanStatus
from library_api.domain.repositories import BookRepository, LoanRepository


class InMemoryBookRepository(BookRepository):
    """In-memory implementation of the BookRepository."""

    def __init__(self) -> None:
        """Initialize the repository with an empty list of books."""
        self._books: List[Book] = []

    def get_by_id(self, book_id: uuid.UUID) -> Optional[Book]:
        """Get a book by its ID."""
        for book in self._books:
            if book.id == book_id:
                return book
        return None

    def list(self) -> List[Book]:
        """List all books."""
        return self._books

    def create(self, book: Book) -> Book:
        """Create a new book."""
        self._books.append(book)
        return book


class InMemoryLoanRepository(LoanRepository):
    """In-memory implementation of the LoanRepository."""

    def __init__(self, book_repository: BookRepository) -> None:
        """Initialize the repository with a reference to the book repository."""
        self.book_repository = book_repository
        self._loans: Dict[str, Loan] = {}

    def get_by_id(self, loan_id: uuid.UUID) -> Loan | None:
        """Get a loan by its ID."""
        return self._loans.get(str(loan_id), None)

    def list(self, user_id: str) -> List[Loan]:
        """List all loans, optionally filtered by user ID."""
        if not user_id:
            raise ValueError("A user_id must be provided")

        return [loan for loan in self._loans.values() if loan.user_id == user_id]

    def list_all(self) -> List[Loan]:
        """List all loans."""
        return list(self._loans.values())

    def request(self, book_id: uuid.UUID, user_id: str) -> Loan:
        """Request a new loan."""
        if self.book_repository.get_by_id(book_id) is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Book with given ID does not exist.")

        loaned = [
            loan for loan in self._loans.values() if loan.book_id == book_id and loan.status != LoanStatus.RETURNED
        ]

        if loaned:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Book is already loaned.")

        loan = Loan.request(book_id, user_id)
        self._loans[str(loan.id)] = loan
        return loan

    def approve(self, loan_id: uuid.UUID) -> Loan:
        """Approve a requested loan."""
        if str(loan_id) not in self._loans.keys():
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Loan with given ID does not exist.")

        loan = self._loans.pop(str(loan_id)).approve()
        self._loans[str(loan.id)] = loan
        return loan

    def delete(self, loan_id: uuid.UUID) -> None:
        """Delete a loan by its ID."""
        self._loans.pop(str(loan_id), None)

    def return_(self, loan_id: uuid.UUID) -> Loan:
        """Return a loaned book."""
        loan = self._loans.get(str(loan_id), None)

        if loan is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Loan with given ID does not exist.")

        if loan.status != LoanStatus.APPROVED:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Cannot return a loan that was not approved."
            )

        self._loans[str(loan.id)] = loan.return_loan()
        return loan


BOOK_IDS = [
    uuid.UUID("daa5931c-87e1-4111-bf05-639144dc46f5"),
    uuid.UUID("3f5f7000-c2c0-4d14-888c-c5a5631b5a38"),
    uuid.UUID("e25921b9-e681-4b03-88be-2e411fec5d2b"),
]

fake_book_repository = InMemoryBookRepository()
fake_loan_repository = InMemoryLoanRepository(fake_book_repository)

fake_book_repository.create(
    Book(
        id=BOOK_IDS[0],
        issue=1,
        isbn="978-3-16-148410-0",
        title="Book 1",
        author="Author 1",
    )
)
fake_book_repository.create(
    Book(
        id=BOOK_IDS[1],
        issue=2,
        isbn="978-3-16-148410-0",
        title="Book 1",
        author="Author 1",
    )
)
fake_book_repository.create(
    Book(
        id=BOOK_IDS[2],
        issue=1,
        isbn="978-4-25-652123-0",
        title="Book 2",
        author="Author 2",
    )
)
