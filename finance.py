"""Small, reusable finance functions for the command-line tracker.

Money is stored as text in JSON, then converted to Decimal for calculations.
This avoids common floating-point problems with pounds and pence.
"""

import csv
import json
import os
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA_FILE = Path(os.environ.get(
    "FINANCE_TRACKER_DATA",
    Path(__file__).resolve().parent / "data" / "transactions.json",
))
PENNY = Decimal("0.01")


def parse_amount(value):
    """Return a positive monetary amount with no more than two decimal places."""
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError("Enter a number, e.g. 12.50.") from None
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    try:
        rounded = amount.quantize(PENNY)
    except InvalidOperation:
        raise ValueError("Amount is too large.") from None
    if amount != rounded:
        raise ValueError("Use no more than two decimal places.")
    return rounded


def format_money(amount):
    return f"£{amount:,.2f}"


def check_date(value):
    """Check the entered date and return it in YYYY-MM-DD form."""
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.") from None


def check_month(value):
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise ValueError("Month must be in YYYY-MM format, e.g. 2026-10.")
    return value


def load_transactions(path=DATA_FILE):
    path = Path(path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read {path}: {error}") from error
    if not isinstance(data, list):
        raise ValueError("Saved data must contain a list of transactions.")
    required = {"id", "date", "type", "amount", "category", "note"}
    if any(not isinstance(item, dict) or not required.issubset(item) for item in data):
        raise ValueError("Saved transactions have an unexpected format.")
    return data


def save_transactions(transactions, path=DATA_FILE):
    """Save via a temporary file, to reduce the risk of losing data."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(transactions, indent=2), encoding="utf-8")
    temporary.replace(path)


def add_transaction(transactions, kind, amount, category, note="", when=None):
    if kind not in ("income", "expense"):
        raise ValueError("Type must be income or expense.")
    amount = parse_amount(amount)
    category = category.strip()
    if not category:
        raise ValueError("Please enter a category.")
    transaction = {
        "id": max((item["id"] for item in transactions), default=0) + 1,
        "date": check_date(when) if when else date.today().isoformat(),
        "type": kind,
        "amount": str(amount),
        "category": category.title(),
        "note": note.strip(),
    }
    transactions.append(transaction)
    return transaction


def get_transaction(transactions, transaction_id):
    return next((item for item in transactions if item["id"] == transaction_id), None)


def update_transaction(transactions, transaction_id, **changes):
    item = get_transaction(transactions, transaction_id)
    if item is None:
        raise ValueError(f"Transaction #{transaction_id} was not found.")
    updated = item.copy()
    if "kind" in changes:
        if changes["kind"] not in ("income", "expense"):
            raise ValueError("Type must be income or expense.")
        updated["type"] = changes["kind"]
    if "amount" in changes:
        updated["amount"] = str(parse_amount(changes["amount"]))
    if "category" in changes:
        category = changes["category"].strip()
        if not category:
            raise ValueError("Category cannot be empty.")
        updated["category"] = category.title()
    if "note" in changes:
        updated["note"] = changes["note"].strip()
    if "when" in changes:
        updated["date"] = check_date(changes["when"])
    item.update(updated)
    return item


def delete_transaction(transactions, transaction_id):
    item = get_transaction(transactions, transaction_id)
    if item is None:
        return False
    transactions.remove(item)
    return True


def sorted_transactions(transactions):
    return sorted(transactions, key=lambda item: (item["date"], item["id"]), reverse=True)


def calculate_totals(transactions):
    income = sum((Decimal(item["amount"]) for item in transactions
                  if item["type"] == "income"), Decimal("0.00"))
    expenses = sum((Decimal(item["amount"]) for item in transactions
                    if item["type"] == "expense"), Decimal("0.00"))
    return income, expenses, income - expenses


def month_transactions(transactions, month):
    check_month(month)
    return [item for item in transactions if item["date"].startswith(month + "-")]


def expenses_by_category(transactions):
    categories = {}
    for item in transactions:
        if item["type"] == "expense":
            category = item["category"]
            categories[category] = categories.get(category, Decimal("0.00")) + Decimal(item["amount"])
    return sorted(categories.items(), key=lambda pair: (-pair[1], pair[0]))


def export_csv(transactions, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Date", "Type", "Amount (GBP)", "Category", "Note"])
        for item in sorted_transactions(transactions):
            writer.writerow([item["id"], item["date"], item["type"],
                             item["amount"], item["category"], item["note"]])
    return path
