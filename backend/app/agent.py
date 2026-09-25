import os
import json
import asyncio
import time
from typing import Any
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.agents.middleware import AgentState, before_agent
from langgraph.runtime import Runtime
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID")

MCP_CLIENT = None
MCP_TOOLS = None
MCP_CLIENT_LOCK = asyncio.Lock()
AGENT = None
AGENT_LOCK = asyncio.Lock()
CHECKPOINTER = InMemorySaver()


async def getmcp_tools():
    global MCP_CLIENT, MCP_TOOLS

    if MCP_TOOLS is not None:
        return MCP_TOOLS

    async with MCP_CLIENT_LOCK:
        if MCP_TOOLS is not None:
            return MCP_TOOLS

        MCP_CLIENT = MultiServerMCPClient(
            {
                "claims_server": {
                    "url": "http://127.0.0.1:8001/mcp",
                    "transport": "http"
                }
            }
        )

        try:
            tools = await MCP_CLIENT.get_tools()
            MCP_TOOLS = tools
            return tools
        except Exception:
            MCP_CLIENT = None
            MCP_TOOLS = None
            raise


async def get_agent(model_id: str = GROQ_MODEL_ID):
    global AGENT

    if AGENT is not None:
        return AGENT

    async with AGENT_LOCK:
        if AGENT is not None:
            return AGENT

        tools = await getmcp_tools()
        llm = ChatGroq(
            model=model_id,
            temperature=0,
            max_tokens=700,
            groq_api_key=GROQ_API_KEY,
        )
        AGENT = create_agent(
            model=llm,
            tools=tools,
            middleware=[validate_claim],
            checkpointer=CHECKPOINTER,
            system_prompt="""
            You are an insurance claims processing agent.
            For a new claim, use policy_coverage, claim_history, and fraud_risk.
            Then return a concise answer with policy coverage, claim history,
            fraud risk, recommendation, and reason. Keep it under 500 tokens.

            For a follow-up question, use the existing conversation and claim
            evaluation. Answer the question directly without restarting the claim
            evaluation or inventing information.
            """
        )
        return AGENT

@before_agent
def validate_claim(state: AgentState, runtime: Runtime):
    messages = state['messages']
    content = messages[-1].content
    required = ["Customer ID:", "Policy ID:", "Claim Type:", "Claim Amount:"]
    
    if not all(field in content for field in required):
        if len(messages) > 1:
            return None
        return {
            "messages": [{"role": "assistant", "content": "Invalid claim: required claim information is missing."}]
        }

    try:
        amount_part = content.split("Claim Amount:")[1].strip()
        clean_amount = amount_part.replace(",", "").replace("Rs.", "").strip()
        clean_amount = clean_amount.split()[0]
        amount = float(clean_amount)
    except (ValueError, IndexError):
        return {
            "messages": [{"role": "assistant", "content": "Invalid claim amount format."}]
        }

    if amount <= 0:
        return {
           "messages": [{"role": "assistant", "content": "Claim amount must be greater than zero."}]
        }
    return None


async def evaluate_claim(customer_id: str, policy_id: str, claim_type: str, 
                        claim_amount: float, claim_description: str,
                        session_id: str, model_id: str = GROQ_MODEL_ID):
    try:
        agent = await get_agent(model_id)
        print("Available MCP tools:")
        for tool in await getmcp_tools():
            print("-", tool.name)
    except Exception as e:
        print(f"Failed to connect to MCP Server: {e}")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503, 
            detail=f"MCP Tools Server connection failed. Make sure Terminal 1 is running on port 8001. Error: {e}"
        )

    claim = f"""
    Customer ID: {customer_id}
    Policy ID: {policy_id}
    Claim Type: {claim_type}
    Claim Amount: Rs. {claim_amount}
    Claim Description: {claim_description}
    """

    print("Invoking agent...")
    start_time = time.time()

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": claim
                }
            ]  
        },
        config={"configurable": {"thread_id": session_id}}
    )

    print("Agent invocation complete!")
    response = result['messages'][-1].content
    print(f"Agent took {time.time() - start_time:.2f} seconds to complete.")

    return {
        "session_id": session_id,
        "customer_id": customer_id,
        "policy_id": policy_id,
        "claim_type": claim_type,
        "claim_amount": claim_amount,
        "claim_description": claim_description,
        "model_output": response
    }


async def ask_followup(session_id: str, question: str, model_id: str = GROQ_MODEL_ID) -> dict[str, Any]:
    agent = await get_agent(model_id)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": session_id}}
    )
    return {"session_id": session_id, "answer": result["messages"][-1].content}


if __name__ == "__main__":
    result = asyncio.run(evaluate_claim("C001", "P001", "Accidental", 20000))
    print(result)
