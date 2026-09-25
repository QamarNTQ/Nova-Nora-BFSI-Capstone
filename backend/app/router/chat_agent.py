from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.chat_request import ChatRequest
from backend.app.schemas.chat_response import ChatResponse
from backend.app.agent import ask_followup
from dotenv import load_dotenv
import os
load_dotenv()
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID")
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/chat', tags=["Process-Claim"])


@router.post("/follow-up-question", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def ask_follow_up_question(question: ChatRequest):
    """Answer follow-up questions using the already evaluated claim context."""
    logger.info(f"Received follow-up question for Customer:-")

    try:
        result = await ask_followup(
            session_id=question.session_id,
            question=question.question,
            model_id=GROQ_MODEL_ID,
        )
        return result
    except Exception as e:
        logger.error(f"Failure handling chat route: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while answering the follow-up question: {str(e)}"
        )

