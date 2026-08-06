from agents.assistant_agent import assistant_agent


class AssistantService:
    """
    Service layer for the AI Assistant.

    The rest of the backend should never
    directly call the LLM.
    """

    @staticmethod
    def chat(question: str) -> str:
        return assistant_agent(question)