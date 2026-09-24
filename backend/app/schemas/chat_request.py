from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier for the current claim")
    policy_id: str = Field(..., description="Active policy identifier for the current claim")
    claim_type: str = Field(..., description="Claim type from the original claim")
    claim_amount: float = Field(..., description="Claim amount from the original claim")
    claim_description: str = Field(..., description="Claim description from the original claim")
    claim_summary: str = Field(..., description="Most recent model summary for this claim")
    question: str = Field(..., description="The follow-up question the user asks")
