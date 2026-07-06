from typing import Optional
import httpx

class SwiggyAPIError(Exception):
    def __init__(self, message: str, tool_name: Optional[str] = None):
        self.tool_name = tool_name
        super().__init__(message)

class RestaurantClosedError(SwiggyAPIError):
    pass

class CartCapExceededError(SwiggyAPIError):
    pass

class MinimumOrderNotMetError(SwiggyAPIError):
    pass

class ItemOutOfStockError(SwiggyAPIError):
    pass

class AddressNotServiceableError(SwiggyAPIError):
    pass

class CouponInvalidError(SwiggyAPIError):
    pass

def classify_swiggy_error(
    message: str,
    code: Optional[int] = None,
    http_status: Optional[int] = None,
    tool_name: Optional[str] = None,
) -> Exception:

    msg_lower = message.lower()

    # Food-specific errors
    if any(phrase in msg_lower for phrase in ["restaurant closed", "not accepting orders"]):
        return RestaurantClosedError(message, tool_name)

    if "cart exceeds" in msg_lower or "₹1000" in message or "1000 cap" in msg_lower:
        return CartCapExceededError(message, tool_name)

    if "minimum order" in msg_lower or "₹99" in message:
        return MinimumOrderNotMetError(message, tool_name)

    # Instamart-specific
    if "out of stock" in msg_lower or "not available" in msg_lower:
        return ItemOutOfStockError(message, tool_name)

    if "not serviceable" in msg_lower or "address not serviceable" in msg_lower:
        return AddressNotServiceableError(message, tool_name)

    if "coupon" in msg_lower and ("invalid" in msg_lower or "expired" in msg_lower):
        return CouponInvalidError(message, tool_name)

    if http_status and http_status >= 500:
        return SwiggyAPIError(f"Upstream service error: {message}" , tool_name)

    return SwiggyAPIError(message, tool_name)
