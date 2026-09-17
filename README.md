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


# Shopkeeper AI — ML & Recommendation Module

## 1. Overview

This document describes the architecture and design of the **ML-powered purchase recommendation system** within the Shopkeeper AI project. The goal is to move beyond a simple "LLM in front of a database" and build a genuinely **agentic system** — one where a natural language query is routed to the right specialized agent, and machine learning is invoked only when it's actually needed.

---

## 2. High-Level ML Pipeline

The core demand-forecasting pipeline that feeds purchase recommendations:

```
MySQL Sales Data
      ↓
Pandas Data Processing
      ↓
Feature Engineering
      ↓
Train ML Model
      ↓
Demand Prediction
      ↓
Purchase Recommendation Agent
      ↓
"Order 40 Milk, 25 Bread..."
```

---

## 3. System Architecture

### 3.1 End-to-End Flow

```
                         SHOPKEEPER
                              │
                              ▼
                  Natural Language Query
                              │
                              ▼
                     ┌────────────────┐
                     │  Intent Router │
                     └───────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
       Sales Agent     Inventory Agent   Purchase Agent
            │                │                │
            └────────────────┼────────────────┘
                             │
                             ▼
                    ┌───────────────────┐
                    │  Business Analyst │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              Data Analysis        ML Forecasting
                    │                   │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │   Recommendation  │
                    │   / Response      │
                    │      Agent        │
                    └─────────┬─────────┘
                              │
                              ▼
                         SHOPKEEPER
```

### 3.2 Component Responsibilities

| Component | Responsibility |
|---|---|
| **Intent Router** | Parses the natural language query and decides which agent should handle it. |
| **Sales Agent** | Retrieves and answers questions about sales data from MySQL. |
| **Inventory Agent** | Checks stock levels, flags low-stock items, updates inventory. |
| **Purchase Agent** | Generates reorder recommendations, using ML demand prediction. |
| **Business Analyst** | Combines data across agents; computes revenue, profit, trends, best/slow sellers. |
| **ML / Forecasting Engine** | Predicts future demand from historical sales data. |
| **Response Agent** | Converts technical/DB output into a plain-language answer for the shopkeeper. |

**Example routing:**
- *"Show low-stock products"* → Inventory Agent
- *"What were my sales today?"* → Sales Agent
- *"What should I order tomorrow?"* → Purchase Agent → Business Analyst → ML Forecasting

---

## 4. Design Principle: Don't Over-Invoke ML

A key architectural rule: **ML and the Business Analyst should not run for every query** — only when the question actually requires forecasting or analysis.

**Simple query** (no ML needed):
```
"Show all products"
Intent Router → Inventory/Product Tool → Response
```

**Complex query** (full ML pipeline):
```
"What should I order tomorrow?"

Intent Router
      ↓
Purchase Agent
      ↓
Inventory + Sales History
      ↓
Business Analyst
      ↓
ML Demand Forecast
      ↓
Purchase Recommendation
      ↓
Response Agent
```

This selective invocation is what makes the system genuinely agentic rather than a single LLM wrapper around a database.

---

## 5. Purchase Recommendation Logic

### 5.1 Flow

```
                         Purchase Agent
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
              Inventory Data        Sales History
                    │                     │
                    └──────────┬──────────┘
                               ▼
                    Demand Forecasting ML
                               │
                               ▼
                       Predicted Demand
                               │
                               ▼
                     Reorder Calculation
                               │
                               ▼
                    Purchase Recommendation
```

### 5.2 Reorder Formula

```
Recommended Order = Predicted Demand + Safety Stock − Current Stock
```

### 5.3 Worked Example — Milk

| Metric | Value |
|---|---|
| Current stock | 15 |
| Predicted demand | 40 |
| Safety stock | 10 |
| **Recommended order** | **40 + 10 − 15 = 35 packets** |

**Final shopkeeper-facing response:**
> "Order approximately 35 packets of milk tomorrow. Recent demand is high and current stock is low."

---

## 6. Database Schema

### 6.1 Core Tables

