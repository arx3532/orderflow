from langchain_core.messages import AIMessage, HumanMessage
from app.services.swiggy_client import swiggy_client
from app.services.llm_service import llm_service
from app.agents.state import SwiggyState
from app.tools.swiggy_tools import (
    get_addresses, search_restaurants, get_restaurant_menu,
    update_food_cart, get_food_cart, place_food_order,
    track_food_order
)
from app.utils.error_handlers import classify_swiggy_error
from app.constants import FOOD_CART_MAX_AMOUNT
from .prompts import FOOD_REVIEW_PROMPT
import re

async def resolve_address(state: SwiggyState):
    try:
        result = await get_addresses.ainvoke({})
        print(f"DEBUG get_addresses result: {result}")

        # Swiggy returns a plain string — parse address IDs from it
        if isinstance(result, str):
            import re
            matches = re.findall(r'\(ID:\s*([^\)]+)\)', result)
            print(f"DEBUG parsed IDs: {matches}")

            if not matches:
                return {"messages": [AIMessage(content="Could not parse address. Please try again.")]}

            # Pick Home address if mentioned, else first one
            if "Home" in result:
                home_match = re.search(r'\[Home\].*?\(ID:\s*([^\)]+)\)', result)
                address_id = home_match.group(1) if home_match else matches[0]
            else:
                address_id = matches[0]

            print(f"DEBUG selected address_id: {address_id}")

            return {
                "address_id": address_id,
                "messages": [AIMessage(content=f"Using your Home address for delivery.")]
            }

        # Fallback: original dict/list handling
        addresses = result.get("data", []) if isinstance(result, dict) else result
        home = next((a for a in addresses if a.get("label") == "Home"), addresses[0] if addresses else None)
        if not home:
            return {"messages": [AIMessage(content="Please add a delivery address in the Swiggy app first.")]}
        address_id = home.get("id") or home.get("addressId")
        return {
            "address": home,
            "address_id": address_id,
            "messages": [AIMessage(content=f"Using delivery address: {home.get('displayText', 'Home')}")]
        }

    except Exception as e:
        print(f"DEBUG resolve_address ERROR: {type(e).__name__}: {e}")
        return {"last_error": str(e), "messages": [AIMessage(content="Failed to fetch addresses.")]}

async def search_restaurants_node(state: SwiggyState):
    try:
        address_id = state.get("address_id")
        user_messages = [msg for msg in state.get("messages", []) if getattr(msg, "type", None) == "human"]
        last_user_message = user_messages[-1].content if user_messages else ""

        print(f"DEBUG Search: User said: '{last_user_message}'")

        # Extract query
        prompt = f"Extract only the main food item or cuisine. 1-3 words.\nUser: \"{last_user_message}\""
        extraction = await llm_service.llm.ainvoke(prompt)
        query = extraction.content.strip().lower()

        print(f"DEBUG Search: LLM extracted query → '{query}'")

        result = await search_restaurants.ainvoke({
            "address_id": address_id,
            "query": query
        })

        print(f"DEBUG Search: Raw result type: {type(result)}")

               # Handle string response from Swiggy
        if isinstance(result, str):
            print("DEBUG Search: Got string response")
            
            # Simple parsing
            restaurants = []
            lines = result.split('\n')
            for line in lines:
                if re.search(r'^\d+\.', line):  # Lines starting with number.
                    # Extract name and ID
                    match = re.search(r'(\d+)\.\s*(.+?)\s*\(ID:\s*([^\)]+)\)', line)
                    if match:
                        restaurants.append({
                            "name": match.group(2).strip(),
                            "id": match.group(3).strip(),
                            "raw": line
                        })

            summary = f"Found {len(restaurants)} restaurants for **{query}**:\n\n{result[:800]}..."
            return {
                "messages": [AIMessage(content=summary)],
                "restaurants": restaurants,
                "search_query": query
            }

        # Handle dict response
        restaurants = result.get("data", []) if isinstance(result, dict) else result
        print(f"DEBUG Search: Got {len(restaurants)} restaurants")

        summary = f"Found some {query} restaurants:\n\n"
        for i, r in enumerate(restaurants[:5], 1):
            status = "OPEN" if r.get("availabilityStatus") == "OPEN" else "CLOSED"
            summary += f"{i}. {r.get('name')} {status}\n"

        summary += "\nReply with number or name."

        return {
            "messages": [AIMessage(content=summary)],
            "restaurants": restaurants,
            "search_query": query
        }

    except Exception as e:
        print(f"DEBUG Search Error: {e}")
        return {"messages": [AIMessage(content="Couldn't search restaurants.")]}


async def select_restaurant_node(state: SwiggyState):
    try:
        restaurants = state.get("restaurants", [])
        messages = state.get("messages", [])

        print(f"DEBUG Select: Available restaurants: {len(restaurants)}")

        if not restaurants:
            return {
                "messages": [AIMessage(content="No restaurants found. Try a different search.")],
            }

        # Find the last HUMAN message specifically — not just last message
        human_messages = [m for m in messages if isinstance(m, HumanMessage)]
        if not human_messages:
            # No human input yet, just show the list and wait
            summary = "Please reply with the number of the restaurant you want:\n"
            for i, r in enumerate(restaurants, 1):
                summary += f"{i}. {r['name']}\n"
            return {"messages": [AIMessage(content=summary)]}

        last_human = human_messages[-1].content.lower()
        print(f"DEBUG Select: Last human message: '{last_human}'")

        # Skip if the last human message is the original search query, not a selection
        # A selection is short — just a number or a name
        is_selection = (
            last_human.strip().isdigit() or
            any(r["name"].lower() in last_human for r in restaurants)
        )

        if not is_selection:
            summary = "Which restaurant would you like? Reply with the number:\n"
            for i, r in enumerate(restaurants, 1):
                summary += f"{i}. {r['name']}\n"
            return {"messages": [AIMessage(content=summary)]}

        # Match selection
        selected = None
        for i, r in enumerate(restaurants, 1):
            if str(i) == last_human.strip() or r["name"].lower() in last_human:
                selected = r
                break

        if selected:
            return {
                "restaurant": selected,
                "restaurant_id": selected["id"],
                "messages": [AIMessage(content=f"Selected **{selected['name']}**. Fetching menu now...")],
            }
        else:
            summary = "Couldn't match that. Please reply with the number:\n"
            for i, r in enumerate(restaurants, 1):
                summary += f"{i}. {r['name']}\n"
            return {"messages": [AIMessage(content=summary)]}

    except Exception as e:
        print(f"DEBUG Select Error: {e}")
        return {"messages": [AIMessage(content="Please choose a restaurant by number.")]}
        

