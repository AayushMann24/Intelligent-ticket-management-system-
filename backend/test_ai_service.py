from app.services.ai_service import AIService

technicians = [
    {
        "id": 1,
        "name": "Rahul",
        "specialization": "Hardware",
        "workload": 4,
    },
    {
        "id": 2,
        "name": "Priya",
        "specialization": "Network",
        "workload": 1,
    },
    {
        "id": 3,
        "name": "Aman",
        "specialization": "Software",
        "workload": 2,
    },
]

result = AIService.analyze_ticket(
    title="Printer not working",
    description="Printer in Lab 4 has a paper jam and nobody can print.",
    technicians=technicians,
)

print(result)