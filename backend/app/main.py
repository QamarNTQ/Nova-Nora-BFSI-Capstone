import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.rag.ingestion import run_ingestion
from dotenv import load_dotenv
from backend.app.router import process_claim
from backend.app.router import chat_agent

load_dotenv()
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID")


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that runs automatically on FastAPI server startup.
    """
    logger.info("FastAPI server is booting up...")
    logger.info("Checking policy documents and triggering automated Vector DB Ingestion...")
    
    try:
        run_ingestion()
        logger.info("Vector DB pipeline successfully initialized and populated!")
    except Exception as e:
        logger.error(f"Critical Failure: Automatic ingestion failed during startup: {e}")
    
    yield
    logger.info("FastAPI server is shutting down cleanly...")


# Initialize the main FastAPI application engine
app = FastAPI(title="Claims Processing Agent API Gateway",version="1.0",lifespan=lifespan)

# Enabling CORS
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process_claim.router)
app.include_router(chat_agent.router)

@app.get("/")
def read_root():
    """Health check endpoint to ensure backend connectivity."""
    return {"status": "healthy", "message": "Claims Processing Core Backend is running seamlessly."}