from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    conversation_history: list[dict] = []
    user_email: str = "abc@email.com"
