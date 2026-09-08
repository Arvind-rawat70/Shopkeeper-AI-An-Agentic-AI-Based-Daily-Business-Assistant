# Shopkeeper-AI-An-Agentic-AI-Based-Daily-Business-Assistant

==============================================================
                        PROJECT REPORT

                       SHOPKEEPER AI
   An Agentic AI-Based Intelligent Business Assistant for
                   Small Retail Stores

   Built with: LangGraph | LLMs | Python | SQL | Machine Learning
==============================================================


TABLE OF CONTENTS
------------------
1.  Abstract
2.  Introduction
3.  Problem Statement
4.  Objectives
5.  Proposed System
6.  Agentic Workflow
7.  Major Modules
8.  Machine Learning Component
9.  Technology Stack
10. Database Design
11. LangGraph State
12. Conclusion


==============================================================
1. ABSTRACT
==============================================================

Small retail shopkeepers perform several business activities
every day, including monitoring inventory, recording sales,
deciding which products to reorder, analyzing profits, and
understanding customer demand. These activities are often
performed manually, making them time-consuming and prone to
errors.

Shopkeeper AI is an Agentic AI-based business assistant
designed to automate and simplify these daily activities. The
system uses LangGraph to coordinate multiple specialized AI
agents that interact with business data and tools. The system
can analyze sales history, monitor inventory, identify
low-stock products, recommend purchases, calculate estimated
profits, and generate daily business reports.

Unlike a conventional chatbot, the proposed system follows an
agentic workflow, where the user's request is analyzed, routed
to the appropriate agent, processed using real business data,
and converted into an actionable response.

The system combines LangGraph, Large Language Models (LLMs),
Python, SQL databases, and Machine Learning to create an
intelligent assistant suitable for small and medium-sized
retail businesses.


==============================================================
2. INTRODUCTION
==============================================================

Small retail businesses generate valuable data through their
daily transactions, but many shopkeepers do not have dedicated
systems for analyzing this information.

For example, a shopkeeper may know that milk is selling
quickly but may not know:

  - How much milk should be ordered tomorrow?
  - Which products are becoming slow-moving?
  - Which products generate the highest profit?
  - How today's sales compare with previous days?
  - Which products are likely to run out soon?

Traditional billing or inventory applications generally store
this information but do not provide intelligent
recommendations.

Shopkeeper AI addresses this problem by combining business
management functionality with Agentic AI.

The system acts as a virtual business assistant that can
understand natural-language questions such as:

    "What should I order tomorrow?"
    "How was today's business?"

...and use actual database information to generate useful
responses.


==============================================================
3. PROBLEM STATEMENT
==============================================================

Small shopkeepers often manage inventory and business
decisions manually. The major problems include:

  - Manual inventory monitoring.
  - Difficulty predicting product demand.
  - Lack of automated sales analysis.
  - Difficulty calculating actual profit.
  - Over-ordering or under-ordering products.
  - Lack of personalized business insights.
  - Limited technical knowledge required to use traditional
    analytics tools.

Therefore, there is a need for an intelligent system that can
analyze business data and provide simple, actionable
recommendations through natural language.


==============================================================
4. OBJECTIVES
==============================================================

The major objectives of Shopkeeper AI are:

Primary Objectives
-------------------
  - Develop an Agentic AI assistant for retail shopkeepers.
  - Automate daily business analysis.
  - Monitor product inventory.
  - Identify low-stock products.
  - Recommend products for restocking.
  - Analyze sales patterns.
  - Calculate estimated revenue and profit.
  - Generate daily and weekly business reports.

AI Objectives
-------------------
  - Implement multi-agent workflows using LangGraph.
  - Use LLMs for natural-language interaction.
  - Integrate external tools with AI agents.
  - Use ML-based demand forecasting where appropriate.
  - Implement state management between agents.
  - Reduce hallucination by grounding responses in database
    information.


==============================================================
5. PROPOSED SYSTEM
==============================================================

The proposed system consists of multiple specialized agents
coordinated by a LangGraph workflow:

                      SHOPKEEPER
                          |
                          v
                 Natural Language Query
                          |
                          v
                  +---------------+
                  | Intent Router |
                  +-------+-------+
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
   Sales Agent      Inventory Agent    Purchase Agent
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                  Business Analyst
                          |
                          v
                  ML / Data Analysis
                          |
                          v
                  Response Agent
                          |
                          v
                     SHOPKEEPER


==============================================================
6. AGENTIC WORKFLOW
==============================================================

The main advantage of the proposed system is that it does not
depend on a single LLM call. Instead, LangGraph controls the
workflow.

Example
-------
Shopkeeper asks: "What products should I order tomorrow?"

    User Query
        -> Intent Detection
        -> Purchase Agent
        -> Get Inventory
        -> Get Sales History
        -> Demand Analysis
        -> Purchase Recommendation
        -> LLM Explanation
        -> Final Response

Sample Output:

    Recommended purchases for tomorrow:

        Product      Recommended Order
        ---------    ------------------
        Milk         40 packets
        Bread        25 packets
        Biscuits     50 packets

    Reason: Milk and bread have high recent sales and their
    current inventory is relatively low.


==============================================================
7. MAJOR MODULES
==============================================================

7.1 Product Management Module
------------------------------
This module stores product information:
  - Product ID
  - Product Name
  - Category
  - Purchase Price
  - Selling Price
  - Current Stock
  - Supplier

