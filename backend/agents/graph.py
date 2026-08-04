from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from agents.state import AgentState
from agents.supervisor import supervisor
from agents.ticket_agent import ticket_agent
from agents.dashboard_agent import dashboard_agent
from agents.user_agent import user_agent
from agents.router import route_agent

from agents.tools import (
    create_ticket_tool,
    get_all_tickets_tool,
    get_ticket_by_id_tool,
    assign_ticket_tool,
    update_ticket_tool,
    update_ticket_status_tool,
    delete_ticket_tool,
)

ticket_tool_node = ToolNode([
    create_ticket_tool,
    get_all_tickets_tool,
    get_ticket_by_id_tool,
    assign_ticket_tool,
    update_ticket_tool,
    update_ticket_status_tool,
    delete_ticket_tool,
])

builder = StateGraph(AgentState)

builder.add_node("supervisor", supervisor)
builder.add_node("ticket_agent", ticket_agent)
builder.add_node("dashboard_agent", dashboard_agent)
builder.add_node("user_agent", user_agent)

builder.add_node("ticket_tools", ticket_tool_node)

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

# Ticket Agent
builder.add_conditional_edges(
    "ticket_agent",
    tools_condition,
    {
        "tools": "ticket_tools",
        END: END,
    },
)

builder.add_edge("ticket_tools", "ticket_agent")

builder.add_edge("dashboard_agent", END)
builder.add_edge("user_agent", END)

graph = builder.compile()