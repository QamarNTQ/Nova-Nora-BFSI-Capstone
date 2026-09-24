from pydantic import BaseModel, Field

class ClaimRequest(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier, e.g., 'C001'")
    policy_id: str = Field(..., description="Active contract policy identifier, e.g., 'P001'")
    claim_type: str = Field(..., description="The matching category clause of the claim, e.g., 'Accidental Damage'")
    claim_description: str = Field(..., description="The description of the claim")
    claim_amount: float = Field(..., description="Total financial value requested for the payout")
