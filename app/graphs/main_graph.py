# app/graphs/main_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import SwiggyState
from app.agents.food.nodes import FOOD_NODES
from app.agents.supervisor import supervisor_node
#from app.agents.instamart.nodes import INSTAMART_NODES

main_graph = None

def build_main_graph():
    global main_graph
    if main_graph is not None:
        return main_graph

    checkpointer = MemorySaver()
    graph = StateGraph(SwiggyState)

    graph.add_node("supervisor", supervisor_node)

    # Register all food nodes
    for name, node in FOOD_NODES.items():
        graph.add_node(name, node)

    # Register all instamart nodes
    #for name, node in INSTAMART_NODES.items():
     #   graph.add_node(name, node)

    # Supervisor routes based on agent field
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state.get("agent", "food"),
        {
            "food": "resolve_address",
            #"instamart": "search_products"   # instamart starts here
        }
    )

    # Food edges (same as now)
    graph.add_edge("resolve_address", "search_restaurants")
    graph.add_edge("search_restaurants", "select_restaurant")
    
    def restaurant_selected(state: SwiggyState) -> str:
        return "selected" if state.get("restaurant_id") else "waiting"

    graph.add_conditional_edges(
        "select_restaurant",
        restaurant_selected,
        {
            "selected": "get_restaurant_menu",
            "waiting": END   # return response to user, wait for next message
        }
    )
    graph.add_edge("get_restaurant_menu", "update_food_cart")
    graph.add_edge("update_food_cart", "review_cart")
    graph.add_conditional_edges(
        "review_cart",
        lambda state: "place_order" if state.get("needs_user_confirmation") else END,
    )
    graph.add_edge("place_order", "track_order")
    graph.add_edge("track_order", END)
    '''
    # Instamart edges
    graph.add_edge("search_products", "select_product")
    graph.add_edge("select_product", "review_instamart_cart")
    graph.add_conditional_edges(
        "review_instamart_cart",
        lambda state: "place_instamart_order" if state.get("needs_user_confirmation") else END,
    )
    graph.add_edge("place_instamart_order", END)
    '''
    # Both interrupts registered here
    main_graph = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["select_restaurant"] #"select_product"]
    )
    return main_graph