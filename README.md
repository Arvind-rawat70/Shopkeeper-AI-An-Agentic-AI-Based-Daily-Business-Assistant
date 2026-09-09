# 🛍️ Shopkeeper AI

**An Agentic AI-Based Intelligent Business Assistant for Small Retail Stores**

Shopkeeper AI is a multi-agent system that helps small shopkeepers automate daily business tasks — tracking inventory, analyzing sales, recommending restocks, and calculating profit — through natural language, using **LangGraph**, **LLMs**, and real business data.

---

## 🧠 Why This Exists

Small retailers generate valuable data every day (sales, stock movement, expenses) but rarely have tools to turn it into decisions. A shopkeeper might know milk is selling fast, but not:

- How much to reorder tomorrow
- Which products are slow-moving
- What today's actual profit was
- Which items are about to run out

Traditional billing/inventory apps store this data but don't reason about it. **Shopkeeper AI does.**

Ask it things like:
> "What should I order tomorrow?"
> "How was today's business?"

...and it answers using real database data — not guesses.

---

## ⚙️ How It Works

Instead of a single LLM call, requests flow through a coordinated agent graph:

```
Shopkeeper Query
      │
      ▼
 Intent Router
      │
 ┌────┼──────────────┐
 ▼    ▼               ▼
Sales  Inventory   Purchase
Agent  Agent       Agent
 └────┼──────────────┘
      ▼
 Business Analyst (ML + Data Analysis)
      ▼
 Response Agent
      ▼
 Shopkeeper
```

**Example — "What products should I order tomorrow?"**

```
Query → Intent Detection → Purchase Agent → Get Inventory
      → Get Sales History → Demand Analysis
      → Purchase Recommendation → LLM Explanation → Response
```

```
Recommended purchases for tomorrow:

  Product      Recommended Order
  ---------    ------------------
  Milk         40 packets
  Bread        25 packets
  Biscuits     50 packets

Reason: Milk and bread have high recent sales and current
inventory is relatively low.
```

---

## 🧩 Core Agents & Modules

| Module | What it does |
|---|---|
| **Product Management** | Add/update/delete/view products (name, category, prices, stock, supplier) |
| **Sales Management** | Records daily transactions |
| **Inventory Agent** | Flags low-stock vs. normal-stock products |
| **Sales Analysis Agent** | Daily/weekly sales, best sellers, slow movers, revenue trends |
| **Purchase Recommendation Agent** | Combines stock + sales history + demand forecast → reorder quantities |
| **Profit Analysis Agent** | Revenue − Product Cost − Expenses = Estimated Profit |
| **Daily Report Agent** | End-of-day summary: revenue, profit, best sellers, low stock, recommendations |

**Sample daily report:**
```
Revenue:            Rs 18,450
Estimated Profit:   Rs  3,240

Best Selling:  Milk, Bread, Biscuits
Low Stock:     Milk, Eggs
Slow Moving:   Product X

Recommendation: Increase milk inventory, reduce next order of Product X.
```

---

## 🤖 Machine Learning

Not everything needs an LLM — demand forecasting uses a traditional ML model trained on:

- Previous sales, day of week, product category, season, recent demand, stock level

Candidate models: **Linear Regression → Random Forest → XGBoost → Time-series**, depending on available data.

```
Historical Sales → ML Model → Demand Prediction → LangGraph Agent → Purchase Recommendation
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| LLM | Groq / Ollama (or other supported) |
| Database | MySQL |
| ORM | SQLAlchemy |
| Backend | FastAPI |
| Frontend | Streamlit |
| ML | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib / Plotly |
| Vector Store (if needed) | FAISS / Chroma |
| Monitoring | LangSmith |
| Deployment | Docker + Cloud |

---

## 🗄️ Database Schema

**`products`** — `product_id`, `name`, `category`, `purchase_price`, `selling_price`, `stock_quantity`, `supplier`

**`sales`** — `sale_id`, `product_id` (FK), `quantity`, `sale_price`, `sale_date`

**`expenses`** — `expense_id`, `description`, `amount`, `date`

**`suppliers`** — `supplier_id`, `name`, `contact`, `product_id` (FK)

---

## 🔄 LangGraph State

```python
state = {
    "user_query": "",
    "intent": "",
    "inventory": [],
    "sales": [],
    "forecast": {},
    "recommendation": "",
    "final_response": ""
}
```

Flow: `Query → Intent → Database Data → Analysis → Recommendation → Final Response`

---

## 📍 Progress

### Phase 1 — Setup & Database

| # | Task | Status |
|---|---|---|
| 1 | Create project folders | ✅ |
| 2 | Design database schema | ✅ |
| 3 | Choose MySQL | ✅ |
| 4 | Create `shopkeeper_ai` database | ✅ |
| 5 | Create tables | ✅ |
| 6 | Insert dummy data | ✅ |
| 7 | Connect Python → MySQL via SQLAlchemy | 🔜 Next |
| 8 | Test `SELECT` queries from Python | ⬜ |
| 9 | Build database tools | ⬜ |
| 10 | Build agents | ⬜ |

---

## 💡 What Makes This Different From a Chatbot

It doesn't just generate text — it detects intent, routes to the right agent, pulls real data, runs analysis (including ML predictions where relevant), and returns a grounded, actionable recommendation.

Current Status

Phase 1 is largely completed, with database integration and tool testing still being finalized.

Your current flow is:

User Query → Groq LLM → LangGraph → Database Tool → MySQL → Real Business Data → AI Response

The next major step is to turn these tools into specialized agents such as the Inventory Agent, Sales Agent, Purchase Recommendation Agent, and Business Analyst Agent.