The shopkeeper can:
  - Add products.
  - Update products.
  - Delete products.
  - View inventory.

7.2 Sales Management Module
------------------------------
The system records daily sales.

7.3 Inventory Agent
------------------------------
The Inventory Agent monitors stock levels. It can identify:

    Product      Status
    ---------    ---------------
    Milk         Low Stock [!]
    Bread        Low Stock [!]
    Biscuits     Normal [OK]
    Rice         Normal [OK]

7.4 Sales Analysis Agent
------------------------------
This agent analyzes:
  - Daily sales.
  - Weekly sales.
  - Best-selling products.
  - Slow-moving products.
  - Revenue trends.
  - Average transaction value.

7.5 Purchase Recommendation Agent
------------------------------
This is one of the most important agents. It combines:

    Current Inventory + Historical Sales + Recent Demand
    + Demand Forecast  ->  Purchase Recommendation

    Product      Current Stock    Recommended Order
    ---------    --------------   ------------------
    Milk         8                40
    Bread        5                25
    Eggs         12               60

7.6 Profit Analysis Agent
------------------------------
The system distinguishes between revenue and profit.
Basic calculation:

    Revenue:               Rs 20,000
    Product Cost:          Rs 15,000
    Expenses:              Rs  1,000
    --------------------------------
    Estimated Profit:      Rs  4,000

7.7 Daily Report Agent
------------------------------
At the end of the day, the system can generate:

    DAILY BUSINESS REPORT
    ----------------------
    Revenue:            Rs 18,450
    Estimated Profit:   Rs  3,240

    Best Selling:
      - Milk
      - Bread
      - Biscuits

    Low Stock:
      - Milk
      - Eggs

    Slow Moving:
      - Product X

    Recommendation:
      Increase milk inventory and reduce the next order of
      Product X.


==============================================================
8. MACHINE LEARNING COMPONENT
==============================================================

The project should not use an LLM for everything. For demand
prediction, a traditional ML model can be used, based on
features such as:

  - Previous Sales
  - Day of Week
  - Product Category
  - Season
  - Recent Demand
  - Stock Level

Possible models:
  - Linear Regression
  - Random Forest
  - XGBoost
  - Time-series models

For the initial version, Random Forest, XGBoost, or a simple
regression-based model can be experimented with, depending on
the available dataset.

    Historical Sales
        -> Machine Learning Model
        -> Demand Prediction
        -> LangGraph Agent
        -> Purchase Recommendation


==============================================================
9. TECHNOLOGY STACK
==============================================================

    Component               Technology
    ---------------------   -----------------------------------
    Programming Language    Python
    Agent Framework         LangGraph
    LLM Framework           LangChain
    LLM                     Groq / Ollama / other supported LLM
    Database                SQLite (initially)
    Backend                 FastAPI
    Frontend                Streamlit (initially)
    Machine Learning        Scikit-learn
    Data Processing         Pandas, NumPy
    Visualization           Matplotlib / Plotly
    Vector Database         FAISS / Chroma (if required)
    Version Control         Git / GitHub
    Deployment              Docker + Cloud
    Monitoring              LangSmith


==============================================================
10. DATABASE DESIGN
==============================================================

Product Table
------------------------------
    product_id        Unique product identifier
    name               Product name
    category           Product category
    purchase_price     Cost price of the product
    selling_price      Selling price of the product
    stock_quantity     Current stock quantity
    supplier           Linked supplier

Sales Table
------------------------------
    sale_id            Unique sale identifier
    product_id         Reference to Product table
    quantity           Quantity sold
    sale_price         Price at time of sale
    sale_date          Date of sale

Expenses Table
------------------------------
    expense_id         Unique expense identifier
    description        Expense description
    amount             Expense amount
    date               Date of expense

Supplier Table
------------------------------
    supplier_id        Unique supplier identifier
    name               Supplier name
    contact            Supplier contact details
    product_id         Reference to Product table


==============================================================
11. LANGGRAPH STATE
==============================================================

A shared state can contain information such as:

    state = {
        "user_query": "",
        "intent": "",
        "inventory": [],
        "sales": [],
        "forecast": {},
        "recommendation": "",
        "final_response": ""
    }

Flow:

    Query -> Intent -> Database Data -> Analysis
          -> Recommendation -> Final Response


==============================================================
12. CONCLUSION
==============================================================

Shopkeeper AI is proposed as an Agentic AI-based daily business
assistant for small retail businesses. The system combines
LangGraph, LLMs, databases, and machine learning to automate
business analysis and provide actionable recommendations.

The key distinction from a traditional chatbot is that the
system does not simply generate text. It can understand the
user's intent, select the appropriate agent, retrieve real
business data, perform analysis, use ML predictions when
required, and generate a contextual recommendation.

This project provides practical exposure to modern AI
engineering concepts including LangGraph, agent orchestration,
tool calling, state management, RAG where applicable, ML
integration, database interaction, API development, and
deployment.

Most importantly, the project can be developed from scratch,
demonstrating a genuine understanding of how Agentic AI systems
are designed and implemented, rather than reproducing a
tutorial.

--------------------------------------------------------------
Recommended Project Title:

  "Shopkeeper AI: An Agentic AI-Based Intelligent Business
   Assistant for Small Retail Stores"
--------------------------------------------------------------
