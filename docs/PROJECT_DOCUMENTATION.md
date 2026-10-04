# Shopkeeper AI Project Documentation

This document explains the current state of the project, the architecture, setup steps, and how the main modules work together.

## 1. Project Overview

Shopkeeper AI is an agentic business assistant for a small retail shop. It combines:

- a LangGraph chatbot for business queries
- a Streamlit dashboard for live data review
- a MySQL-backed data layer for products, sales, expenses, and suppliers
- a FastAPI forecasting endpoint for demand prediction and reorder recommendations
- a simple ML model trained for demand forecasting

The goal is to help a shopkeeper answer questions such as:

- Which products are low in stock?
- Which items sell best this week?
- What is the revenue and profit for a selected date range?
- Who is the supplier for a product?
- How much stock should be reordered?

## 2. System Architecture

The repository is organized into the following layers:

- [database/](../database): database connection logic, agent tools, and configuration
- [ui/app.py](../ui/app.py): graphical dashboard for querying business data
- [ml/api.py](../ml/api.py): FastAPI demand forecast API
- [api.py](../api.py): export entry point for the backend app
- [chat_response_utils.py](../chat_response_utils.py): short business response formatting helpers
- [data/](../data): sales and product dataset files
- [tests/](../tests): unit tests for response helpers

## 3. Main Features

### 3.1 Agentic shop assistant

The core conversational agent is implemented in [database/agent.py](../database/agent.py). It uses:

- LangChain Groq
- LangGraph state graph
- tool calling for database operations
- a system prompt that instructs the assistant to use real data and avoid guessing

The agent exposes database actions such as:

- get_all_products
- get_product_by_name
- get_low_stock_products
- update_stock
- add_sale
- get_sales_by_date_range
- get_best_selling_products
- get_slow_moving_products
- get_expenses_by_date_range
- add_expense
- get_revenue_and_profit
- get_supplier_for_product

This makes the assistant capable of handling operational and reporting questions in natural language.

### 3.2 SQL-safe business dashboard

The Streamlit UI in [ui/app.py](../ui/app.py) provides a business-friendly interface to:

- connect to the configured database
- ask natural-language business questions
- generate read-only SQL through an LLM
- validate queries before execution
- display charts and summary data
- use forecasting-related actions

The dashboard includes safeguards against unsafe SQL by blocking operations like UPDATE, DELETE, DROP, and other non-SELECT statements.

### 3.3 Demand forecasting API

The forecasting service in [ml/api.py](../ml/api.py) exposes:

- POST /predict-demand
- POST /reorder-recommendation

These endpoints use a trained joblib model located in:

- [ml/models/demand_forecast_model.joblib](../ml/models/demand_forecast_model.joblib)

The service predicts demand for a product at a target week and recommends how much should be ordered based on current stock and required safety stock.

### 3.4 Data layer

The raw database access code is in [database/tools.py](../database/tools.py), which exposes functions for:

- products
- sales
- expenses
- revenue/profit calculations
- supplier lookups

Connection details are centralized in [database/config.py](../database/config.py) and [database/database.py](../database/database.py).

## 4. Project Workflow

A typical usage flow is:

1. Configure environment variables from [.env.example](../.env.example)
2. Start a MySQL database with the required schema
3. Install dependencies from [requirements.txt](../requirements.txt)
4. Run the forecasting API or Streamlit dashboard
5. Ask a business question through the assistant or UI
6. The assistant fetches verified data and answers in a business-focused way

## 5. Environment Setup

### 5.1 Create environment file

Copy the example file and fill in your values:

```bash
copy .env.example .env
```

The expected variables include:

```env
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=shopkeeper_ai
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
SHOPKEEPER_API_URL=http://127.0.0.1:8000
```

## 16. Notifications (Email)

The project can send scheduled business summaries by email using Gmail SMTP. The implementation uses `email_service.py` to build and send messages, helper scripts under `tools/` for testing and manual sends, and an APScheduler-based scheduler for automation.

Files involved:
- `email_service.py`: builds the plain-text report and sends email via SMTP.
- `tools/_email_preview.py`: preview the generated email body.
- `tools/_send_email.py`: send a single morning report from the CLI.
- `tools/test_smtp_ssl.py`: quick SMTP SSL auth test.
- `tools/email_scheduler.py`: scheduler that sends morning (07:00) and evening (17:00) reports.
- `tools/run_scheduler.ps1`: PowerShell helper to start the scheduler detached.

Environment variables (add to `.env`):

```env
EMAIL_SENDER=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_gmail_app_password     # 16-character app password
OWNER_EMAIL=recipient@example.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_DEBUG=false
```

Gmail notes and troubleshooting:
- Use a Google App Password when 2‑Step Verification is enabled. Create one here: https://support.google.com/accounts/answer/185833
- If Google blocks sign-in, try: https://accounts.google.com/DisplayUnlockCaptcha
- Set `EMAIL_DEBUG=true` to enable smtplib debug output during troubleshooting.

Quick commands:

Preview the email body:
```bash
python tools/_email_preview.py
```

Test SMTP auth (SSL, port 465):
```bash
python tools/test_smtp_ssl.py
```

Send a single morning report now:
```bash
python tools/_send_email.py
```

Start the scheduler (07:00 and 17:00):
```bash
pip install -r requirements.txt
python tools/email_scheduler.py
# or on Windows detached:
.\tools\run_scheduler.ps1
```

