from agents.tools import (
    get_all_tickets_tool,
    create_ticket_tool,
    get_ticket_by_id_tool,
    assign_ticket_tool,
    update_ticket_tool,
    delete_ticket_tool,
)

print(
    get_all_tickets_tool.invoke({})
)

print(
    create_ticket_tool.invoke(
        {
            "title":"AI Test Ticket",
            "description":"Created by LangGraph",
            "priority":"High"
        }
    )
)
from agents.tools import get_ticket_by_id_tool

print(
    get_ticket_by_id_tool.invoke(
        {
            "ticket_id": 1
        }
    )
)
from agents.tools import assign_ticket_tool

print(
    assign_ticket_tool.invoke(
        {
            "ticket_id": 3,
            "assigned_to": 2
        }
    )
)

print(
    update_ticket_tool.invoke(
        {
            "ticket_id": 3,
            "title": "Updated AI Ticket",
            "description": "Updated by LangChain",
            "priority": "High",
            "status": "Assigned",
        }
    )
)

print(
    delete_ticket_tool.invoke(
        {
            "ticket_id": 6
        }
    )
)