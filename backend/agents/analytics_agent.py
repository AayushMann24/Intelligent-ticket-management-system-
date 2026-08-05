from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import ANALYTICS_PROMPT
from agents.json_parser import parse_llm_json


def analytics_agent(state):
    """
    Analytics Agent

    Generates AI insights from dashboard statistics.
    """

    analytics = state.get("analytics", {})

    prompt = f"""
{ANALYTICS_PROMPT}

Dashboard Statistics:

{analytics}

Generate management insights.

Return ONLY valid JSON.
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    result = parse_llm_json(response.content)

    return {
        "analytics": result,
        "messages": [response],
    }