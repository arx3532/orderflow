# app/api/endpoints/chat.py
from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage
from app.graphs.main_graph import build_main_graph
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = request.user_id or "default_user"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        graph = build_main_graph()

        # Check if this thread is currently paused at an interrupt
        current_state = await graph.aget_state(config)
        is_interrupted = bool(current_state.next)  # .next is non-empty when paused

        print(f"[CHAT] thread={thread_id} | interrupted={is_interrupted} | next={current_state.next}")

        if is_interrupted:
            # Resume flow: inject user's message into existing state, then continue
            await graph.aupdate_state(
                config,
                {"messages": [HumanMessage(content=request.message)]}
            )
            result = await graph.ainvoke(None, config=config)  # None = don't restart
        else:
            # Fresh conversation or after a completed run
            result = await graph.ainvoke(
                {
                    "messages": [HumanMessage(content=request.message)],
                    "thread_id": thread_id,
                    "user_id": thread_id,
                },
                config=config
            )

        last_message = (
            result.get("messages", [])[-1].content
            if result and result.get("messages")
            else "No response"
        )

        return ChatResponse(
            response=last_message,
            needs_confirmation=result.get("needs_user_confirmation", False) if result else False
        )

    except Exception as e:
        print(f"[CHAT ERROR] {type(e).__name__}: {e}")
        return ChatResponse(
            response=f"Error: {str(e)}",
            needs_confirmation=False
        )