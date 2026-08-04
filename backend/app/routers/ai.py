from fastapi import APIRouter

from langchain_core.messages import HumanMessage

from agents.graph import graph

from app.schemas.ai import (
    AIRequest,
    AIResponse,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"],
)


@router.post(
    "/chat",
    response_model=AIResponse,
)
def chat(request: AIRequest):

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=request.message
                )
            ]
        }
    )

    return AIResponse(
        response=result["messages"][-1].content
    )