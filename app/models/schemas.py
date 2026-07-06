from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Address(BaseModel):
    id: str
    label: str
    displayText: str
    addressId: Optional[str] = None

class CartItem(BaseModel):
    item_id: str
    name: str
    quantity: int
    price: float
    total: Optional[float] = None

class FoodCart(BaseModel):
    items: List[CartItem]
    total: float
    restaurant_name: Optional[str] = None

class InstamartCart(BaseModel):
    items: List[CartItem]
    total: float
    delivery_fee: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    status: str
    total: float
    estimated_delivery: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str = Field(..., description="Unique user identifier for conversation state")
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    needs_confirmation: bool = False
    current_cart: Optional[Dict] = None
    order_id: Optional[str] = None