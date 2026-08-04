from agents.llm import llm

from agents.user_tools import (
    get_all_users_tool,
    get_user_by_id_tool,
    update_user_role_tool,
)

llm_with_tools = llm.bind_tools([
    get_all_users_tool,
    get_user_by_id_tool,
    update_user_role_tool,
])


def user_agent(state):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }