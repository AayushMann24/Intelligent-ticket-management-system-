from langchain_core.messages import HumanMessage

from agents.graph import graph

queries = [
    "Create a printer ticket",
    "Show dashboard summary",
    "Create technician Rahul",
]

for query in queries:

    print("\n========================")
    print("USER:", query)

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        }
    )

    print(result["messages"][-1].content)