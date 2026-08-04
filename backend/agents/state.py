from typing import TypedDict, List
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Shared state passed between all agents.
    """

    query: str
    response: str
    next_agent: str
    messages: List[BaseMessage]