**`products`**
| Column | Description |
|---|---|
| product_id | Primary key |
| name | Product name |
| category | Product category |
| purchase_price | Cost price |
| selling_price | Retail price |
| stock_quantity | Current stock |
| supplier_id | Foreign key → suppliers |

**`sales`**
| Column | Description |
|---|---|
| sale_id | Primary key |
| product_id | Foreign key → products |
| quantity | Units sold |
| sale_price | Price at time of sale |
| sale_date | Date of transaction |

**`expenses`**
| Column | Description |
|---|---|
| expense_id | Primary key |
| description | Expense description |
| amount | Expense amount |
| expense_date | Date incurred |

**`suppliers`**
| Column | Description |
|---|---|
| supplier_id | Primary key |
| name | Supplier name |
| contact | Contact info |

### 6.2 Entity Relationships

```
                    suppliers
                       │
                       │ supplier_id
                       ▼
                    products
                       │
                       │ product_id
                       ▼
                     sales

                    expenses
                (independent table)
```

### 6.3 Business Analyst Calculations

```
Revenue
− Product Cost
− Expenses
= Estimated Profit
```

Plus: sales trends, best sellers, slow movers.

---

## 7. End-to-End Query Flow (Purchase Recommendation)

```
                 SHOPKEEPER
                     │
                     ▼
              Intent Router
                     │
                     ▼
              Purchase Agent
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      MySQL Sales          MySQL Inventory
          │                     │
          └──────────┬──────────┘
                      ▼
              Feature Engineering
                      │
                      ▼
                 ML Model
                      │
                      ▼
              Demand Prediction
                      │
                      ▼
             Reorder Calculation
                      │
                      ▼
              Response Agent
                      │
                      ▼
                 SHOPKEEPER
```

---

## 8. Implementation Roadmap

### Phase 1 — Prototype with Kaggle (M5 Dataset)

Use the M5 forecasting dataset to build and validate the pipeline before real data exists.

```
M5 Dataset → Pandas → EDA → Feature Engineering
   → Train/Test Split → Random Forest / XGBoost → Demand Prediction
```

This provides enough historical data to train a meaningful model from day one.

### Phase 2 — Adapt to Shopkeeper AI

Transform M5 data into the project's own schema:

```
product_id, date, quantity_sold, selling_price, category
```

Connect the trained model to the live MySQL database.

### Phase 3 — Transition to Real Data

Once the database accumulates real sales history, retrain and run the pipeline directly on live data:

```
MySQL → Historical Sales → Feature Engineering → Trained ML Model → Demand Forecast
```

This is what makes the final product genuinely robust and production-ready.

---

## 9. ML Development Workflow (Step-by-Step)

1. Collect Data
2. Clean Data
3. Exploratory Data Analysis (EDA)
4. Feature Engineering
5. Create Target Variable
6. Train/Test Split
7. Train ML Models
8. Evaluate Models
9. Select Best Model
10. Save Model
11. Connect Model to MySQL
12. Demand Prediction
13. Reorder Calculation
14. Feed into Purchase Agent

# Shopkeeper AI — ML Demand Forecasting Module

## Status: Model trained and validated ✅

This README documents the ML workflow completed so far for the Purchase Agent's demand forecasting component, part of the larger Shopkeeper AI project.

---

## Goal

Predict weekly product demand from historical sales data, to feed into the Purchase Agent's reorder recommendation:

```
Recommended Order = Predicted Demand + Safety Stock − Current Stock
```

---

## Dataset

- **Source:** Kaggle M5 Forecasting — Accuracy competition
- **Files used:** `sales_train_validation.csv`, `calendar.csv`, `sell_prices.csv`
- **Subset used:** 80 items from store `CA_1`
- Loaded locally from a `data/` folder (see notebook for path setup)

---

## What's Been Done

### 1. Data Loading & Merging
- Loaded raw M5 CSVs (sales, calendar, prices)
- Selected a random sample of 80 items from one store (initial attempt with only 3 items produced an unusable model — see "Key Findings" below)
- Melted the wide daily format (`d_1 ... d_1913`) into long format: one row per `(item_id, date, sales)`
- Merged in real calendar dates and weekly price data

