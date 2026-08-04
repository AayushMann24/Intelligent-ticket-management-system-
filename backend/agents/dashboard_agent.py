from langchain_core.messages import AIMessage

def dashboard_agent(state):

    return {
        "messages": [
            AIMessage(
                content="Dashboard Agent reached successfully."
            )
        ]
    }