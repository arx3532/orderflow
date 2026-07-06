# constants.py (Project Root)
from typing import Final

# ==================== CART LIMITS ====================
FOOD_CART_MAX_AMOUNT: Final[int] = 1000
INSTAMART_MIN_ORDER_AMOUNT: Final[int] = 99

# ==================== POLLING & TIMEOUTS ====================
ORDER_TRACKING_POLL_INTERVAL_SECONDS: Final[int] = 10
MAX_TRACKING_DURATION_MINUTES: Final[int] = 60

# ==================== REDIS ====================
REDIS_URL: Final[str] = "redis://localhost:6379/0"

# ==================== MCP SERVERS ====================
MCP_FOOD_SERVER: Final[str] = "food"
MCP_INSTAMART_SERVER: Final[str] = "im"

# ==================== ERROR KEYWORDS ====================
RESTAURANT_CLOSED_KEYWORDS = [
    "restaurant closed", 
    "not accepting orders", 
    "closed now",
    "unavailable"
]

CART_CAP_KEYWORDS = [
    "exceeds ₹1000", 
    "1000 cap", 
    "cart exceeds",
    "maximum limit"
]

MIN_ORDER_KEYWORDS = [
    "minimum order", 
    "under ₹99", 
    "₹99 minimum"
]

# ==================== DEFAULT VALUES ====================
DEFAULT_ADDRESS_LABEL: Final[str] = "Home"
DEFAULT_PAYMENT_METHOD: Final[str] = "COD"

# ==================== LANGGRAPH CONFIG ====================
MAX_HISTORY_MESSAGES: Final[int] = 20