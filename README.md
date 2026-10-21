# Personal Finance Tracker

A small command-line app built in **Python** to practise real programming concepts while keeping track of income and expenses. It runs locally and doesn't need an account, database server or third-party packages.

## Features

- Record income and expenses, with an amount, date, category and optional note.
- **Keep transactions between sessions** using a local JSON file (created on first save).
- Show your overall balance and browse your transaction history.
- View **monthly income, spending and net balance**, plus spending by category.
- Correct a mistake by editing a transaction, or delete it with confirmation.
- Export your transactions to a CSV file that opens in Excel.
- Handle invalid amounts and dates without crashing.

## Getting started

1. Install [Python 3.10+](https://www.python.org/downloads/).
2. Download or clone the repository, then open its folder in a terminal.
3. Run:

   ```bash
   python main.py
   ```

   On some computers, use `py main.py` (Windows) or `python3 main.py` (macOS/Linux).
4. Choose a menu option. No extra packages are required.

Data is saved in `data/transactions.json`. That folder is created automatically. Local transaction data and CSV exports are excluded from Git so personal financial information isn't accidentally uploaded.

### Example session

```text
--- MAIN MENU ---
Total balance: £0.00
1. Add income
2. Add expense
3. View transactions
4. Monthly summary
5. Edit a transaction
6. Delete a transaction
7. Export CSV
8. Exit
Choose an option (1-8): 1

-- Add income --
Amount (£): 500
Category (e.g. Food, Travel, Salary): Part-time job
Note (optional): Weekend shifts
Date YYYY-MM-DD (Enter for today): 2026-10-20
Saved income #1: £500.00.
```

## Project structure

```text
main.py                # Interactive menu and input prompts
finance.py             # Data storage, validation, calculations and CSV export
tests/test_finance.py   # Automated tests for the finance logic
.gitignore             # Keeps personal transaction data out of Git
data/                  # Created locally when the app is first used
```

## How it works

The original version just adjusted a single balance in memory. Closing the app lost that balance and there was no record of *what* had been added. To solve that, the program now stores **individual transactions** in JSON. It calculates balances from those records, so a corrected transaction is reflected in the totals.

A few choices worth understanding:

- **Why `Decimal`?** Ordinary Python `float` values can produce small rounding errors, so amounts are converted to `Decimal` and stored as strings with two decimal places.
- **Why separate `main.py` and `finance.py`?** The menu deals with user input; the finance functions can be tested without typing into the menu.
- **Why JSON?** It is readable and simple for a single-user beginner project. A database could be a later improvement.
- **Why a temporary file when saving?** It reduces the chance of a half-written JSON file if saving is interrupted.

### Testing

Run the included tests with Python's built-in `unittest` module:

```bash
python -m unittest discover -s tests -v
```

The tests cover calculating balances, input validation, monthly summaries, updates, deletion, saving/loading and CSV export.

## Ideas to improve later

- Set monthly spending limits and show warnings when they're exceeded.
- Add a graphical interface or a web frontend.
- Let users import transactions from CSV, not just export them.

This is a **learning project**, not banking software. It doesn't connect to real bank accounts and shouldn't be used to store sensitive credentials.
