from uuid import uuid4
import os
from dotenv import load_dotenv
from backend.app.agent import evaluate_claim
from backend.app.schemas.claim_request import ClaimRequest
import logging

logger = logging.getLogger(__name__)

load_dotenv()
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID")

async def handle_claim_evaluation(claim: ClaimRequest):
    """Business logic for evaluating an insurance claim."""
    session_id = claim.session_id or str(uuid4())
    logger.info(f"Initiating claim evaluation service for Customer ID: {claim.customer_id} | Session ID: {session_id}")
    
    try:
        agent_decision = await evaluate_claim(
            customer_id=claim.customer_id,
            policy_id=claim.policy_id,
            claim_type=claim.claim_type,
            claim_amount=claim.claim_amount,
            claim_description=claim.claim_description,
            session_id=session_id,
            model_id=GROQ_MODEL_ID
        )
        logger.info(f"Service completed evaluation for Customer ID: {claim.customer_id} with outcome status: {getattr(agent_decision, 'status', 'Success')}")
        return agent_decision
    except Exception as e:
        logger.error(f"Error inside claim evaluation service for Customer {claim.customer_id}: {str(e)}")
        raise e
