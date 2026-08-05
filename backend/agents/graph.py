from langgraph.graph import StateGraph, START, END

from agents.state import AgentState

from agents.ticket_analysis import ticket_analysis_agent
from agents.priority_agent import priority_agent
from agents.assignment_agent import assignment_agent


builder = StateGraph(AgentState)

# ==========================================
# Nodes
# ==========================================

builder.add_node(
    "ticket_analysis",
    ticket_analysis_agent,
)

builder.add_node(
    "priority",
    priority_agent,
)

builder.add_node(
    "assignment",
    assignment_agent,
)

# ==========================================
# Workflow
# ==========================================

builder.add_edge(
    START,
    "ticket_analysis",
)

builder.add_edge(
    "ticket_analysis",
    "priority",
)

builder.add_edge(
    "priority",
    "assignment",
)

builder.add_edge(
    "assignment",
    END,
)

ticket_graph = builder.compile()