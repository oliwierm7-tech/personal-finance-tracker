"""Tests for the finance calculations and file handling.

Run using: python -m unittest discover -s tests -v
"""

import csv
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from finance import (
    add_transaction, calculate_totals, check_date, check_month,
    delete_transaction, expenses_by_category, export_csv, load_transactions,
    month_transactions, parse_amount, save_transactions, update_transaction,
)


class FinanceTrackerTests(unittest.TestCase):
    def setUp(self):
        self.transactions = []
        add_transaction(self.transactions, "income", "1500.00", "salary", "October pay", "2026-10-02")
        add_transaction(self.transactions, "expense", "20.50", "food", "Lunch", "2026-10-03")
        add_transaction(self.transactions, "expense", "15.25", "food", "Groceries", "2026-10-04")
        add_transaction(self.transactions, "expense", "10.00", "travel", "Bus", "2026-09-29")

    def test_parsing_amounts(self):
        self.assertEqual(parse_amount("12.50"), Decimal("12.50"))
        for amount in ["-4", "0", "three", "1.999", "NaN", "Infinity", "1e999", ""]:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                parse_amount(amount)

    def test_totals_do_not_use_float_arithmetic(self):
        self.assertEqual(calculate_totals(self.transactions), (
            Decimal("1500.00"), Decimal("45.75"), Decimal("1454.25")))

    def test_monthly_summary_and_categories(self):
        october = month_transactions(self.transactions, "2026-10")
        self.assertEqual(len(october), 3)
        self.assertEqual(calculate_totals(october)[2], Decimal("1464.25"))
        self.assertEqual(expenses_by_category(october), [("Food", Decimal("35.75"))])

    def test_invalid_date_and_month(self):
        for date_text in ["2026-02-30", "23/10/2026", "2026-9-01"]:
            with self.assertRaises(ValueError):
                check_date(date_text)
        with self.assertRaises(ValueError):
            check_month("2026-13")

    def test_update_is_atomic_when_validation_fails(self):
        old = self.transactions[1].copy()
        with self.assertRaises(ValueError):
            update_transaction(self.transactions, 2, category="New", amount="not a number")
        self.assertEqual(self.transactions[1], old)
        update_transaction(self.transactions, 2, amount="18.50", note="Updated lunch")
        self.assertEqual(self.transactions[1]["amount"], "18.50")
        self.assertEqual(self.transactions[1]["note"], "Updated lunch")

    def test_delete_and_missing_record(self):
        self.assertTrue(delete_transaction(self.transactions, 3))
        self.assertFalse(delete_transaction(self.transactions, 999))
        self.assertEqual(len(self.transactions), 3)

    def test_category_and_kind_validation(self):
        with self.assertRaises(ValueError):
            add_transaction(self.transactions, "other", "5", "Food")
        with self.assertRaises(ValueError):
            add_transaction(self.transactions, "expense", "5", " ")

    def test_save_load_and_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "data" / "transactions.json"
            self.assertEqual(load_transactions(filename), [])
            save_transactions(self.transactions, filename)
            self.assertEqual(load_transactions(filename), self.transactions)
            exported = Path(folder) / "report.csv"
            export_csv(self.transactions, exported)
            with exported.open(encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["Category"], "Food")  # latest first

    def test_corrupt_file_is_not_silently_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "transactions.json"
            path.write_text("{not valid json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_transactions(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "{not valid json")


if __name__ == "__main__":
    unittest.main()