### 2. Data Cleaning
- **Found and fixed a real data quality issue:** merging sales with `sell_prices` produced rows with `sell_price = 0` for dates before an item was actually introduced in a store
- Confirmed via `groupby` check that 100% of these zero-price rows also had `sales = 0` — proof they were "not yet on sale" placeholder rows, not real transactions
- Dropped all such rows before training
- Verified date continuity per item (no missing calendar days within each item's active sales window)

### 3. Exploratory Data Analysis (EDA)
- Checked structure, missing values, and cardinality of all columns
- Confirmed a realistic **weekend sales spike** (Saturday highest, matching real retail behavior) — validated that the cleaned data reflects genuine demand patterns
- Checked target (`sales`) distribution and outliers — no destructive outliers found
- Plotted total daily sales trend and per-item series to confirm distinct, sensible patterns per product

### 4. Feature Engineering
Built on **weekly aggregated** data (see "Key Findings" for why):
- **Lag features:** sales from 1, 2, 4, and 8 weeks ago
- **Rolling statistics:** 4-week and 8-week rolling mean/std (computed with `shift(1)` before `.rolling()` to prevent data leakage — no row ever sees its own future value)
- **Calendar features:** month, week of year, year
- **Price features:** price change, previous period's price

### 5. Train/Test Split
- **Time-based split** (80% earliest weeks = train, most recent 20% = test)
- Deliberately avoided random shuffling, which would leak future information into training

### 6. Model Training & Comparison
Built a `scikit-learn` `Pipeline` with a `ColumnTransformer` (one-hot encoding `item_id`, passthrough for numeric features) wrapping each model, so preprocessing is fit only on training data.

Compared 5 models:

| Model | MAE | RMSE | R² |
|---|---|---|---|
| **Ridge (best)** | **3.423** | **5.956** | **0.824** |
| Linear Regression | 3.439 | 5.981 | 0.822 |
| Gradient Boosting | 3.439 | 6.211 | 0.808 |
| Random Forest | 3.494 | 6.227 | 0.807 |
| XGBoost | 3.508 | 6.301 | 0.803 |

**Ridge Regression selected as the best model** — saved with `joblib` to `models/demand_forecast_model.joblib`.

---

## Key Findings

1. **Item count matters more than model choice.** An early version trained on just 3 items with daily granularity produced an unusable model (R² ≈ 0.004 — barely better than predicting the mean every time). Scaling to 80 items fixed this.

2. **Weekly aggregation was necessary.** Daily sales for a single low-volume item were mostly 0s and 1s — too sparse and noisy for regression models to learn from. Aggregating to weekly totals gave the target real variance (mean ≈ 2.7, std ≈ 2.5) and better matched the actual business decision (shopkeepers reorder weekly, not daily).

3. **Always compare against a baseline.** Comparing model MAE against a "predict the mean" baseline caught the early failed model before wasting time on hyperparameter tuning — a low MAE alone was misleading given how low-variance the raw daily data was.

4. **Simpler models won.** Ridge/Linear Regression outperformed Random Forest and XGBoost. All 5 models clustered closely (R² 0.80–0.82), suggesting the feature engineering — not model complexity — is doing most of the work, and the demand-to-feature relationship is largely linear at the weekly level.

---

## Next Steps

- [ ] Light hyperparameter tuning on Ridge (`alpha` search via `TimeSeriesSplit` cross-validation)
- [ ] Connect the saved model to the MySQL-backed Purchase Agent for live predictions
- [ ] Wire predicted demand into the reorder calculation
- [ ] Replace the M5-derived training data with real shop sales data once the database accumulates enough history (Phase 3 of the original roadmap)

---

## Files

- `ml_updated_local_data.ipynb` — full pipeline notebook (load → clean → EDA → feature engineer → train → compare → save)
- `ml_pipeline.py` — same pipeline as a modular, runnable Python script
- `models/demand_forecast_model.joblib` — saved best model (Ridge)
