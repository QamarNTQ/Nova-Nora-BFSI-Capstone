from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Answer to the follow-up question using claim context")
