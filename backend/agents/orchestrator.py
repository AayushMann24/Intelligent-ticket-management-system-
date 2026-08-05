from langchain_core.messages import HumanMessage

from agents.graph import ticket_graph
from agents.analytics_agent import analytics_agent
from agents.supervisor import supervisor_agent


def analyze_ticket(
    title: str,
    description: str,
    technicians: list,
):
    """
    Main AI entry point for ticket creation.
    """

    state = {

        "messages": [

            HumanMessage(
                content=f"""
Title:
{title}

Description:
{description}
"""
            )

        ],

        "workflow": "",

        "title": title,

        "description": description,

        "category": None,

        "subcategory": None,

        "keywords": [],

        "confidence": None,

        "priority": None,

        "priority_reason": None,

        "technicians": technicians,

        "assigned_to": None,

        "assigned_name": None,

        "assignment_reason": None,

        "dashboard_stats": None,

        "analytics": None,

        "final_response": None,
    }

    # -------------------------------
    # Decide workflow
    # -------------------------------

    state.update(
        supervisor_agent(state)
    )

    if state["workflow"] != "ticket_workflow":
        raise ValueError(
            "Supervisor selected the wrong workflow."
        )

    # -------------------------------
    # Execute Ticket Graph
    # -------------------------------

    result = ticket_graph.invoke(state)

    return result


def generate_dashboard_insights(
    dashboard_stats: dict,
):
    """
    AI entry point for dashboard analytics.
    """

    state = {

        "messages": [

            HumanMessage(
                content="Generate dashboard insights."
            )

        ],

        "workflow": "analytics_workflow",

        "title": "",

        "description": "",

        "category": None,

        "subcategory": None,

        "keywords": [],

        "confidence": None,

        "priority": None,

        "priority_reason": None,

        "technicians": [],

        "assigned_to": None,

        "assigned_name": None,

        "assignment_reason": None,

        "dashboard_stats": dashboard_stats,

        "analytics": None,

        "final_response": None,
    }

    result = analytics_agent(state)

    return result["analytics"]