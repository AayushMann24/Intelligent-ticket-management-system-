from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.database.connection import get_db
from app.schemas.ticket_comment import (
    TicketAttachmentResponse,
    TicketAttachmentListResponse,
)
from app.services.ticket_attachment_service import (
    upload_attachment,
    get_attachments,
    get_attachment_by_id,
    download_attachment,
    delete_attachment,
)
from app.dependencies.roles import (
    require_authenticated_user,
)
from app.dependencies.csrf import csrf_protect

router = APIRouter(
    tags=["Ticket Attachments"],
)


@router.post(
    "/{ticket_id}/attachments",
    response_model=TicketAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
async def upload_ticket_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return upload_attachment(
        db=db,
        ticket_id=ticket_id,
        file=file,
        user_id=user["id"],
        user_role=user["role"],
    )


@router.get(
    "/{ticket_id}/attachments",
    response_model=TicketAttachmentListResponse,
)
def list_ticket_attachments(
    ticket_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_attachments(
        db=db,
        ticket_id=ticket_id,
        user_id=user["id"],
        user_role=user["role"],
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{ticket_id}/attachments/{attachment_id}",
    response_model=TicketAttachmentResponse,
)
def get_ticket_attachment(
    ticket_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_attachment_by_id(
        db=db,
        attachment_id=attachment_id,
        user_id=user["id"],
        user_role=user["role"],
    )


@router.get(
    "/{ticket_id}/attachments/{attachment_id}/download",
    response_class=FileResponse,
)
def download_ticket_attachment(
    ticket_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return download_attachment(
        db=db,
        attachment_id=attachment_id,
        user_id=user["id"],
        user_role=user["role"],
    )


@router.delete(
    "/{ticket_id}/attachments/{attachment_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(csrf_protect)],
)
def delete_ticket_attachment(
    ticket_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return delete_attachment(
        db=db,
        attachment_id=attachment_id,
        user_id=user["id"],
        user_role=user["role"],
    )