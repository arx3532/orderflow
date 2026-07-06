from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from app.models.schemas import FoodCart, InstamartCart

class SwiggyState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    
    # User context
    user_id: str
    thread_id: str
    
    # Shared
    address: Optional[Dict] = None
    address_id: Optional[str] = None
    mode: Optional[str] = None  # "food" or "instamart"
    
    search_query: Optional[str]
    restaurants: Optional[List[Dict]]
    # Food specific
    restaurant: Optional[Dict] = None
    food_cart: Optional[FoodCart] = None
    
    # Instamart specific
    instamart_cart: Optional[InstamartCart] = None
    
    # Order
    order_id: Optional[str] = None
    order_status: Optional[Dict] = None
    
    # Control flags
    needs_user_confirmation: bool = False
    last_error: Optional[str] = None
    pending_action: Optional[str] = None
