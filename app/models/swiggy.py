from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Restaurant(BaseModel):
    id: str
    name: str
    availabilityStatus: str = "CLOSED"
    distance: Optional[float] = None
    rating: Optional[float] = None

class MenuItem(BaseModel):
    id: str
    name: str
    price: float
    inStock: bool = True

class ProductVariant(BaseModel):
    spinId: str
    name: str
    price: float
    inStock: bool = True

class SearchProductsResponse(BaseModel):
    products: List[Dict]  # Keep flexible for now