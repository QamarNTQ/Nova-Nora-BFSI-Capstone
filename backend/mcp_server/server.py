import os 
import logging
from mcp.server.fastmcp import FastMCP
import torch

from backend.app.tools.claims_history import check_claim_history
from backend.app.tools.fraud_risk import check_fraud_risk
from backend.app.tools.policy_coverage import check_policy_coverage

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

mcp = FastMCP("Claims processing agent", host='127.0.0.1',port=8001)

@mcp.tool()
def policy_coverage(policy_id: str, claim_type: str, claim_amount: float) -> dict:
    """ Check whether a claim type is covered by a policy and whether the claim amount is within the policy limit
    to help the "fraud_risk" tool to check the fraud using the customer history and the policy document.
    Args:
        policy_id (str): The ID of the policy (e.g., 'P001').
        claim_type (str): The type of claim (e.g., 'Accidental damage').
        claim_amount (float): The total cost of the claim."""
    logger.info(
        f"Policy coverage tool called: policy={policy_id}, "
        f"claim_type={claim_type}, amount=Rs. {claim_amount}"
    )
    result = check_policy_coverage(policy_id, claim_type, claim_amount)
    logger.info(f"Policy coverage completed for policy: {policy_id}")
    return result

@mcp.tool()
def claim_history(customer_id: str) -> dict:
    """Retrieve the claim history for a customer to help the "fraud_risk" tool to check the fraud using history"""
    logger.info(f"Claim history tool called for customer: {customer_id}")
    result = check_claim_history(customer_id)
    logger.info(f"Claim history completed for customer: {customer_id}")
    return result

@mcp.tool()
def fraud_risk(customer_id: str, claim_amount: float, policy_coverage_result: dict) -> dict:
    """Assess fraud risk using claim history and policy coverage information."""
    logger.info(
        f"Fraud risk tool called: customer={customer_id}, "
        f"amount=Rs. {claim_amount}"
    )
    result = check_fraud_risk(customer_id, claim_amount, policy_coverage_result)
    logger.info(f"Fraud risk assessment completed for customer: {customer_id}")
    return result


if __name__ == "__main__":
    logger.info("Starting MCP server on port 8001...")
    mcp.run(transport="streamable-http")