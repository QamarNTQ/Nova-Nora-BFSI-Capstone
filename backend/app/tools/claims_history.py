import os
import logging
import pandas as pd


CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
CLAIMS_HISTORY_PATH = os.path.join(BACKEND_ROOT, "data", "claims_history.csv")

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

if os.path.exists(CLAIMS_HISTORY_PATH):
    df = pd.read_csv(CLAIMS_HISTORY_PATH)
else:
    logger.error(f"claims_history.csv not found at {CLAIMS_HISTORY_PATH}!")
    df = pd.DataFrame()

def check_claim_history(customer_id: str) -> dict:
    logger.info(f"Checking claim history for customer: {customer_id}")
    if df.empty:
        return {"customer_id": customer_id, "claim_count": 0, "previous_claims": []}
    
    customer_claims = df[df['customer_id']==customer_id].copy()

    if customer_claims.empty:
        logger.info(f"No previous claims found for customer: {customer_id}")
        return {
            "customer_id": customer_id,
            "claim_count": 0,
            "previous_claims": []
        }

    customer_claims["claim_date"] = pd.to_datetime(customer_claims["claim_date"])
    customer_claims = customer_claims.sort_values("claim_date",ascending=False)

    claim_count = len(customer_claims)
    logger.info(f"Found {claim_count} previous claims for customer: {customer_id}")

    logger.info("Returning response from claim_history tool")
    return {
        "customer_id": customer_id,
        "claim_count": len(customer_claims),
        "previous_claims": customer_claims.to_dict(orient="records")
    }