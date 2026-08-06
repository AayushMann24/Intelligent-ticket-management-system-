from langchain_core.messages import HumanMessage

from agents.llm import llm
from agents.prompts import ASSISTANT_PROMPT


def assistant_agent(question: str):
    """
    General ITMS AI Assistant.
    """

    prompt = f"""
{ASSISTANT_PROMPT}

User Question:
{question}
"""

    response = llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    return response.content