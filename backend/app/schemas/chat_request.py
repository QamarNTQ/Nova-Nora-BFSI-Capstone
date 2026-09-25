from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Conversation ID returned after claim submission")
    question: str = Field(..., description="The follow-up question the user asks")
