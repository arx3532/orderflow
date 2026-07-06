# app/agents/supervisor.py
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from app.agents.state import SwiggyState
from app.services.llm_service import llm_service

SUPERVISOR_SYSTEM_PROMPT = """You are a routing assistant for Swiggy.
User wants Food (biryani, pizza, restaurant) → reply "food"
User wants Groceries (milk, vegetables, instamart) → reply "instamart"
Reply with **only** one word: food or instamart."""

async def supervisor_node(state: SwiggyState):
    try:
        prompt = ChatPromptTemplate.from_template(
            SUPERVISOR_SYSTEM_PROMPT + "\n\nUser: {message}"
        )
        chain = prompt | llm_service.llm.with_config(temperature=0)
        
        last_message = state["messages"][-1].content if state.get("messages") else ""
        response = await chain.ainvoke({"message": last_message})
        
        mode = "food" if "instamart" not in response.content.lower() else "instamart"
        
        return {
            "mode": mode,
            "messages": [AIMessage(content=f"Routing to {mode} mode.")]
        }
    except Exception:
        return {
            "mode": "food",
            "messages": [AIMessage(content="Routing to food mode (default).")]
        }