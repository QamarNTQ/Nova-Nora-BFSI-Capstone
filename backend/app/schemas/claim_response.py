from pydantic import BaseModel, Field


class ClaimResponse(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    policy_id: str = Field(..., description="Active contract policy identifier")
    claim_type: str = Field(..., description="Claim category")
    claim_amount: float = Field(..., description="Total financial value requested for the payout")
    claim_description: str = Field(..., description="Description of the claim")
    model_output: str = Field(..., description="Model response to the query")