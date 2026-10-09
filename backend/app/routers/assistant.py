"""AI Assistant API Router.

Provides grounded AI assistant endpoint for IT support questions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.dependencies.auth import verify_token
from app.dependencies.csrf import csrf_protect
from app.dependencies.rate_limit import rate_limit_dependency
from app.services.itms_assistant import (
    ask_assistant,
    AssistantResponse,
    InsufficientEvidenceError,
)
from app.services.ai_gateway import AIGatewayError
from app.config import settings

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"],
)


class AskRequest(BaseModel):
    """Request to ask the AI Assistant a question."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="IT support question",
    )
    provider: str | None = Field(
        default=None,
        description="Optional provider override (gemini or ollama)",
        pattern="^(gemini|ollama)$",
    )


class AskResponse(BaseModel):
    """Response from the AI Assistant."""
    answer: str
    citations: list[dict]
    evidence_found: bool
    grounded: bool
    provider: str
    model: str
    usage: dict | None = None
    metadata: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    code: str | None = None
    retryable: bool = False


@router.post(
    "/ask",
    response_model=AskResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "AI provider unavailable"},
    },
    dependencies=[Depends(csrf_protect), Depends(rate_limit_dependency)],
)
async def ask_assistant_endpoint(
    request: Request,
    ask_request: AskRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
) -> AskResponse:
    """
    Ask the ITMS AI Assistant a question.
    
    The assistant uses Knowledge Base evidence to ground its answers.
    Returns citations for all evidence used.
    
    Requires authentication. Available to all authenticated users (Employee, Technician, Admin).
    """
    # Validate provider override if provided
    provider_override = ask_request.provider
    if provider_override and provider_override not in ["gemini", "ollama"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider. Must be 'gemini' or 'ollama'.",
        )
    
    # Check if provider is available
    if provider_override == "gemini" and not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini provider not configured (missing API key)",
        )
    
    question = ask_request.question.strip()
    
    try:
        response = await ask_assistant(
            db=db,
            question=question,
            user_role=user["role"],
            provider_override=provider_override,
        )
        
        return AskResponse(
            answer=response.answer,
            citations=response.citations,
            evidence_found=response.evidence_found,
            grounded=response.grounded,
            provider=response.provider,
            model=response.model,
            usage=response.usage,
            metadata=response.metadata,
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    except InsufficientEvidenceError as e:
        # This shouldn't happen as we handle it in the service, but just in case
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=str(e),
        )
    
    except AIGatewayError as e:
        # Map provider errors to appropriate HTTP status codes
        if e.retryable:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Don't expose internal error details
        if e.code in ["OLLAMA_CONNECTION_TIMEOUT", "OLLAMA_INIT_FAILED", "GEMINI_API_KEY_MISSING"]:
            detail = "AI service temporarily unavailable. Please try again later."
        else:
            detail = "An error occurred while generating the answer."
        
        raise HTTPException(
            status_code=http_status,
            detail=detail,
        )
    
    except Exception as e:
        # Log the full error for debugging but don't expose it
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(
            "Unexpected error in assistant endpoint",
            extra={
                "error_type": type(e).__name__,
                "question_length": len(question),
                "user_id": user["id"],
            },
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.get(
    "/health",
    response_model=dict,
)
async def assistant_health() -> dict:
    """Health check for the assistant service."""
    return {
        "status": "healthy",
        "service": "assistant",
        "ai_provider": settings.ai_provider,
        "ai_model": settings.ollama_model if settings.ai_provider == "ollama" else settings.gemini_model,
    }