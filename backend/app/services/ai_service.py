from agents.orchestrator import (
    analyze_ticket,
    generate_dashboard_insights,
)


class AIService:
    """
    Facade between the backend services
    and the AI Engine.

    No other backend service should import
    anything from the agents package directly.
    """

    @staticmethod
    def analyze_ticket(
        title: str,
        description: str,
        technicians: list,
    ):
        return analyze_ticket(
            title=title,
            description=description,
            technicians=technicians,
        )

    @staticmethod
    def dashboard_insights(
        dashboard_stats: dict,
    ):
        return generate_dashboard_insights(
            dashboard_stats
        )