#!/usr/bin/env python3
"""Debug script to identify where the agent freezes"""

import sys
import os

print("=" * 60, flush=True)
print("[STEP 1] Script started", flush=True)

try:
    print("[STEP 2] Importing dependencies...", flush=True)
    from datetime import date
    from typing import Optional
    print("[STEP 2.1] Base imports OK", flush=True)
    
    from dotenv import load_dotenv
    print("[STEP 2.2] dotenv OK", flush=True)
    
    from langchain_core.tools import tool
    from langchain_core.messages import SystemMessage, AIMessage
    print("[STEP 2.3] langchain_core OK", flush=True)
    
    from langchain_groq import ChatGroq
    print("[STEP 2.4] langchain_groq OK", flush=True)
    
    from langgraph.graph import StateGraph, MessagesState, START
    from langgraph.prebuilt import ToolNode, tools_condition
    from langgraph.checkpoint.memory import MemorySaver
    print("[STEP 2.5] langgraph OK", flush=True)
    
    import tools as db
    print("[STEP 2.6] Database tools OK", flush=True)
    
    print("\n[STEP 3] All imports successful!", flush=True)
    
    load_dotenv()
    print("[STEP 4] Environment loaded", flush=True)
    
    print("[STEP 5] Initializing LLM with timeout=10s...", flush=True)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, timeout=10, max_retries=1)
    print("[STEP 5.1] LLM created successfully", flush=True)
    
    # Test the LLM
    print("[STEP 6] Testing LLM with simple message...", flush=True)
    response = llm.invoke("Say 'hello' briefly")
    print(f"[STEP 6.1] LLM Response: {response.content[:100]}", flush=True)
    
    print("\n" + "=" * 60, flush=True)
    print("[SUCCESS] Agent components are working!", flush=True)
    print("=" * 60, flush=True)
    
except TimeoutError as e:
    print(f"\n[ERROR] TIMEOUT: {e}", flush=True)
    print("The LLM API call timed out. Check your internet connection or Groq API status.", flush=True)
except ConnectionError as e:
    print(f"\n[ERROR] CONNECTION: {e}", flush=True)
    print("Could not connect to Groq API or database.", flush=True)
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("=" * 60, flush=True)
