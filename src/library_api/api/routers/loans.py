"""Router for loan-related operations."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from library_api.api.repositories import fake_loan_repository
from library_api.api.security import JWT, Permission
from library_api.api.security.authentication import authentication
from library_api.api.security.authorization import require_permissions
from library_api.domain.models import Loan

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
)


@router.post("/")
async def request_loan(book_id: uuid.UUID, jwt: Annotated[JWT, Depends(authentication)]) -> Loan:
    """Request a new loan for a book."""
    return fake_loan_repository.request(book_id=book_id, user_id=jwt.subjet)


@router.post("/approve", dependencies=[require_permissions(required={Permission.LOAN_APPROVE})])
async def approve_loan(loan_id: uuid.UUID) -> Loan:
    """Request a new loan for a book."""
    return fake_loan_repository.approve(loan_id)


# Todo: add a new loan:read_all permission
@router.get("/all", dependencies=[require_permissions(required={Permission.LOAN_APPROVE})])
async def list_all_loans(jwt: Annotated[JWT, Depends(authentication)]) -> list[Loan]:
    """Request a new loan for a book."""
    return fake_loan_repository.list_all()
