from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import ASSIGNMENT_PROMPT
from agents.json_parser import parse_llm_json
from agents.assignment_tools import get_technician_workload


def assignment_agent(state, db):
    """
    Assignment Agent

    Uses real technicians from the database.
    """

    title = state["title"]
    description = state["description"]

    category = state.get("category", "")
    subcategory = state.get("subcategory", "")
    priority = state.get("priority", "")

    technicians = get_technician_workload(db)

    prompt = f"""
{ASSIGNMENT_PROMPT}

Ticket Title:
{title}

Ticket Description:
{description}

Category:
{category}

Subcategory:
{subcategory}

Priority:
{priority}

Available Technicians:

{technicians}

Choose the BEST technician.

Return ONLY JSON.

Example:

{{
    "assigned_to":2,
    "assigned_name":"Rahul",
    "reason":"Hardware specialist with lowest workload"
}}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    result = parse_llm_json(response.content)

    return {

        "assigned_to": result.get("assigned_to"),

        "assigned_name": result.get("assigned_name"),

        "assignment_reason": result.get("reason"),

        "messages": [response],
    }