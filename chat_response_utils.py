"""Helpers for producing concise business answers from query results."""

from __future__ import annotations

import pandas as pd


def _to_lower_text(value):
    return (value or "").strip().lower()


def _pick_column(columns, preferred_names):
    for column in columns:
        normalized = _to_lower_text(column).replace(" ", "_")
        if normalized in preferred_names:
            return column
    for column in columns:
        normalized = _to_lower_text(column).replace(" ", "_")
        for name in preferred_names:
            if name in normalized:
                return column
    return None


def build_direct_business_answer(question, result_df):
    """Return a deterministic, concise answer for single-target stock questions."""
    q = _to_lower_text(question)
    if result_df is None or result_df.empty:
        return "No matching records were found."

    asks_for_lowest_stock = (
        ("lowest" in q or "least" in q or "minimum" in q or "min" in q)
        and ("stock" in q or "inventory" in q or "quantity" in q)
        and ("name" in q or "product" in q or "item" in q)
    )

    if not asks_for_lowest_stock:
        return None

    name_col = _pick_column(result_df.columns, {"name", "product_name", "product", "item"})
    stock_col = _pick_column(
        result_df.columns,
        {"stock_quantity", "stock", "quantity", "inventory", "current_stock"},
    )

    if not name_col or not stock_col:
        return None

    df = result_df.copy()
    df[stock_col] = pd.to_numeric(df[stock_col], errors="coerce")
    df = df.dropna(subset=[stock_col])

    if df.empty:
        return "No matching records were found."

    lowest_row = df.sort_values(by=[stock_col, name_col], ascending=[True, True], na_position="last").iloc[0]
    stock_value = lowest_row[stock_col]
    if pd.isna(stock_value):
        return "No matching records were found."

    stock_display = int(stock_value) if float(stock_value).is_integer() else float(stock_value)
    return (
        f"The product with the lowest stock right now is {lowest_row[name_col]}, "
        f"with {stock_display} units currently in stock."
    )
