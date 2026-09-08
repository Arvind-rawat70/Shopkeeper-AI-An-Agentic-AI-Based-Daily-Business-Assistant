"""
database/tools.py

Reusable, "dumb" database-access functions for Shopkeeper AI.

These functions contain NO agent/LLM logic — they only read/write data
and return plain Python dicts/lists. LangGraph agents will later call
these as tools; the agent decides *when* to call them, not this file.
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from datetime import date

load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")

missing = [k for k in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
           if not os.getenv(k)]

if missing:
    raise EnvironmentError(
        f"Missing environment variables: {', '.join(missing)}"
    )

db_password_quoted = quote_plus(db_password)

database_url = (
    f"mysql+pymysql://{db_user}:{db_password_quoted}"
    f"@{db_host}/{db_name}"
)

engine = create_engine(database_url, pool_pre_ping=True)


def _rows_to_dicts(result):
    """Convert a SQLAlchemy CursorResult into a list of plain dicts."""
    return [dict(row._mapping) for row in result]


# ---------------------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------------------

def get_all_products():
    """Return all products with their current stock."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM products"))
        return _rows_to_dicts(result)


def get_product_by_name(name: str):
    """Fetch a single product's details by (partial, case-insensitive) name."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE name LIKE :name"),
            {"name": f"%{name}%"},
        )
        return _rows_to_dicts(result)


def get_low_stock_products(threshold: int = 20):
    """Return products where stock_quantity is below the given threshold."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM products WHERE stock_quantity < :threshold"),
            {"threshold": threshold},
        )
        return _rows_to_dicts(result)


def update_stock(product_id: int, new_quantity: int):
    """Set a product's stock_quantity to a new value. Returns rows affected."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "UPDATE products SET stock_quantity = :qty "
                "WHERE product_id = :pid"
            ),
            {"qty": new_quantity, "pid": product_id},
        )
        connection.commit()
        return result.rowcount


# ---------------------------------------------------------------------
# SALES
# ---------------------------------------------------------------------

def add_sale(product_id: int, quantity: int, sale_price: float, sale_date: date = None):
    """Insert a new sale record. Defaults sale_date to today if not given."""
    sale_date = sale_date or date.today()
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "INSERT INTO sales (product_id, quantity, sale_price, sale_date) "
                "VALUES (:pid, :qty, :price, :sdate)"
            ),
            {"pid": product_id, "qty": quantity, "price": sale_price, "sdate": sale_date},
        )
        connection.commit()
        return result.rowcount


def get_sales_by_date_range(start_date: date, end_date: date):
    """Return all sales between start_date and end_date (inclusive)."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT * FROM sales "
                "WHERE sale_date BETWEEN :start AND :end "
                "ORDER BY sale_date"
            ),
            {"start": start_date, "end": end_date},
        )
        return _rows_to_dicts(result)


def get_best_selling_products(start_date: date, end_date: date, limit: int = 5):
    """Return the top-selling products (by quantity) within a date range."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT p.product_id, p.name, SUM(s.quantity) AS total_sold "
                "FROM sales s "
                "JOIN products p ON p.product_id = s.product_id "
                "WHERE s.sale_date BETWEEN :start AND :end "
                "GROUP BY p.product_id, p.name "
                "ORDER BY total_sold DESC "
                "LIMIT :limit"
            ),
            {"start": start_date, "end": end_date, "limit": limit},
        )
        return _rows_to_dicts(result)


def get_slow_moving_products(start_date: date, end_date: date, max_sold: int = 5):
    """Return products that sold at or below max_sold units in the date range."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT p.product_id, p.name, "
                "COALESCE(SUM(s.quantity), 0) AS total_sold "
                "FROM products p "
                "LEFT JOIN sales s ON s.product_id = p.product_id "
                "AND s.sale_date BETWEEN :start AND :end "
                "GROUP BY p.product_id, p.name "
                "HAVING total_sold <= :max_sold "
                "ORDER BY total_sold ASC"
            ),
            {"start": start_date, "end": end_date, "max_sold": max_sold},
        )
        return _rows_to_dicts(result)


# ---------------------------------------------------------------------
# EXPENSES
# ---------------------------------------------------------------------

def get_expenses_by_date_range(start_date: date, end_date: date):
    """Return all expenses between start_date and end_date (inclusive)."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT * FROM expenses "
                "WHERE expense_date BETWEEN :start AND :end "
                "ORDER BY expense_date"
            ),
            {"start": start_date, "end": end_date},
        )
        return _rows_to_dicts(result)


def add_expense(description: str, amount: float, expense_date: date = None):
    """Insert a new expense record. Defaults expense_date to today if not given."""
    expense_date = expense_date or date.today()
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "INSERT INTO expenses (description, amount, expense_date) "
                "VALUES (:desc, :amount, :edate)"
            ),
            {"desc": description, "amount": amount, "edate": expense_date},
        )
        connection.commit()
        return result.rowcount


# ---------------------------------------------------------------------
# PROFIT / REVENUE
# ---------------------------------------------------------------------

def get_revenue_and_profit(start_date: date, end_date: date):
    """
    Calculate revenue, product cost, expenses, and estimated profit
    for a date range.
    """
    with engine.connect() as connection:
        revenue_row = connection.execute(
            text(
                "SELECT COALESCE(SUM(s.quantity * s.sale_price), 0) AS revenue, "
                "COALESCE(SUM(s.quantity * p.purchase_price), 0) AS product_cost "
                "FROM sales s "
                "JOIN products p ON p.product_id = s.product_id "
                "WHERE s.sale_date BETWEEN :start AND :end"
            ),
            {"start": start_date, "end": end_date},
        ).fetchone()

        expenses_row = connection.execute(
            text(
                "SELECT COALESCE(SUM(amount), 0) AS total_expenses "
                "FROM expenses WHERE expense_date BETWEEN :start AND :end"
            ),
            {"start": start_date, "end": end_date},
        ).fetchone()

    revenue = float(revenue_row.revenue)
    product_cost = float(revenue_row.product_cost)
    total_expenses = float(expenses_row.total_expenses)
    profit = revenue - product_cost - total_expenses

    return {
        "revenue": revenue,
        "product_cost": product_cost,
        "expenses": total_expenses,
        "estimated_profit": profit,
    }


# ---------------------------------------------------------------------
# SUPPLIERS
# ---------------------------------------------------------------------

def get_supplier_for_product(product_id: int):
    """Return supplier details linked to a given product."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT sup.* FROM suppliers sup "
                "JOIN products p ON p.supplier_id = sup.supplier_id "
                "WHERE p.product_id = :pid"
            ),
            {"pid": product_id},
        )
        return _rows_to_dicts(result)


# ---------------------------------------------------------------------
# QUICK MANUAL TESTS
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("All products:")
    products = get_all_products()
    if not products:
        print("  (no products found — check DB connection/table data)")
    for p in products:
        print(" ", p)

    print("\nLow stock (< 20):")
    low_stock = get_low_stock_products(threshold=20)
    if not low_stock:
        print("  (none below threshold)")
    for p in low_stock:
        print(" ", p)

    # Your dummy data uses random dates within 2025, not today's date —
    # so we use a wide range here instead of date.today() to actually
    # pick up rows. Narrow this once you're testing with real dates.
    range_start = date(2025, 1, 1)
    range_end = date(2025, 12, 31)

    print(f"\nRevenue/profit for {range_start} to {range_end}:")
    print(" ", get_revenue_and_profit(range_start, range_end))

    print(f"\nBest selling products ({range_start} to {range_end}):")
    for p in get_best_selling_products(range_start, range_end, limit=5):
        print(" ", p)