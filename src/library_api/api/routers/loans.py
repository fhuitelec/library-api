"""Router for loan-related operations."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import Field, BaseModel

from library_api.api.repositories import fake_loan_repository, BOOK_IDS
from library_api.api.security import JWT, Permission
from library_api.api.security.authentication import authentication
from library_api.api.security.authorization import require_permissions
from library_api.domain.models import Loan

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
)


class LoanRequest(BaseModel):
    """Request model for a book loan."""

    book_id: uuid.UUID = Field(examples=BOOK_IDS)


class LoanApprove(BaseModel):
    """Request model for approving a book loan."""

    loan_id: uuid.UUID


@router.post("/", dependencies=[require_permissions(required={Permission.LOAN_REQUEST})])
async def request_a_loan(loan: LoanRequest, jwt: Annotated[JWT, Depends(authentication)]) -> Loan:
    """Request a new loan for a book."""
    return fake_loan_repository.request(book_id=loan.book_id, user_id=jwt.subject)


@router.post("/approve", dependencies=[require_permissions(required={Permission.LOAN_APPROVE})])
async def approve_a_loan(loan: LoanApprove) -> Loan:
    """Approve a previously requested loan for a book."""
    return fake_loan_repository.approve(loan.loan_id)


@router.get("/all", dependencies=[require_permissions(required={Permission.LOAN_READ_ALL})])
async def list_all_loans() -> list[Loan]:
    """List all book loans."""
    return fake_loan_repository.list_all()
