from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import PRIORITY_PROMPT
from agents.json_parser import parse_llm_json


def priority_agent(state):
    """
    Priority Intelligence Agent

    Responsibilities:
    - Determine ticket priority
    - Explain why the priority was chosen

    Input:
        - title
        - description
        - category
        - subcategory

    Output:
        - priority
        - priority_reason
    """

    title = state["title"]
    description = state["description"]

    category = state.get("category", "Other")
    subcategory = state.get("subcategory", "General")

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

        "priority": result.get(
            "priority",
            "Medium"
        ),

        "priority_reason": result.get(
            "reason",
            "Default priority assigned."
        ),

        "messages": [response],
    }