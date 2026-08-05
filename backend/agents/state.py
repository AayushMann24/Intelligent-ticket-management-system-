from typing import Annotated, TypedDict, Optional

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # ============================
    # LangGraph Messages
    # ============================
    messages: Annotated[list, add_messages]

    # Next node selected by Supervisor
    next: str

    # ============================
    # Original Ticket
    # ============================
    title: str
    description: str

    # ============================
    # Ticket Analysis Agent Output
    # ============================
    category: Optional[str]
    subcategory: Optional[str]
    keywords: list[str]
    confidence: Optional[float]

    # ============================
    # Priority Agent Output
    # ============================
    priority: Optional[str]
    priority_reason: Optional[str]

    # ============================
    # Assignment Agent Output
    # ============================
    assigned_to: Optional[int]
    assigned_name: Optional[str]
    assignment_reason: Optional[str]

    # ============================
    # Analytics Agent Output
    # ============================
    analytics: Optional[dict]

    # ============================
    # Final Supervisor Response
    # ============================
    final_response: Optional[dict]