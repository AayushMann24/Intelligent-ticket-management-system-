from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import TICKET_ANALYSIS_PROMPT
from agents.json_parser import parse_llm_json


def ticket_analysis_agent(state):
    """
    Ticket Intelligence Agent

    Responsibilities:
    - Classify ticket
    - Detect category
    - Detect subcategory
    - Extract keywords
    - Calculate confidence
    """

    title = state["title"]
    description = state["description"]

    prompt = f"""
{TICKET_ANALYSIS_PROMPT}

Ticket Title:
{title}

Ticket Description:
{description}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    result = parse_llm_json(response.content)

    return {

        "category": result.get(
            "category",
            "Other"
        ),

        "subcategory": result.get(
            "subcategory",
            "General"
        ),

        "keywords": result.get(
            "keywords",
            []
        ),

        "confidence": result.get(
            "confidence",
            0.0
        ),

        "messages": [response],
    }