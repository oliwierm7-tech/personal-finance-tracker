
print("Welcome to Personal Finance Tracker!")

balance = 0.0

while True:
    print("\n--- MAIN MENU ---")
    print("1. Add Income")
    print("2. Add Expense")
    print("3. View Balance")
    print("4. Exit")

    choice = input("Choose an option (1-4): ")

    if choice == "1":
        income = float(input("Enter income (£): "))
        balance += income
        print("Income added successfully!")

    elif choice == "2":
        expense = float(input("Enter expense (£): "))
        balance -= expense
        print("Expense added successfully!")

    elif choice == "3":
        print("Current balance: £", round(balance, 2))

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid option. Please try again.")