Logging and reliability:
- The scheduler prints to stdout; run under a process manager or redirect output to a logfile for persistence.
- The `send_email` function now supports `EMAIL_DEBUG` and raises clear errors for auth and connection issues.

### How the Gmail notification flow works

- The service reads SMTP configuration and credentials from environment variables (see the example above).
- When a report is triggered (manual or scheduled), `email_service.build_daily_report()` gathers data via `database.tools` and formats a plain-text summary.
- `email_service.send_email()` creates an `EmailMessage`, connects to Gmail's SMTP server (`smtp.gmail.com`) on the configured port, negotiates TLS (STARTTLS on port 587) or uses SSL (port 465), authenticates using the supplied credentials (recommended: a Google App Password), and issues the RFC‑2822 message transfer commands (`MAIL FROM`, `RCPT TO`, `DATA`).
- The function includes optional debug output (`EMAIL_DEBUG=true`) which enables smtplib tracing for troubleshooting SMTP exchanges.

### Challenges encountered while building Gmail notifications

- Authentication restrictions: Google blocks simple username/password logins for many accounts. The supported pattern is 2‑Step Verification + App Passwords or OAuth2. Without an app password the server returns errors such as `535 BadCredentials` or `534 InvalidSecondFactor` and closes the connection.
- Security blocks from Google: sign-ins from new locations or automated scripts may be blocked by Google account protections. This requires either an account unlock step or using an app password.
- Connection reliability: transient network issues or abrupt server disconnects appear as `SMTPServerDisconnected`. Robust error handling and retries are required for production use.
- Visibility and logging: smtplib default logging is minimal — enabling debug output helps, but for production you should log structured send attempts, responses and failures to a file or external logging service.
- Secret management: storing app passwords in `.env` is convenient for local dev but not secure for production. Use a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault) when deploying.
- Delivery and rate limits: SMTP providers impose rate and daily sending limits. For higher volume or guaranteed deliverability, API-based providers (SendGrid, Mailgun, SES) are recommended.

### Mitigations and recommendations

- Use 2‑Step Verification and generate a Google App Password; set that value as `EMAIL_PASSWORD` in `.env` for CLI scripts and local runs.
- For long‑running schedulers, run under a process manager (systemd, NSSM on Windows, or a container orchestration) so the scheduler restarts on failure.
- Add retry logic with exponential backoff around `send_email()` and persist failed attempts to a queue or database for later replay.
- Use structured logging and capture SMTP debug output to a log file when `EMAIL_DEBUG` is enabled.
- For production deployments or higher volume, switch to an API-based transactional email provider and store credentials in a secrets manager.


## 6. Installation

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 7. Running the Project

### 7.1 Start the forecasting API

```bash
uvicorn ml.api:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 Start the Streamlit dashboard

```bash
streamlit run ui/app.py
```

### 7.3 Run the chatbot agent

The agent can be started from the database module context if needed:

```bash
python database/agent.py
```

## 8. Database Schema Expectations

The app expects the following tables (or equivalent data):

- products
- suppliers
- sales
- expenses

Typical columns include:

- products: product_id, name, category, purchase_price, selling_price, stock_quantity, supplier_id
- suppliers: supplier_id, name, contact
- sales: sale_id, product_id, quantity, sale_price, sale_date
- expenses: expense_id, description, amount, expense_date

## 9. Example Business Questions

The assistant is designed to answer questions like:

- What is the total revenue for this month?
- Which item has the lowest stock?
- Which products sold the most in the last 7 days?
- What were the expenses during the last month?
- Who is the supplier for Rice?
- Should I reorder Tea?

## 10. Example API Calls

### Predict demand

```bash
curl -X POST "http://127.0.0.1:8000/predict-demand" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "HOBBIES_1_001",
    "target_week": "2026-09-21",
    "current_sell_price": 99.5
  }'
```

### Reorder recommendation

```bash
curl -X POST "http://127.0.0.1:8000/reorder-recommendation" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "HOBBIES_1_001",
    "target_week": "2026-09-21",
    "current_sell_price": 99.5,
    "safe_stock": 10,
    "current_stock": 15
  }'
```

## 11. Testing

The project includes a focused unit test suite in [tests/test_chat_response_utils.py](../tests/test_chat_response_utils.py).

Run tests with:

```bash
pytest -q
```

## 12. Notes on Safety and Design

Several safety measures are built into the project:

- strict allow-listing of tables in SQL execution
- read-only validation for generated SQL
- blocked operations for write statements
- system prompt rules that discourage guessing
- result summarization to keep answers short and business-focused

## 13. Current Project Status

The repository currently includes:

- an intelligent shop assistant
- a database-driven analytics layer
- a forecasting API
- a Streamlit interface
- supporting test coverage

It is suitable for a small-store operational assistant and can be extended with more product intelligence, inventory alerts, purchase-order creation, and richer analytics dashboards.

## 14. Development Roadmap

Potential future improvements include:

- better database schema initialization scripts
- product category analytics
- supplier performance tracking
- automatic low-stock alerts
- richer charts and KPIs
- deployment via Docker or cloud hosting

## 15. Summary

This project combines AI, data, and retail operations into a practical business tool. It lets a shopkeeper interact with their sales and inventory using natural language while also retrieving demand forecasts and reorder guidance from a trained ML model.
