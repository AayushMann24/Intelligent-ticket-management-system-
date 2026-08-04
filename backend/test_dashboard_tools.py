from agents.dashboard_tools import (
    dashboard_summary_tool,
    recent_tickets_tool,
    priority_summary_tool,
)

print(dashboard_summary_tool.invoke({}))

print(recent_tickets_tool.invoke({}))

print(priority_summary_tool.invoke({}))