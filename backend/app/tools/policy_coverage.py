import os
import sys
from backend.app.rag.retriever import search_policy
import logging

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_policy_coverage(policy_id: str, claim_type: str, claim_amount: float) -> dict:

    logger.info(
        f"Checking policy coverage: policy={policy_id}, "
        f"claim_type={claim_type}, amount=Rs. {claim_amount}"
)
    query = f"{claim_type} coverage limits exclusions"

    results = search_policy(query=query, policy_id=policy_id)

    logger.info(f"Retrieved {len(results)} policy documents for policy {policy_id}")

    try:
        print("\n Received 'search_policy' results\nSample result:-", results[0].page_content)
    except:
        if not results:
            logger.warning(f"No relevant policy evidence found for policy {policy_id}")
            return {
                "policy_id": policy_id,
                "covered": None,
                "within_limit": None,
                "coverage_limit": None,
                "evidence": [],
                "message": "No relevant policy evidence found."
            }

    evidence = []

    for doc in results:
        evidence.append({
            "source": doc.metadata.get("source"),
            "content": doc.page_content
        })

    logger.info(f"Policy evidence successfully collected for policy {policy_id}")

    return {
        "policy_id": policy_id,
        "claim_type": claim_type,
        "claim_amount": claim_amount,
        "evidence": evidence
    }


if __name__ == "__main__":
    print(check_policy_coverage("P001","Accidental Damage", 50000))