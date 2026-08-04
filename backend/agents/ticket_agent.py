
from agents.llm import llm
from agents.tools import (
    create_ticket_tool,
    get_all_tickets_tool,
    get_ticket_by_id_tool,
    assign_ticket_tool,
    update_ticket_tool,
    update_ticket_status_tool,
    delete_ticket_tool,

)

llm_with_tools = llm.bind_tools([
    create_ticket_tool,
    get_all_tickets_tool,
    get_ticket_by_id_tool,
    assign_ticket_tool,
    update_ticket_tool,
    update_ticket_status_tool,
    delete_ticket_tool,
])


def ticket_agent(state):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }