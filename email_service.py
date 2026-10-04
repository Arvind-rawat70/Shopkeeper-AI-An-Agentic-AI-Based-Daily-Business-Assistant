"""Free email-based daily report delivery for Shopkeeper AI.

This module uses Gmail SMTP and does not require a paid SMS service.
It generates a business summary and sends it to the owner by email.
"""

from __future__ import annotations

import os
import smtplib
from datetime import date, timedelta
from email.message import EmailMessage
from typing import Optional

from dotenv import load_dotenv

from database import tools as db

load_dotenv()

OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() in {"1", "true", "yes"}
EMAIL_DEBUG = os.getenv("EMAIL_DEBUG", "false").lower() in {"1", "true", "yes"}


def _money(value: Optional[float]) -> str:
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def _safe_names(items, key_name: str, max_items: int = 3) -> str:
    if not items:
        return "No items found"
    names = []
    for item in items[:max_items]:
        name = item.get(key_name)
        if name:
            names.append(str(name))
    return ", ".join(names) if names else "No items found"


def _format_items(items, key_name: str, max_items: int = 5) -> str:
    """Return a numbered list string of item names suitable for email bodies."""
    if not items:
        return "No items found"
    lines = []
    for i, item in enumerate(items[:max_items], start=1):
        name = item.get(key_name) if isinstance(item, dict) else str(item)
        if name:
            lines.append(f"{i}. {name}")
    return "\n".join(lines) if lines else "No items found"


def build_daily_report(report_type: str = "morning") -> str:
    """Create a human-friendly business summary string for email delivery."""
    end_date = date.today()
    start_date = end_date - timedelta(days=1)

    try:
        revenue_info = db.get_revenue_and_profit(start_date, end_date)
        revenue = float(revenue_info.get("revenue", 0) or 0)
        expenses = float(revenue_info.get("expenses", 0) or 0)
        profit = float(revenue_info.get("estimated_profit", 0) or 0)
    except Exception:
        revenue, expenses, profit = 0.0, 0.0, 0.0

    try:
        low_stock = db.get_low_stock_products(20)
    except Exception:
        low_stock = []

    try:
        top_items = db.get_best_selling_products(start_date, end_date, limit=3)
    except Exception:
        top_items = []

    low_stock_names = _safe_names(low_stock, "name")
    top_item_names = _safe_names(top_items, "name")

    greeting = (
        "Hey there — good morning!"
        if report_type.lower() == "morning"
        else "Hey there — good evening!"
    )

    header = f"{greeting}\nHere's your Shopkeeper AI summary for {start_date} to {end_date}."

    highlights = (
        f"\n\nHighlights:\n"
        f"- Revenue: {_money(revenue)}\n"
        f"- Expenses: {_money(expenses)}\n"
        f"- Estimated profit: {_money(profit)}\n"
    )

    top_section = "\nTop-selling products:\n" + (_format_items(top_items, "name") or "No items found")
    low_section = "\n\nLow stock (please restock soon):\n" + (_format_items(low_stock, "name") or "No items found")

    actions = (
        "\n\nQuick actions:\n"
        "- Review low-stock items and reorder where needed.\n"
        "- Consider promotions for top-selling products.\n"
    )

    footer = "\nHave a great day!\n— Shopkeeper AI"

    return header + highlights + top_section + low_section + actions + footer


def send_email(subject: str, body: str, to_email: Optional[str] = None):
    """Send a plain-text email using Gmail SMTP.

    Required env vars:
        EMAIL_SENDER, EMAIL_PASSWORD, OWNER_EMAIL

    Gmail note:
    - App password is required if 2-Step Verification is enabled.
    - Use an app-specific password from Google account security settings.
    """
    recipient = to_email or OWNER_EMAIL
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, recipient]):
        raise ValueError(
            "Missing email configuration. Set EMAIL_SENDER, EMAIL_PASSWORD, "
            "and OWNER_EMAIL in your .env file."
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = EMAIL_SENDER
    message["To"] = recipient
    message.set_content(body)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_DEBUG:
                server.set_debuglevel(1)
            if EMAIL_USE_TLS:
                server.starttls()
            try:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            except smtplib.SMTPAuthenticationError as exc:
                raise ValueError(
                    "SMTP authentication failed. Verify EMAIL_SENDER and EMAIL_PASSWORD; "
                    "if using Gmail enable 2-Step Verification and use an app password. "
                    "See: https://support.google.com/mail/?p=BadCredentials"
                ) from exc
            server.send_message(message)
    except smtplib.SMTPServerDisconnected as exc:
        raise ConnectionError(
            "SMTP server disconnected unexpectedly. Check network, host/port, and TLS settings."
        ) from exc
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"SMTP error sending email: {exc}") from exc

    return True


def send_morning_report():
    body = build_daily_report(report_type="morning")
    return send_email("Shopkeeper AI - Morning Business Report", body)


def send_evening_report():
    body = build_daily_report(report_type="evening")
    return send_email("Shopkeeper AI - Evening Business Report", body)


if __name__ == "__main__":
    print(build_daily_report("morning"))
