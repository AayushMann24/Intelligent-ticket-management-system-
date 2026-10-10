"""Conversation API Router.

Provides CRUD operations for user conversations and message management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.dependencies.auth import verify_token
from app.dependencies.csrf import csrf_protect
from app.dependencies.rate_limit import rate_limit_dependency
from app.services.conversation import (
    create_conversation,
    get_conversations,
    get_conversation,
    update_conversation,
    delete_conversation,
    add_message,
    get_messages,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationTitleUpdate,
)


router = APIRouter(
    prefix="/assistant/conversations",
    tags=["Assistant Conversations"],
)


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    code: str | None = None
    retryable: bool = False


class ConversationTitleUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="New conversation title")


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Conversation created"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    dependencies=[Depends(csrf_protect), Depends(rate_limit_dependency)],
)
async def create_conversation_endpoint(
    request: Request,
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> ConversationResponse:
    """
    Create a new conversation.

    Requires authentication. The conversation is owned by the authenticated user.
    """
    new_conversation = await create_conversation(
        db=db,
        title=conversation.title,
        owner_id=user["id"],
    )

    return ConversationResponse(
        id=new_conversation.id,
        title=new_conversation.title,
        owner_id=new_conversation.owner_id,
        archived=new_conversation.archived,
        created_at=new_conversation.created_at,
        updated_at=new_conversation.updated_at,
    )


@router.get(
    "",
    response_model=list[ConversationResponse],
    responses={
        200: {"description": "List of conversations"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    dependencies=[Depends(rate_limit_dependency)],
)
async def list_conversations(
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> list[ConversationResponse]:
    """
    List all conversations for the authenticated user.

    Requires authentication. Only shows conversations owned by the user.
    """
    conversations = await get_conversations(db=db, owner_id=user["id"])

    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title,
            owner_id=conv.owner_id,
            archived=conv.archived,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
        for conv in conversations
    ]


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    responses={
        200: {"description": "Conversation details"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    dependencies=[Depends(rate_limit_dependency)],
)
async def get_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> ConversationResponse:
    """
    Get a specific conversation by ID.

    Requires authentication. Enforces ownership - user can only access their own conversations.
    """
    conversation = await get_conversation(
        db=db,
        conversation_id=conversation_id,
        owner_id=user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        owner_id=conversation.owner_id,
        archived=conversation.archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    responses={
        200: {"description": "Conversation updated"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    dependencies=[Depends(csrf_protect), Depends(rate_limit_dependency)],
)
async def update_conversation_endpoint(
    conversation_id: int,
    title_update: ConversationTitleUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> ConversationResponse:
    """
    Update a conversation title.

    Requires authentication. Enforces ownership - only the conversation owner can rename it.
    """
    conversation = await update_conversation(
        db=db,
        conversation_id=conversation_id,
        new_title=title_update.title,
        owner_id=user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        owner_id=conversation.owner_id,
        archived=conversation.archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Conversation deleted"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    dependencies=[Depends(csrf_protect), Depends(rate_limit_dependency)],
)
async def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> None:
    """
    Delete (archive) a conversation.

    Requires authentication. Enforces ownership - only the conversation owner can archive it.
    """
    success = await delete_conversation(
        db=db,
        conversation_id=conversation_id,
        owner_id=user["id"],
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Message added"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    dependencies=[Depends(csrf_protect), Depends(rate_limit_dependency)],
)
async def add_message_endpoint(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> MessageResponse:
    """
    Add a message to a conversation.

    Requires authentication. Enforces ownership - only messages in the user's conversations can be added.
    """
    # First verify the conversation belongs to the user
    conversation = await get_conversation(
        db=db,
        conversation_id=conversation_id,
        owner_id=user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    new_message = await add_message(
        db=db,
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
    )

    return MessageResponse(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        role=new_message.role,
        content=new_message.content,
        created_at=new_message.created_at,
        citation_metadata=new_message.citation_metadata,
    )


@router.get(
    "/{conversation_id}/messages",
    responses={
        200: {"description": "List of messages"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
    dependencies=[Depends(rate_limit_dependency)],
)
async def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> list[MessageResponse]:
    """
    List all messages in a conversation.

    Requires authentication. Enforces ownership - only the conversation owner can view messages.
    """
    # First verify the conversation belongs to the user
    conversation = await get_conversation(
        db=db,
        conversation_id=conversation_id,
        owner_id=user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await get_messages(db=db, conversation_id=conversation_id)

    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            citation_metadata=msg.citation_metadata,
        )
        for msg in messages
    ]