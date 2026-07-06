from fastapi import FastAPI, HTTPException
from pydantic import HttpUrl
from app.services.swiggy_client import swiggy_client
from app.core.config import settings

async def get_swiggy_client():
    try:
        return swiggy_client
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Swiggy service unavailable"
        )

async def get_current_user(user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    return user_id