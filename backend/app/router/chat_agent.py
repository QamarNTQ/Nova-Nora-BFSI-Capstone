from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.chat_request import ChatRequest
from backend.app.schemas.chat_response import ChatResponse
from backend.app.services.chatbot_service import handle_chat_followup
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/chat', tags=["Process-Claim"])

@router.post("/follow-up-question", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def ask_follow_up_question(question: ChatRequest):
    """Endpoint to trigger follow-up questions."""
    logger.info("Received follow-up question.")
    try:
        return await handle_chat_followup(question)
    except Exception as e:
        logger.error(f"Failure handling chat route: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while answering the follow-up question: {str(e)}"
        )
