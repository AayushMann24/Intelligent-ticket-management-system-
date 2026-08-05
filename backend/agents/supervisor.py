from agents.ticket_agent import ticket_agent
from agents.priority_agent import priority_agent
from agents.assignment_agent import assignment_agent
from agents.analytics_agent import analytics_agent


def supervisor(state):
    """
    Supervisor Agent

    Coordinates all AI agents and
    produces one final response.
    """

    messages = state.get("messages", [])

    request = ""

    if messages:
        request = messages[-1].content.lower()

    # ==========================================
    # Analytics Requests
    # ==========================================

    analytics_keywords = [
        "dashboard",
        "analytics",
        "summary",
        "statistics",
        "report",
        "trend",
        "insight",
    ]

    if any(word in request for word in analytics_keywords):

        analytics_result = analytics_agent(state)

        state.update(analytics_result)

        state["final_response"] = {
            "type": "analytics",
            "analytics": analytics_result.get(
                "analytics",
                {},
            ),
        }

        return state

    # ==========================================
    # Ticket Processing Workflow
    # ==========================================

    # Step 1
    ticket_result = ticket_agent(state)

    state.update(ticket_result)

    # Step 2
    priority_result = priority_agent(state)

    state.update(priority_result)

    # Step 3
    assignment_result = assignment_agent(
    state,
    state["db"],
    )

    state.update(assignment_result)

    # ==========================================
    # Final Combined Output
    # ==========================================

    state["final_response"] = {

        "type": "ticket",

        "category": state.get("category"),

        "subcategory": state.get("subcategory"),

        "keywords": state.get("keywords"),

        "confidence": state.get("confidence"),

        "priority": state.get("priority"),

        "priority_reason": state.get("priority_reason"),

        "assigned_to": state.get("assigned_to"),

        "assigned_name": state.get("assigned_name"),

        "assignment_reason": state.get("assignment_reason"),
    }

    return state