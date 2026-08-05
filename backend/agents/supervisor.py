from langchain_core.messages import AIMessage


def supervisor(state):
    """
    Supervisor Agent

    Decides which workflow should run.
    """

    messages = state.get("messages", [])

    request = ""

    if messages:
        request = messages[-1].content.lower()

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

        state["next"] = "analytics_agent"

    else:

        state["next"] = "ticket_agent"

    state["messages"].append(
        AIMessage(
            content=f"Routing to {state['next']}"
        )
    )

    return state