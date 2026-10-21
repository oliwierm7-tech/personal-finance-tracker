"""Personal Finance Tracker - run this file to open the menu."""

from datetime import date

from finance import (
    DATA_FILE, add_transaction, calculate_totals, check_date, check_month,
    delete_transaction, expenses_by_category, export_csv, format_money,
    get_transaction, load_transactions, month_transactions, parse_amount,
    save_transactions, sorted_transactions, update_transaction,
)


def ask_amount(prompt="Amount (£): "):
    while True:
        answer = input(prompt).strip()
        try:
            return parse_amount(answer)
        except ValueError as error:
            print(f"Invalid amount: {error}")


def ask_category():
    while True:
        category = input("Category (e.g. Food, Travel, Salary): ").strip()
        if category:
            return category
        print("Please enter a category.")


def ask_date():
    while True:
        answer = input("Date YYYY-MM-DD (Enter for today): ").strip()
        if not answer:
            return date.today().isoformat()
        try:
            return check_date(answer)
        except ValueError as error:
            print(error)


def ask_id():
    try:
        return int(input("Transaction ID: ").strip())
    except ValueError:
        print("Enter a whole-number transaction ID.")
        return None


def add_flow(transactions, kind):
    print(f"\n-- Add {kind} --")
    amount = ask_amount()
    category = ask_category()
    note = input("Note (optional): ")
    when = ask_date()
    item = add_transaction(transactions, kind, amount, category, note, when)
    save_transactions(transactions)
    print(f"Saved {kind} #{item['id']}: {format_money(amount)}.")


def show_transactions(transactions):
    if not transactions:
        print("\nNo transactions yet. Add your first income or expense!")
        return
    print("\nID  Date        Type      Amount        Category       Note")
    print("-" * 76)
    for item in sorted_transactions(transactions):
        value = format_money(parse_amount(item["amount"]))
        print(f"{item['id']:<3} {item['date']:<10}  {item['type']:<7}  "
              f"{value:>11}   {item['category'][:14]:<14} {item['note'][:22]}")


def show_month(transactions):
    while True:
        month = input("Month YYYY-MM (Enter for current month): ").strip()
        month = month or date.today().strftime("%Y-%m")
        try:
            check_month(month)
            break
        except ValueError as error:
            print(error)
    selected = month_transactions(transactions, month)
    income, expenses, net = calculate_totals(selected)
    print(f"\n-- Summary for {month} --")
    print(f"Income:   {format_money(income)}")
    print(f"Expenses: {format_money(expenses)}")
    print(f"Net:      {format_money(net)}")
    categories = expenses_by_category(selected)
    if categories:
        print("\nSpending by category:")
        for category, amount in categories:
            print(f"  {category:<18} {format_money(amount):>12}")
    else:
        print("No expenses for this month.")


def edit_flow(transactions):
    show_transactions(transactions)
    if not transactions:
        return
    transaction_id = ask_id()
    item = get_transaction(transactions, transaction_id)
    if item is None:
        print("Transaction not found.")
        return
    print("Leave any field blank to keep its current value. Enter '-' to clear a note.")
    print(f"Editing #{item['id']} ({item['category']}, {item['amount']}).")
    kind = input(f"Type [{item['type']}] (income/expense): ").strip().lower()
    amount = input(f"Amount [{item['amount']}]: ").strip()
    category = input(f"Category [{item['category']}]: ").strip()
    note = input(f"Note [{item['note'] or '(none)'}]: ").strip()
    when = input(f"Date [{item['date']}] YYYY-MM-DD: ").strip()
    changes = {}
    if kind:
        changes["kind"] = kind
    if amount:
        changes["amount"] = amount
    if category:
        changes["category"] = category
    if note:
        changes["note"] = "" if note == "-" else note
    if when:
        changes["when"] = when
    try:
        update_transaction(transactions, transaction_id, **changes)
    except ValueError as error:
        print(f"Nothing changed: {error}")
        return
    save_transactions(transactions)
    print("Transaction updated.")


def delete_flow(transactions):
    show_transactions(transactions)
    if not transactions:
        return
    transaction_id = ask_id()
    item = get_transaction(transactions, transaction_id)
    if item is None:
        print("Transaction not found.")
        return
    answer = input(f"Delete #{transaction_id} ({item['category']}, £{item['amount']})? (y/N): ")
    if answer.strip().lower() == "y":
        delete_transaction(transactions, transaction_id)
        save_transactions(transactions)
        print("Transaction deleted.")
    else:
        print("Cancelled. Nothing was deleted.")


def main():
    try:
        transactions = load_transactions()
    except ValueError as error:
        print(f"Unable to load saved transactions: {error}")
        print("Your data was NOT overwritten. Check the JSON file or restore a backup.")
        return

    print("Welcome to Personal Finance Tracker!")
    while True:
        income, expenses, balance = calculate_totals(transactions)
        print("\n--- MAIN MENU ---")
        print(f"Total balance: {format_money(balance)}")
        print("1. Add income")
        print("2. Add expense")
        print("3. View transactions")
        print("4. Monthly summary")
        print("5. Edit a transaction")
        print("6. Delete a transaction")
        print("7. Export CSV")
        print("8. Exit")
        choice = input("Choose an option (1-8): ").strip()
        if choice == "1":
            add_flow(transactions, "income")
        elif choice == "2":
            add_flow(transactions, "expense")
        elif choice == "3":
            show_transactions(transactions)
        elif choice == "4":
            show_month(transactions)
        elif choice == "5":
            edit_flow(transactions)
        elif choice == "6":
            delete_flow(transactions)
        elif choice == "7":
            output = export_csv(transactions, DATA_FILE.parent / "transactions_export.csv")
            print(f"Exported {len(transactions)} transactions to {output}")
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 8.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
