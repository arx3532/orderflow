# app/tools/swiggy_tools.py
from langchain_core.tools import tool
from typing import Dict, List, Optional
from app.services.swiggy_client import swiggy_client
from app.constants import MCP_FOOD_SERVER, MCP_INSTAMART_SERVER

# ====================== FOOD TOOLS ======================

@tool
async def get_addresses() -> Dict:
    """Get user's saved delivery addresses."""
    return await swiggy_client.call_tool(MCP_FOOD_SERVER, "get_addresses")


@tool
async def search_restaurants(address_id: str, query: str) -> Dict:
    """Search for restaurants near the address. Only OPEN restaurants should be used."""
    return await swiggy_client.call_tool(
        MCP_FOOD_SERVER,
        "search_restaurants",
        {"addressId": address_id, "query": query}
    )


@tool
async def get_restaurant_menu(restaurant_id: str) -> Dict:
    """Get full menu of a restaurant."""
    return await swiggy_client.call_tool(
        MCP_FOOD_SERVER,
        "get_restaurant_menu",
        {"restaurantId": restaurant_id}
    )


@tool
async def update_food_cart(restaurant_id: str, items: List[Dict]) -> Dict:
    """Add/update items in food cart. Cart is tied to one restaurant."""
    return await swiggy_client.call_tool(
        MCP_FOOD_SERVER,
        "update_food_cart",
        {"restaurantId": restaurant_id, "items": items}
    )


@tool
async def get_food_cart(address_id: str = None) -> Dict:
    """Get current food cart details."""
    args = {}
    if address_id:
        args["addressId"] = address_id
    return await swiggy_client.call_tool(MCP_FOOD_SERVER, "get_food_cart", args)


@tool
async def fetch_food_coupons() -> Dict:
    """Get available coupons (filter for COD only later)."""
    return await swiggy_client.call_tool(MCP_FOOD_SERVER, "fetch_food_coupons")


@tool
async def apply_food_coupon(code: str) -> Dict:
    """Apply a coupon to the current cart."""
    return await swiggy_client.call_tool(
        MCP_FOOD_SERVER, "apply_food_coupon", {"code": code}
    )


@tool
async def place_food_order(payment_method: str = "COD") -> Dict:
    """Place the final order. This is NOT idempotent — use with care."""
    return await swiggy_client.call_tool(
        MCP_FOOD_SERVER, "place_food_order", {"paymentMethod": payment_method}
    )


@tool
async def track_food_order(order_id: str) -> Dict:
    """Track order status."""
    return await swiggy_client.call_tool(
        MCP_FOOD_SERVER, "track_food_order", {"orderId": order_id}
    )

# ====================== INSTAMART TOOLS ======================

@tool
async def search_products(address_id: str, query: str) -> Dict:
    """Search grocery products on Instamart."""
    return await swiggy_client.call_tool(
        MCP_INSTAMART_SERVER,
        "search_products",
        {"addressId": address_id, "query": query}
    )


@tool
async def your_go_to_items(address_id: str) -> Dict:
    """Get frequently ordered items for quick re-order."""
    return await swiggy_client.call_tool(
        MCP_INSTAMART_SERVER,
        "your_go_to_items",
        {"addressId": address_id}
    )


@tool
async def update_cart(items: List[Dict]) -> Dict:
    """Update Instamart cart using spinId."""
    return await swiggy_client.call_tool(
        MCP_INSTAMART_SERVER, "update_cart", {"items": items}
    )


@tool
async def get_cart() -> Dict:
    """Get current Instamart cart."""
    return await swiggy_client.call_tool(MCP_INSTAMART_SERVER, "get_cart")


@tool
async def checkout(payment_method: str = "COD") -> Dict:
    """Checkout and place Instamart order."""
    return await swiggy_client.call_tool(
        MCP_INSTAMART_SERVER, "checkout", {"paymentMethod": payment_method}
    )


@tool
async def track_order(order_id: str) -> Dict:
    """Track Instamart order."""
    return await swiggy_client.call_tool(
        MCP_INSTAMART_SERVER, "track_order", {"orderId": order_id}
    )