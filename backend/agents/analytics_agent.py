from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import ANALYTICS_PROMPT
from agents.json_parser import parse_llm_json


def analytics_agent(state):
    """
    Analytics Intelligence Agent

    Responsibilities:
    - Analyze dashboard statistics
    - Generate summary
    - Detect operational risks
    - Suggest recommendations
    """

    dashboard = state.get(
        "dashboard_stats",
        {},
    )

    prompt = f"""
{ANALYTICS_PROMPT}

Dashboard Statistics:

{dashboard}
"""

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    result = parse_llm_json(
        response.content
    )

    return {

        "analytics": {

            "summary": result.get(
                "summary",
                "",
            ),

            "risks": result.get(
                "risks",
                [],
            ),

            "recommendations": result.get(
                "recommendations",
                [],
            ),

        },

        "messages": [response],
    }