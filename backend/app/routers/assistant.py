from fastapi import APIRouter

from app.schemas.assistant import (
    AssistantRequest,
    AssistantResponse,
)

from app.services.assistant_service import AssistantService

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"],
)


@router.post(
    "/chat",
    response_model=AssistantResponse,
)
def chat(request: AssistantRequest):

    answer = AssistantService.chat(
        request.message
    )

    return AssistantResponse(
        response=answer
    )