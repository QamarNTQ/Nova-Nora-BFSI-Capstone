from fastapi import APIRouter, Depends, HTTPException, status
from uuid import uuid4
from backend.app.schemas.claim_request import ClaimRequest
from backend.app.schemas.claim_response import ClaimResponse
from backend.app.agent import evaluate_claim
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID")
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/claim-processor', tags=["Process-Claim"])

@router.post("/check-claim", response_model=ClaimResponse, status_code=status.HTTP_200_OK)
async def check_claim(claim: ClaimRequest):
    """
    Main trigger endpoint. Streamlit sends a POST request here with the claim data.
    """
    logger.info(f"Received claim processing request for Customer: {claim.customer_id}")
    
    try:
        agent_decision = await evaluate_claim(
            customer_id=claim.customer_id,
            policy_id=claim.policy_id,
            claim_type=claim.claim_type,
            claim_amount=claim.claim_amount,
            claim_description=claim.claim_description,
            session_id=claim.session_id or str(uuid4()),
            model_id=GROQ_MODEL_ID
        )
        
        logger.info(f"Agent valuation finalized for Customer: {claim.customer_id}")
        return agent_decision

    except Exception as e:
        logger.error(f"Failure handling agent execution route: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while the AI Agent evaluated the claim: {str(e)}"
        )

