from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import PRIORITY_PROMPT
from agents.json_parser import parse_llm_json


def priority_agent(state):
    """
    Priority Agent

    Determines ticket priority based on
    ticket details and analysis.
    """

    title = state["title"]
    description = state["description"]

    category = state.get("category", "")
    subcategory = state.get("subcategory", "")

    prompt = f"""
{PRIORITY_PROMPT}

Ticket Title:
{title}

Ticket Description:
{description}

Detected Category:
{category}

Detected Subcategory:
{subcategory}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    result = parse_llm_json(response.content)

    return {
        "priority": result.get("priority"),
        "priority_reason": result.get("reason"),
        "messages": [response],
    }