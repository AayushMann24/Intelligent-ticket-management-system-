"""
Supervisor Agent

This agent does NOT use an LLM.

Its only responsibility is to determine
which workflow should execute.

Possible workflows:

1. ticket_workflow
2. analytics_workflow
"""


ANALYTICS_KEYWORDS = {

    "dashboard",
    "analytics",
    "analysis",
    "report",
    "reports",
    "statistics",
    "summary",
    "trend",
    "trends",
    "graph",
    "graphs",
    "chart",
    "charts",
    "insight",
    "insights",
    "metrics",

}


def supervisor_agent(state):
    """
    Decide which workflow to execute.

    Returns:
        ticket_workflow
        analytics_workflow
    """

    messages = state.get("messages", [])

    if not messages:
        return {
            "workflow": "ticket_workflow"
        }

    request = messages[-1].content.lower()

    for keyword in ANALYTICS_KEYWORDS:

        if keyword in request:

            return {
                "workflow": "analytics_workflow"
            }

    return {
        "workflow": "ticket_workflow"
    }