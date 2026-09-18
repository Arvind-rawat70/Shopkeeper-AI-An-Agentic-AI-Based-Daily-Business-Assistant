from datetime import date
from typing import Optional
import sys
 
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, AIMessage

print("[INIT] Loading environment...", flush=True)
load_dotenv()

print("[INIT] Importing LangChain Groq (this may take a moment)...", flush=True)
try:
    from langchain_groq import ChatGroq
    print("[INIT] Groq import successful", flush=True)
except ImportError as e:
    print(f"\n[ERROR] Failed to import Groq: {e}", flush=True)
    print("[ERROR] Run: pip install langchain-groq", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Network/Connection issue: {e}", flush=True)
    print("[ERROR] Check: 1) Internet connection 2) Firewall 3) Groq API key", flush=True)
    sys.exit(1)

print("[INIT] Importing LanGraph...", flush=True)
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

print("[INIT] Importing database tools...", flush=True)
import tools as db
from config import MODEL, TEMPERATURE, TIMEOUT_SECONDS, MAX_RETRIES

print(f"[INIT] Using model: {MODEL}")
print("[INIT] All imports successful!", flush=True)

import json


def _safe_result(result):
    """Serialize a tool's return value into a guaranteed non-empty string.

    Groq's API requires tool-role message content to be either a non-empty
    string or a list with at least one item. LangChain does not always
    stringify list/dict tool outputs before packing them into a
    ToolMessage - an empty list (e.g. "no sales found in this range")
    can be passed through as a literal [] object, which satisfies
    neither requirement and gets rejected with a 400 error. Routing
    every tool's return value through this function avoids that.
    """
    if result is None or result == [] or result == {} or result == "":
        return "No results found."
    try:
        return json.dumps(result, default=str)
    except TypeError:
        return str(result)


# ---------------------------------------------------------------------
# 1. Wrap the DB functions as LLM-callable tools
#
# Dates come in from the LLM as plain strings (YYYY-MM-DD) because tool
# schemas need JSON-serializable types - we parse to date() right
# before calling into database/tools.py.
# ---------------------------------------------------------------------
@tool
def get_all_products() -> str:
    """Get all products in the shop with their category, prices, and current stock."""
    return _safe_result(db.get_all_products())

@tool
def get_product_by_name(name: str) -> str:
    """Look up product(s) by name (partial, case-insensitive match).
    Call this first if you only have a product name but a tool needs product_id."""
    return _safe_result(db.get_product_by_name(name))

@tool
def get_low_stock_products(threshold: int = 20) -> str:
    """List products with stock_quantity below the given threshold (default 20).
    Use for reorder / restock alerts."""
    return _safe_result(db.get_low_stock_products(threshold))


@tool
def update_stock(product_id: int, new_quantity: int) -> str:
    """Set a product's stock_quantity to a new absolute value.
    Requires the numeric product_id - resolve it with get_product_by_name first if needed."""
    rows = db.update_stock(product_id, new_quantity)
    return f"Updated stock for product_id={product_id} to {new_quantity}. Rows affected: {rows}"
 
 
@tool
def add_sale(product_id: int, quantity: int, sale_price: float, sale_date: Optional[str] = None) -> str:
    """Record a new sale. sale_date is optional, format YYYY-MM-DD, defaults to today.
    Requires the numeric product_id."""
    parsed_date = date.fromisoformat(sale_date) if sale_date else None
    rows = db.add_sale(product_id, quantity, sale_price, parsed_date)
    return f"Recorded sale: {quantity} unit(s) of product_id={product_id} at {sale_price} each. Rows affected: {rows}"
 
 
@tool
def get_sales_by_date_range(start_date: str, end_date: str) -> str:
    """Get all individual sale records between start_date and end_date (YYYY-MM-DD, inclusive)."""
    return _safe_result(db.get_sales_by_date_range(date.fromisoformat(start_date), date.fromisoformat(end_date)))
 
 
@tool
def get_best_selling_products(start_date: str, end_date: str, limit: int = 5) -> str:
    """Get the top-selling products by quantity sold within a date range (YYYY-MM-DD)."""
    return _safe_result(db.get_best_selling_products(date.fromisoformat(start_date), date.fromisoformat(end_date), limit))
 
 
@tool
def get_slow_moving_products(start_date: str, end_date: str, max_sold: int = 5) -> str:
    """Get products that sold at or below max_sold units within a date range (YYYY-MM-DD).
    Useful for spotting dead stock."""
    return _safe_result(db.get_slow_moving_products(date.fromisoformat(start_date), date.fromisoformat(end_date), max_sold))
 
 
@tool
def get_expenses_by_date_range(start_date: str, end_date: str) -> str:
    """Get all expense records between start_date and end_date (YYYY-MM-DD, inclusive)."""
    return _safe_result(db.get_expenses_by_date_range(date.fromisoformat(start_date), date.fromisoformat(end_date)))
 
 
@tool
def add_expense(description: str, amount: float, expense_date: Optional[str] = None) -> str:
    """Record a new expense. expense_date is optional, format YYYY-MM-DD, defaults to today."""
    parsed_date = date.fromisoformat(expense_date) if expense_date else None
    rows = db.add_expense(description, amount, parsed_date)
    return f"Recorded expense '{description}' of {amount}. Rows affected: {rows}"
 
 
@tool
def get_revenue_and_profit(start_date: str, end_date: str) -> str:
    """Get total revenue, product cost, expenses, and estimated profit for a date range (YYYY-MM-DD)."""
    return _safe_result(db.get_revenue_and_profit(date.fromisoformat(start_date), date.fromisoformat(end_date)))
 
 
@tool
def get_supplier_for_product(product_id: int) -> str:
    """Get supplier contact details linked to a given product_id."""
    return _safe_result(db.get_supplier_for_product(product_id))

TOOLS = [
    get_all_products,
    get_product_by_name,
    get_low_stock_products,
    update_stock,
    add_sale,
    get_sales_by_date_range,
    get_best_selling_products,
    get_slow_moving_products,
    get_expenses_by_date_range,
    add_expense,
    get_revenue_and_profit,
    get_supplier_for_product
]

llm = ChatGroq(
    model=MODEL,
    temperature=TEMPERATURE,
    timeout=TIMEOUT_SECONDS,
    max_retries=MAX_RETRIES
)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = SystemMessage(content=(
    "You are Shopkeeper AI, an assistant for a small shop owner. "
    "Answer questions about products, stock, sales, expenses, profit, and "
    "suppliers by calling the tools available to you - never guess numbers, "
    "always call a tool to get real data.\n\n"
    "Do NOT assume the current date or use any system clock. If the user "
    "provides a relative date (for example: 'this month', 'last week', or "
    "'yesterday'), ask the user to provide explicit YYYY-MM-DD start and end "
    "dates before calling any tool. Do not invent or infer dates from the "
    "system time.\n\n"
    "If a tool needs a product_id but the user only gave a product name, "
    "call get_product_by_name first to resolve it - if more than one match "
    "comes back, ask the user which one they mean instead of guessing.\n\n"
    "Keep answers short, concrete, and business-focused - this is a busy "
    "shopkeeper, not a data scientist. Use rupee figures plainly (e.g. "
    "'₹4,250'), not raw JSON."
))

# ---------------------------------------------------------------------
# 3. Graph: chatbot node <-> tools node, looped until the LLM stops
#    calling tools (tools_condition routes to END when no tool call).
# -----------------------------------------------------

def chatbot_node(state:MessagesState):
    messages = [SYSTEM_PROMPT] + state["messages"]
    try:
        print("[DEBUG] Calling LLM with tools...", flush=True)
        response = llm_with_tools.invoke(messages)  # FIX: Use .invoke() instead of calling directly
        print("[DEBUG] LLM responded successfully", flush=True)
    except Exception as e:
        error_str = str(e)
        # Check for model decommissioned error
        if "decommissioned" in error_str.lower():
            content = (
                f"Error: Model '{config.MODEL}' is no longer supported.\n"
                f"Please update config.py with an available model.\n"
                f"Check: https://console.groq.com/docs/models"
            )
        elif "does not exist" in error_str.lower() or "no access" in error_str.lower():
            content = (
                f"Error: No access to model '{config.MODEL}'.\n"
                f"Please check your Groq API key and try a different model in config.py"
            )
        else:
            content = f"LLM Error: {error_str}"
        
        print(f"[DEBUG] LLM error: {e}", flush=True)
        response = AIMessage(content=content)
    return {'messages': [response]}


builder = StateGraph(MessagesState)
builder.add_node('chatbot', chatbot_node)
builder.add_node('tools', ToolNode(TOOLS))
builder.add_edge(START, 'chatbot')
builder.add_conditional_edges('chatbot', tools_condition, {'tools': 'tools', '__end__': '__end__'})
builder.add_edge("tools", "chatbot")

# In-memory checkpointing for now (per-process only). Swap MemorySaver for
# a MySQL-backed checkpointer later, same idea as your MULTI-USE-CHATBOT
# project, if you want threads to survive a restart.
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

 
# ---------------------------------------------------------------------
# 4. Simple CLI loop for manual testing
# -------------------

if __name__ == "__main__":
    thread_id = "cli-session-1"
    config = {'configurable':{'thread_id': thread_id}}
    print("Welcome to Shopkeeper AI! Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("[DEBUG] Processing message...")
        try:
            result = graph.invoke(
                {"messages": [("user", user_input)]},
                config=config,
            )
            print("[DEBUG] Graph invocation complete", flush=True)
            ai_response = result["messages"][-1].content
            print(f"AI: {ai_response}\n", flush=True)
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}\n", flush=True)