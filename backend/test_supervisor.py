from langchain_core.messages import HumanMessage

from agents.supervisor import supervisor

tests = [
    "Create a high priority printer ticket",
    "Show dashboard summary",
    "Create technician Rahul",
    "Show all tickets",
    "How many tickets are open?",
]

for query in tests:

    result = supervisor(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        }
    )

    print(f"\nQuery : {query}")
    print(f"Route : {result}")