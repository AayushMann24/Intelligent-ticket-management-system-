from langgraph.graph import StateGraph, START, END

from agents.state import AgentState

from agents.supervisor import supervisor
from agents.ticket_agent import ticket_agent
from agents.priority_agent import priority_agent
from agents.assignment_agent import assignment_agent
from agents.analytics_agent import analytics_agent

builder = StateGraph(AgentState)

# ================================
# Nodes
# ================================

builder.add_node("supervisor", supervisor)

builder.add_node("ticket_agent", ticket_agent)

builder.add_node("priority_agent", priority_agent)

builder.add_node("assignment_agent", assignment_agent)

builder.add_node("analytics_agent", analytics_agent)

# ================================
# Flow
# ================================

builder.add_edge(
    START,
    "supervisor",
)

builder.add_edge(
    "supervisor",
    "ticket_agent",
)

builder.add_edge(
    "ticket_agent",
    "priority_agent",
)

builder.add_edge(
    "priority_agent",
    "assignment_agent",
)

builder.add_edge(
    "assignment_agent",
    END,
)

builder.add_edge(
    "analytics_agent",
    END,
)

graph = builder.compile()