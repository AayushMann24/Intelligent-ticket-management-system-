from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for all AI agents.

    Every agent reads from this state,
    updates only its own fields,
    and passes it to the next agent.
    """

    # ==========================================
    # Conversation
    # ==========================================

    messages: Annotated[list, add_messages]

    # ==========================================
    # Supervisor Routing
    # ==========================================

    workflow: str

    # ==========================================
    # Original Ticket
    # ==========================================

    title: str
    description: str

    # ==========================================
    # Ticket Analysis Output
    # ==========================================

    category: Optional[str]
    subcategory: Optional[str]

    keywords: list[str]

    confidence: Optional[float]

    # ==========================================
    # Priority Output
    # ==========================================

    priority: Optional[str]

    priority_reason: Optional[str]

    # ==========================================
    # Assignment Input
    # ==========================================

    technicians: list[dict]

    # ==========================================
    # Assignment Output
    # ==========================================

    assigned_to: Optional[int]

    assigned_name: Optional[str]

    assignment_reason: Optional[str]

    # ==========================================
    # Analytics
    # ==========================================

    dashboard_stats: Optional[dict]

    analytics: Optional[dict]

    # ==========================================
    # Final Output
    # ==========================================

    final_response: Optional[dict]