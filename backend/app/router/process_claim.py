from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.claim_request import ClaimRequest
from backend.app.schemas.claim_response import ClaimResponse
from backend.app.services.claim_service import handle_claim_evaluation
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/claim-processor', tags=["Process-Claim"])

@router.post("/check-claim", response_model=ClaimResponse, status_code=status.HTTP_200_OK)
async def check_claim(claim: ClaimRequest):
    """Main trigger endpoint that receives data from Streamlit."""
    logger.info(f"Received claim processing request for Customer: {claim.customer_id}")
    try:
        return await handle_claim_evaluation(claim)
    except Exception as e:
        logger.error(f"Failure handling agent execution route: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while the AI Agent evaluated the claim: {str(e)}"
        )


