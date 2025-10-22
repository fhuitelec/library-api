"""Router for loan-related operations."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import Field, BaseModel

from library_api.api.repositories import fake_loan_repository, BOOK_IDS
from library_api.api.security import JWT
from library_api.api.security.authentication import authentication
from library_api.domain.models import Loan

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
    dependencies=[Depends(authentication)],
)


class LoanRequest(BaseModel):
    """Request model for a book loan."""

    book_id: uuid.UUID = Field(examples=BOOK_IDS)


class LoanApprove(BaseModel):
    """Request model for approving a book loan."""

    loan_id: uuid.UUID


@router.post("/")
async def request_a_loan(loan: LoanRequest, jwt: Annotated[JWT, Depends(authentication)]) -> Loan:
    """Request a new loan for a book."""
    return fake_loan_repository.request(book_id=loan.book_id, user_id=jwt.subject)


@router.post("/approve")
async def approve_a_loan(loan: LoanApprove) -> Loan:
    """Approve a previously requested loan for a book."""
    return fake_loan_repository.approve(loan.loan_id)


@router.get("/me")
async def list_loans_for_a_user(jwt: Annotated[JWT, Depends(authentication)]) -> list[Loan]:
    """List all book loans."""
    return fake_loan_repository.list(user_id=jwt.subject)


@router.get("/")
async def list_all_loans() -> list[Loan]:
    """List all book loans."""
    return fake_loan_repository.list_all()
