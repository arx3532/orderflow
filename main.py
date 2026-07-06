# main.py (Project Root)
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints.chat import router as chat_router
from app.graphs.main_graph import build_main_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{settings.PROJECT_NAME} is starting...")
    try:
        build_main_graph()   # Initialize the LangGraph
        print("Main graph built successfully")
    except Exception as e:
        print(f"Warning: Failed to build graph: {e}")
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Include routers
app.include_router(chat_router)

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "Swiggy AI Agent",
        "version": "0.1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)