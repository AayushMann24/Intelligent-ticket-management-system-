from pydantic import BaseModel


class AssistantRequest(BaseModel):
    message: str


class AssistantResponse(BaseModel):
    response: str
    