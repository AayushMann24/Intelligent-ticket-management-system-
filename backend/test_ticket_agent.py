from agents.graph import graph

result = graph.invoke(
    {
        "query": "Create a high priority network issue."
    }
)

print(result["response"])