from langchain_core.messages import AIMessage

def user_agent(state):

    return {
        "messages": [
            AIMessage(
                content="User Agent reached successfully."
            )
        ]
    }