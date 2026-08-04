from agents.llm import llm

from agents.dashboard_tools import (
    dashboard_summary_tool,
    recent_tickets_tool,
    priority_summary_tool,
)

llm_with_tools = llm.bind_tools([
    dashboard_summary_tool,
    recent_tickets_tool,
    priority_summary_tool,
])


def dashboard_agent(state):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }