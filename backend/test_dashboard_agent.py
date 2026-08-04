from langchain_core.messages import HumanMessage

from agents.dashboard_agent import dashboard_agent


state = {
    "messages": [
        HumanMessage(
            content="Show dashboard summary"
        )
    ]
}

result = dashboard_agent(state)

print(result["messages"][0])