from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.ticket_comment import (
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentResponse,
    TicketCommentListResponse,
)
from app.services.ticket_comment_service import (
    create_comment,
    get_comments,
    get_comment_by_id,
    update_comment,
    delete_comment,
)
from app.dependencies.roles import (
    require_admin,
    require_authenticated_user,
    require_technician,
    require_admin_or_technician,
)
from app.dependencies.csrf import csrf_protect

router = APIRouter(
    tags=["Ticket Comments"],
)


@router.post(
    "/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
def create_ticket_comment(
    ticket_id: int,
    comment: TicketCommentCreate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return create_comment(
        db=db,
        ticket_id=ticket_id,
        comment_data=comment,
        user_id=user["id"],
        user_role=user["role"],
    )


@router.get(
    "/{ticket_id}/comments",
    response_model=TicketCommentListResponse,
)
def list_ticket_comments(
    ticket_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    include_internal: bool = Query(False, description="Include internal notes"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_comments(
        db=db,
        ticket_id=ticket_id,
        user_id=user["id"],
        user_role=user["role"],
        page=page,
        page_size=page_size,
        include_internal=include_internal,
    )


@router.get(
    "/{ticket_id}/comments/{comment_id}",
    response_model=TicketCommentResponse,
)
def get_ticket_comment(
    ticket_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_comment_by_id(
        db=db,
        comment_id=comment_id,
        user_id=user["id"],
        user_role=user["role"],
    )


@router.put(
    "/{ticket_id}/comments/{comment_id}",
    response_model=TicketCommentResponse,
    dependencies=[Depends(csrf_protect)],
)
def update_ticket_comment(
    ticket_id: int,
    comment_id: int,
    comment: TicketCommentUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return update_comment(
        db=db,
        comment_id=comment_id,
        comment_data=comment,
        user_id=user["id"],
        user_role=user["role"],
    )


@router.delete(
    "/{ticket_id}/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(csrf_protect)],
)
def delete_ticket_comment(
    ticket_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=user["id"],
        user_role=user["role"],
    )