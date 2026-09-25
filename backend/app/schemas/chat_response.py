from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    session_id: str = Field(..., description="Conversation ID used for this answer")
    answer: str = Field(..., description="Answer to the follow-up question using claim context")
