from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.supervisor import supervisor
from agents.ticket_agent import ticket_agent
from agents.dashboard_agent import dashboard_agent
from agents.user_agent import user_agent
from agents.router import route_agent

builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("ticket_agent", ticket_agent)
builder.add_node("dashboard_agent", dashboard_agent)
builder.add_node("user_agent", user_agent)

builder.add_edge(START, "supervisor")

builder.add_conditional_edges(
    "supervisor",
    route_agent,
    {
        "ticket_agent": "ticket_agent",
        "dashboard_agent": "dashboard_agent",
        "user_agent": "user_agent",
    },
)

builder.add_edge("ticket_agent", END)
builder.add_edge("dashboard_agent", END)
builder.add_edge("user_agent", END)

graph = builder.compile()