async def get_restaurant_menu_node(state: SwiggyState):
    try:
        # For now, we'll need restaurant_id from state (we'll improve this later)
        restaurant_id = state.get("restaurant_id")
        if not restaurant_id:
            return {
                "messages": [AIMessage(content="Please select a restaurant first.")],
            }

        result = await get_restaurant_menu.ainvoke({"restaurant_id": restaurant_id})
        
        return {
            "messages": [AIMessage(content="Here is the menu for the selected restaurant:")],
            # You can store menu in state later
        }
    except Exception as e:
        print(f"DEBUG Menu Error: {e}")
        return {
            "messages": [AIMessage(content="Could not load the menu right now.")],
        }


async def update_food_cart_node(state: SwiggyState):
    try:
        restaurant_id = state.get("restaurant_id")
        if not restaurant_id:
            return {
                "messages": [AIMessage(content="Please select a restaurant first.")],
            }
        # For demo, we'll add a sample item. In real flow, LLM will decide what to add.
        sample_item = {
            "itemId": "sample_item_1",   # Replace with real itemId from menu
            "quantity": 1
        }

        result = await update_food_cart.ainvoke({
            "restaurant_id": restaurant_id,
            "items": [sample_item]
        })

        return {
            "messages": [AIMessage(content="Added item to your cart.")],
        }
    except Exception as e:
        print(f"DEBUG Update Cart Error: {e}")
        return {
            "messages": [AIMessage(content="Could not add item to cart.")],
        }


async def review_cart_node(state: SwiggyState):
    try:
        address_id = state.get("address_id")
        print(f"DEBUG review_cart address_id: {address_id}")

        if not address_id:
            return {
                "messages": [AIMessage(content="Address not found. Please try again.")],
                "needs_user_confirmation": False
            }

        cart_result = await get_food_cart.ainvoke({"address_id": address_id})
        print("DEBUG: Cart result:", cart_result)

        if isinstance(cart_result, str):
            if "empty" in cart_result.lower():
                return {
                    "messages": [AIMessage(content="Got it! Your cart is empty right now.\n\nWhat would you like to order? For example: biryani, pizza, chicken curry, etc.")],
                    "needs_user_confirmation": False
                }

        cart_data = cart_result.get("data", cart_result) if isinstance(cart_result, dict) else cart_result

        if not cart_data or not cart_data.get("items"):
            return {
                "messages": [AIMessage(content="Your cart is empty. What would you like to order? (e.g., biryani, pizza)")],
                "needs_user_confirmation": False
            }

        # Build summary
        summary = f"Cart Summary:\n"
        for item in cart_data.get("items", []):
            summary += f"• {item.get('name')} × {item.get('quantity')} = ₹{item.get('price', 0)}\n"
        summary += f"\n**Total: ₹{cart_data.get('total', 0)}**\n\nShall I place the order? (Yes / No)"

        return {
            "food_cart": cart_data,
            "needs_user_confirmation": True,
            "messages": [AIMessage(content=summary)]
        }

    except Exception as e:
        print(f"DEBUG Cart Error: {e}")
        return {
            "messages": [AIMessage(content="No items in cart yet. What would you like to eat?")],
            "needs_user_confirmation": False
        }


async def place_order_node(state: SwiggyState):
    try:
        result = await place_food_order.ainvoke({"paymentMethod" : "COD"})
        order_id = result.get("data", {}).get("orderId") or result.get("orderId")

        return {
            "order_id" : order_id,
            "messages" : [AIMessage(content =f"OrderOrder placed successfully! Order ID: {order_id}")],
            "needs_user_confirmation" : False
        }


    except Exception as e:
        error = classify_swiggy_error(str(e) , tool_name="place_food_order")
        return {"last_error": str(error), "messages": [AIMessage(content=f"Order failed: {str(error)}")]}


async def track_order_node(state: SwiggyState):
    if not state.get("order_id"):
        return {"messages": [AIMessage(content="No active order to track.")]}
    
    try:
        status = await track_food_order.ainvoke({"orderId" : state['order_id']})
        return {
            "order_status" : status,
            "messages": [AIMessage(content=f"Order status: {status.get('status', 'Unknown')}")]
        }

    except Exception as e:
        return {"messages": [AIMessage(content="Could not fetch tracking info right now.")]}


FOOD_NODES = {
    "resolve_address": resolve_address,
    "search_restaurants": search_restaurants_node,
    "select_restaurant": select_restaurant_node,   
    "get_restaurant_menu": get_restaurant_menu_node,
    "update_food_cart": update_food_cart_node,
    "review_cart": review_cart_node,
    "place_order": place_order_node,
    "track_order": track_order_node,
}