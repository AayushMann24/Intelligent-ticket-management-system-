from langchain_core.messages import HumanMessage

from agents.graph import graph

result = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Assign ticket 3 to technician 2"
            )
        ]
    }
)

print(result["messages"][-1].content)