from backend.app.agent import ask_followup
from backend.app.schemas.chat_request import ChatRequest
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv()
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID")

async def handle_chat_followup(question: ChatRequest):
    """Business logic for answering follow-up questions."""
    logger.info(f"Processing chat follow-up for Session ID: {question.session_id}")
    
    try:
        result = await ask_followup(
            session_id=question.session_id,
            question=question.question,
            model_id=GROQ_MODEL_ID,
        )
        logger.info(f"Successfully generated chat response for Session ID: {question.session_id}")
        return result
    except Exception as e:
        logger.error(f"Error inside chatbot service execution for Session {question.session_id}: {str(e)}")
        raise e