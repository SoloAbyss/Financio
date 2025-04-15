import json
import os
import uuid
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta # More robust for adding months/years

DATA_FILE = "financio_data.json"

# --- Helper Functions ---

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_float_input(prompt):
    """Gets valid float input from the user."""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_date_input(prompt):
    """Gets valid date input from the user (YYYY-MM-DD)."""
    while True:
        try:
            date_str = input(f"{prompt} (YYYY-MM-DD): ")
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def format_currency(amount):
    """Formats a float as currency."""
    return f"${amount:,.2f}"

# --- Financio Core Class ---

class FinancioApp:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.data = self._load_data()
        self._process_recurring_transactions() # Process on startup

    def _load_data(self):
        """Loads data from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                loaded_data = json.load(f)
                # Convert date strings back to date objects
                for t in loaded_data.get('transactions', []):
                    t['date'] = datetime.fromisoformat(t['date']).date()
                for rt in loaded_data.get('recurring_transactions', []):
                    rt['next_due_date'] = datetime.fromisoformat(rt['next_due_date']).date()
                    if rt.get('last_processed_date'):
                         rt['last_processed_date'] = datetime.fromisoformat(rt['last_processed_date']).date()
                for g in loaded_data.get('goals', []):
                     if g.get('deadline'):
                         g['deadline'] = datetime.fromisoformat(g['deadline']).date()
                return loaded_data
        except (FileNotFoundError, json.JSONDecodeError):
            print("Data file not found or invalid. Starting with empty data.")
            # Default structure
            return {
                "income": 0.0, # User's primary income (e.g., monthly)
                "transactions": [],
                "recurring_transactions": [],
                "accounts": { # Track loans, credit cards, bank accounts
                    # Example: "Chase Checking": {"type": "bank", "balance": 1000.00},
                    # Example: "Visa Card": {"type": "credit_card", "balance": -500.00, "limit": 5000},
                    # Example: "Student Loan": {"type": "loan", "balance": -10000.00, "principal": 15000}
                },
                "budget": { # Category: amount per period (e.g., month)
                    # Example: "Groceries": 400.00, "Rent": 1200.00
                },
                "goals": [
                    # Example: {"id": "g1", "name": "Emergency Fund", "target": 1000.00, "current": 150.00, "deadline": None}
                ],
                "badges": [] # List of strings representing earned badges
            }

    def _save_data(self):
        """Saves the current data state to the JSON file."""
        try:
            # Create a deep copy to avoid modifying original data during serialization
            data_to_save = json.loads(json.dumps(self.data, default=str)) # Convert dates etc to strings

            # Explicitly format dates as ISO strings before saving
            for t in data_to_save.get('transactions', []):
                if isinstance(t.get('date'), date):
                    t['date'] = t['date'].isoformat()
            for rt in data_to_save.get('recurring_transactions', []):
                 if isinstance(rt.get('next_due_date'), date):
                    rt['next_due_date'] = rt['next_due_date'].isoformat()
                 if isinstance(rt.get('last_processed_date'), date):
                    rt['last_processed_date'] = rt['last_processed_date'].isoformat()
            for g in data_to_save.get('goals', []):
                if isinstance(g.get('deadline'), date):
                    g['deadline'] = g['deadline'].isoformat()


            with open(self.data_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")
        except TypeError as e:
             print(f"Error preparing data for saving (serialization issue): {e}")


    # --- Core Feature Methods ---

    def log_transaction(self, is_recurring=False):
        """Logs a new income or expense transaction."""
        print("\n--- Log New Transaction ---")
        ttype = input("Type (income/expense): ").lower()
        if ttype not in ['income', 'expense']:
            print("Invalid type.")
            return

        amount = get_float_input("Amount: ")
        category = input("Category (e.g., Groceries, Salary, Rent): ")
        description = input("Description (optional): ")
        trans_date = get_date_input("Date")
        account_name = input("Affect Account (leave blank if none, e.g. 'Chase Checking', 'Visa Card'): ")

        if account_name and account_name not in self.data['accounts']:
             print(f"Account '{account_name}' not found. Transaction not linked to account.")
             account_name = None # Don't link if it doesn't exist


        transaction = {
            "id": str(uuid.uuid4()), # Unique ID
            "type": ttype,
            "amount": amount,
            "category": category,
            "description": description,
            "date": trans_date,
            "account_name": account_name
        }

        self.data['transactions'].append(transaction)

        # Update account balance if linked
        if account_name:
            acc = self.data['accounts'][account_name]
            if ttype == 'income':
                acc['balance'] += amount
                print(f"Income added. Account '{account_name}' balance updated to {format_currency(acc['balance'])}")
            elif ttype == 'expense':
                acc['balance'] -= amount # Balance decreases for expenses/payments
                print(f"Expense added. Account '{account_name}' balance updated to {format_currency(acc['balance'])}")

        self._save_data()
        print("Transaction logged successfully.")


    def add_recurring_transaction(self):
        """Adds a new recurring transaction rule."""
        print("\n--- Add Recurring Transaction ---")
        ttype = input("Type (income/expense): ").lower()
        if ttype not in ['income', 'expense']:
            print("Invalid type.")
            return

        amount = get_float_input("Amount: ")
        category = input("Category: ")
        description = input("Description (optional): ")
        frequency = input("Frequency (daily/weekly/monthly/yearly): ").lower()
        if frequency not in ['daily', 'weekly', 'monthly', 'yearly']:
            print("Invalid frequency.")
            return
        start_date = get_date_input("First occurrence date")
        account_name = input("Affect Account (leave blank if none): ")
        if account_name and account_name not in self.data['accounts']:
             print(f"Account '{account_name}' not found. Recurring transaction will not be linked.")
             account_name = None


        recurring_trans = {
            "id": str(uuid.uuid4()), # Unique ID for the rule
            "type": ttype,
            "amount": amount,
            "category": category,
            "description": description,
            "frequency": frequency,
            "next_due_date": start_date,
            "account_name": account_name,
            "last_processed_date": None # Track last processing
        }
        self.data['recurring_transactions'].append(recurring_trans)
        self._save_data()
        print("Recurring transaction rule added.")

    def _process_recurring_transactions(self):
        """Checks and processes recurring transactions that are due."""
        today = date.today()
        processed_count = 0
        for rt in self.data['recurring_transactions']:
            # Ensure dates are date objects
            if isinstance(rt['next_due_date'], str):
                 rt['next_due_date'] = datetime.fromisoformat(rt['next_due_date']).date()
            if rt.get('last_processed_date') and isinstance(rt['last_processed_date'], str):
                 rt['last_processed_date'] = datetime.fromisoformat(rt['last_processed_date']).date()


            # Process if due date is today or in the past AND not processed today already
            if rt['next_due_date'] <= today and rt.get('last_processed_date') != today:
                print(f"Processing recurring transaction: {rt['category']} ({format_currency(rt['amount'])})")

                # Create the actual transaction
                transaction = {
                    "id": str(uuid.uuid4()),
                    "type": rt['type'],
                    "amount": rt['amount'],
                    "category": rt['category'],
                    "description": f"(Recurring) {rt['description']}",
                    "date": rt['next_due_date'], # Log with the due date
                    "account_name": rt.get('account_name'),
                    "recurring_id": rt['id'] # Link back to the rule
                }
                self.data['transactions'].append(transaction)
                processed_count += 1

                # Update account balance if linked
                account_name = rt.get('account_name')
                if account_name and account_name in self.data['accounts']:
                    acc = self.data['accounts'][account_name]
                    if rt['type'] == 'income':
                        acc['balance'] += rt['amount']
                    elif rt['type'] == 'expense':
                        acc['balance'] -= rt['amount']


                # Calculate the next due date
                current_due = rt['next_due_date']
                if rt['frequency'] == 'daily':
                    rt['next_due_date'] = current_due + timedelta(days=1)
                elif rt['frequency'] == 'weekly':
                    rt['next_due_date'] = current_due + timedelta(weeks=1)
                elif rt['frequency'] == 'monthly':
                     # Use relativedelta for month additions to handle month ends correctly
                    rt['next_due_date'] = current_due + relativedelta(months=1)
                elif rt['frequency'] == 'yearly':
                     rt['next_due_date'] = current_due + relativedelta(years=1)

                rt['last_processed_date'] = today # Mark as processed today

        if processed_count > 0:
            self._save_data()
            print(f"Processed {processed_count} recurring transactions.")
        # No need to print if none were processed on startup

    def view_transactions(self):
        """Displays logged transactions."""
        print("\n--- All Transactions ---")
        if not self.data['transactions']:
            print("No transactions logged yet.")
            return

        # Sort by date, most recent first
        sorted_transactions = sorted(self.data['transactions'], key=lambda t: t['date'], reverse=True)

        for t in sorted_transactions:
            amount_str = format_currency(t['amount'])
            indicator = "+" if t['type'] == 'income' else "-"
            account_info = f" (Account: {t['account_name']})" if t.get('account_name') else ""
            print(f"{t['date']} | {t['type'].capitalize():<8} | {indicator}{amount_str:<12} | {t['category']:<20} | {t.get('description', '')}{account_info}")

    def set_income(self):
        """Sets the user's periodic income (e.g., monthly)."""
        print("\n--- Set Periodic Income ---")
        print(f"Current periodic income set to: {format_currency(self.data.get('income', 0.0))}")
        new_income = get_float_input("Enter new periodic income amount (e.g., monthly salary): ")
        self.data['income'] = new_income
        self._save_data()
        print("Income updated.")

    def calculate_budget_status(self, period_start=None, period_end=None):
        """Calculates budget surplus or deficit for a given period."""
        print("\n--- Budget Status ---")
        user_income = self.data.get('income', 0.0)
        if user_income <= 0:
            print("Income not set. Please set your periodic income first (Option 7).")
            # Optionally, calculate based on logged income transactions instead
            # user_income = sum(t['amount'] for t in self.data['transactions'] if t['type'] == 'income' and period_start <= t['date'] <= period_end)

        if not period_start or not period_end:
             # Default to current month if no period specified
            today = date.today()
            period_start = today.replace(day=1)
            period_end = (period_start + relativedelta(months=1)) - timedelta(days=1)
            print(f"(Calculating for {period_start.strftime('%B %Y')})")


        total_expenses = sum(t['amount'] for t in self.data['transactions']
                             if t['type'] == 'expense' and period_start <= t['date'] <= period_end)

        print(f"Periodic Income Set: {format_currency(user_income)}")
        print(f"Total Expenses ({period_start} to {period_end}): {format_currency(total_expenses)}")

        difference = user_income - total_expenses
        if difference >= 0:
            print(f"Budget Surplus: {format_currency(difference)}")
            status = "Surplus"
        else:
            print(f"Budget Deficit: {format_currency(abs(difference))}")
            status = "Deficit"
        return status, difference


    def manage_accounts(self):
        """Menu for managing accounts (view, add, maybe update/delete)."""
        while True:
            print("\n--- Manage Accounts ---")
            print("1. View Accounts")
            print("2. Add Account")
            # Add options for update/delete later if needed
            print("0. Back to Main Menu")
            choice = input("Choose option: ")

            if choice == '1':
                self.view_accounts()
            elif choice == '2':
                self.add_account()
            elif choice == '0':
                break
            else:
                print("Invalid choice.")

    def view_accounts(self):
        """Displays details of all accounts."""
        print("\n--- Account Balances ---")
        if not self.data['accounts']:
            print("No accounts set up yet.")
            return

        for name, details in self.data['accounts'].items():
            balance_str = format_currency(details['balance'])
            type_str = details.get('type', 'Unknown').capitalize()
            extra_info = ""
            if details.get('type') == 'credit_card':
                limit = details.get('limit')
                extra_info = f" (Limit: {format_currency(limit)})" if limit else ""
                # Available credit calculation could be added
            elif details.get('type') == 'loan':
                 principal = details.get('principal')
                 extra_info = f" (Original: {format_currency(principal)})" if principal else ""

            print(f"- {name} ({type_str}): {balance_str}{extra_info}")


    def add_account(self):
        """Adds a new bank, credit card, or loan account."""
        print("\n--- Add New Account ---")
        name = input("Account Name (e.g., Chase Checking, Visa Card): ")
        if name in self.data['accounts']:
            print("An account with this name already exists.")
            return

        acc_type = input("Account Type (bank/credit_card/loan): ").lower()
        if acc_type not in ['bank', 'credit_card', 'loan']:
            print("Invalid account type.")
            return

        balance = get_float_input("Current Balance: ")
        limit = None
        principal = None

        if acc_type == 'credit_card':
            limit_input = input("Credit Limit (optional, press Enter to skip): ")
            if limit_input:
                try:
                    limit = float(limit_input)
                except ValueError:
                    print("Invalid limit amount, skipping.")
            # Convention: Credit card balances are often negative (money owed)
            if balance > 0:
                 print("Note: Credit card balances are typically entered as negative numbers.")

        elif acc_type == 'loan':
             principal_input = input("Original Loan Amount (Principal) (optional): ")
             if principal_input:
                  try:
                      principal = float(principal_input)
                  except ValueError:
                      print("Invalid principal amount, skipping.")
            # Convention: Loan balances are typically negative (money owed)
             if balance > 0:
                 print("Note: Loan balances are typically entered as negative numbers.")


        self.data['accounts'][name] = {
            "type": acc_type,
            "balance": balance
        }
        if limit is not None:
            self.data['accounts'][name]['limit'] = limit
        if principal is not None:
             self.data['accounts'][name]['principal'] = principal

        self._save_data()
        print(f"Account '{name}' added successfully.")


    def manage_budget(self):
        """Menu for managing budget categories."""
        while True:
            print("\n--- Manage Budget ---")
            print("1. View Budget")
            print("2. Set/Update Budget Category")
            print("3. Compare Budget vs Actual Spending (Current Month)")
            print("0. Back to Main Menu")
            choice = input("Choose option: ")

            if choice == '1':
                self.view_budget()
            elif choice == '2':
                self.set_budget_category()
            elif choice == '3':
                self.compare_budget_vs_actual()
            elif choice == '0':
                break
            else:
                print("Invalid choice.")

    def view_budget(self):
        """Displays the current budget setup."""
        print("\n--- Current Budget ---")
        if not self.data['budget']:
            print("No budget categories defined yet.")
            return
        for category, amount in self.data['budget'].items():
            print(f"- {category}: {format_currency(amount)}")

    def set_budget_category(self):
        """Sets or updates the budgeted amount for a category."""
        print("\n--- Set Budget Category ---")
        category = input("Category Name: ")
        amount = get_float_input(f"Budgeted Amount for {category}: ")
        self.data['budget'][category] = amount
        self._save_data()
        print(f"Budget for '{category}' set to {format_currency(amount)}.")

    def compare_budget_vs_actual(self, period_start=None, period_end=None):
         """Compares budgeted amounts vs actual spending for categories."""
         print("\n--- Budget vs Actual Comparison ---")

         if not period_start or not period_end:
             # Default to current month
             today = date.today()
             period_start = today.replace(day=1)
             period_end = (period_start + relativedelta(months=1)) - timedelta(days=1)
             print(f"(Comparing for {period_start.strftime('%B %Y')})")

         # Calculate actual spending per category for the period
         actual_spending = {}
         for t in self.data['transactions']:
             if t['type'] == 'expense' and period_start <= t['date'] <= period_end:
                 actual_spending[t['category']] = actual_spending.get(t['category'], 0) + t['amount']

         if not self.data['budget'] and not actual_spending:
              print("No budget set and no spending recorded for this period.")
              return

         print("\n{:<20} | {:<15} | {:<15} | {:<15}".format("Category", "Budgeted", "Spent", "Difference"))
         print("-" * 70)

         all_categories = set(self.data['budget'].keys()) | set(actual_spending.keys())

         total_budgeted = 0
         total_spent = 0

         for category in sorted(list(all_categories)):
             budgeted = self.data['budget'].get(category, 0.0)
             spent = actual_spending.get(category, 0.0)
             difference = budgeted - spent
             diff_str = format_currency(difference)
             if difference < 0:
                  diff_str = f"({format_currency(abs(difference))})" # Indicate overspending

             print("{:<20} | {:<15} | {:<15} | {:<15}".format(
                 category,
                 format_currency(budgeted),
                 format_currency(spent),
                 diff_str
             ))
             total_budgeted += budgeted
             total_spent += spent

         print("-" * 70)
         total_diff = total_budgeted - total_spent
         total_diff_str = format_currency(total_diff)
         if total_diff < 0:
             total_diff_str = f"({format_currency(abs(total_diff))})"
         print("{:<20} | {:<15} | {:<15} | {:<15}".format(
                 "TOTALS",
                 format_currency(total_budgeted),
                 format_currency(total_spent),
                 total_diff_str
         ))
         print("-" * 70)


    def manage_goals(self):
         """Menu for managing savings goals."""
         while True:
            print("\n--- Manage Savings Goals ---")
            print("1. View Goals")
            print("2. Add New Goal")
            print("3. Contribute to Goal")
            print("4. View Badges")
            print("0. Back to Main Menu")
            choice = input("Choose option: ")

            if choice == '1':
                self.view_goals()
            elif choice == '2':
                self.add_goal()
            elif choice == '3':
                self.contribute_to_goal()
            elif choice == '4':
                 self.view_badges()
            elif choice == '0':
                break
            else:
                print("Invalid choice.")

    def view_goals(self):
        """Displays current savings goals and progress."""
        print("\n--- Savings Goals ---")
        if not self.data['goals']:
            print("No savings goals set yet.")
            return

        for i, goal in enumerate(self.data['goals']):
            name = goal['name']
            target = goal['target']
            current = goal['current']
            progress = (current / target) * 100 if target > 0 else 100
            deadline_str = f" (Deadline: {goal['deadline']})" if goal.get('deadline') else ""
            print(f"{i+1}. {name}: {format_currency(current)} / {format_currency(target)} ({progress:.1f}%){deadline_str}")

    def add_goal(self):
         """Adds a new savings goal."""
         print("\n--- Add New Savings Goal ---")
         name = input("Goal Name (e.g., Emergency Fund, Vacation): ")
         target = get_float_input("Target Amount: ")
         current = get_float_input("Current Amount Saved Towards Goal: ")
         deadline_str = input("Deadline (YYYY-MM-DD, optional, press Enter to skip): ")
         deadline = None
         if deadline_str:
             try:
                 deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
             except ValueError:
                 print("Invalid date format. Deadline not set.")

         goal = {
             "id": str(uuid.uuid4()),
             "name": name,
             "target": target,
             "current": current,
             "deadline": deadline
         }
         self.data['goals'].append(goal)
         self._check_goal_completion(goal) # Check immediate completion
         self._save_data()
         print(f"Goal '{name}' added.")

    def contribute_to_goal(self):
        """Adds funds towards a specific goal."""
        print("\n--- Contribute to Goal ---")
        self.view_goals()
        if not self.data['goals']:
            return

        try:
            choice = int(input("Enter the number of the goal to contribute to: ")) - 1
            if 0 <= choice < len(self.data['goals']):
                goal = self.data['goals'][choice]
                amount = get_float_input(f"Amount to contribute to '{goal['name']}': ")
                if amount <= 0:
                     print("Contribution amount must be positive.")
                     return

                goal['current'] += amount
                print(f"Contributed {format_currency(amount)} to '{goal['name']}'. New total: {format_currency(goal['current'])}")

                # Optional: Log a corresponding *expense* transaction to track where the money came from
                log_expense = input("Log this contribution as an expense transaction? (y/n): ").lower()
                if log_expense == 'y':
                    print("Logging expense for goal contribution...")
                    # You might want more details like which account it came from
                    expense_trans = {
                        "id": str(uuid.uuid4()),
                        "type": "expense",
                        "amount": amount,
                        "category": "Savings Goal", # Or specific goal name
                        "description": f"Contribution to goal: {goal['name']}",
                        "date": date.today(),
                        "account_name": input("From which account? (leave blank if none): ") or None
                    }
                     # Validate account if entered
                    if expense_trans["account_name"] and expense_trans["account_name"] not in self.data['accounts']:
                         print(f"Account '{expense_trans['account_name']}' not found. Not linking.")
                         expense_trans["account_name"] = None

                    self.data['transactions'].append(expense_trans)

                     # Update account balance if linked
                    if expense_trans["account_name"]:
                         acc = self.data['accounts'][expense_trans["account_name"]]
                         acc['balance'] -= amount
                         print(f"Account '{expense_trans['account_name']}' balance updated to {format_currency(acc['balance'])}")

                self._check_goal_completion(goal)
                self._save_data()

            else:
                print("Invalid goal number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


    def _check_goal_completion(self, goal):
        """Checks if a goal is completed and awards a badge if needed."""
        if goal['current'] >= goal['target']:
            badge_name = f"Goal Achieved: {goal['name']}!"
            if badge_name not in self.data['badges']:
                print(f"\n******************************")
                print(f"Congratulations! You reached your goal: {goal['name']}")
                print(f"Badge Earned: {badge_name}")
                print(f"******************************")
                self.data['badges'].append(badge_name)
                # Optionally remove completed goal or mark as completed
                # goal['completed'] = True # Add a completed flag
                # self._save_data() # Save immediately after badge award


    def view_badges(self):
        """Displays earned badges."""
        print("\n--- Earned Badges & Rewards ---")
        if not self.data['badges']:
            print("No badges earned yet. Keep working towards your goals!")
        else:
            for badge in self.data['badges']:
                print(f"- {badge} ⭐")

    def show_dashboard(self):
        """Displays a summary dashboard."""
        clear_screen()
        print("========== Financio Dashboard ==========")

        # 1. Account Summary
        print("\n--- Accounts ---")
        self.view_accounts() # Re-use existing view function

        # 2. Budget Status (Current Month)
        print("\n--- Budget Status (Current Month) ---")
        self.calculate_budget_status() # Re-use existing function

        # 3. Recent Transactions (Last 5)
        print("\n--- Recent Transactions ---")
        if not self.data['transactions']:
            print("No transactions yet.")
        else:
            # Sort by date, most recent first
            sorted_transactions = sorted(self.data['transactions'], key=lambda t: t['date'], reverse=True)
            for t in sorted_transactions[:5]: # Show last 5
                amount_str = format_currency(t['amount'])
                indicator = "+" if t['type'] == 'income' else "-"
                print(f"{t['date']} | {indicator}{amount_str:<10} | {t['category']}")

         # 4. Goal Progress Summary
        print("\n--- Goal Progress ---")
        if not self.data['goals']:
            print("No goals set.")
        else:
             for goal in self.data['goals']:
                target = goal['target']
                current = goal['current']
                progress = (current / target) * 100 if target > 0 else 100
                print(f"- {goal['name']}: {format_currency(current)} / {format_currency(target)} ({progress:.1f}%)")


        # 5. Upcoming Recurring Transactions (Next 5 due)
        print("\n--- Upcoming Recurring Transactions ---")
        upcoming = sorted([rt for rt in self.data['recurring_transactions']], key=lambda rt: rt['next_due_date'])
        if not upcoming:
            print("No recurring transactions scheduled.")
        else:
            for rt in upcoming[:5]: # Show next 5
                print(f"{rt['next_due_date']} | {rt['category']} ({format_currency(rt['amount'])}) - {rt['frequency']}")


        print("\n======================================")
        input("\nPress Enter to return to the main menu...")


    # --- Main Application Loop ---

    def run(self):
        """Runs the main application loop."""
        while True:
            clear_screen()
            print("======= Financio Personal Finance Manager =======")
            print("\n--- Main Menu ---")
            print("1. Show Dashboard")
            print("2. Log Transaction (Income/Expense)")
            print("3. View All Transactions")
            print("4. Manage Accounts (Bank, CC, Loan)")
            print("5. Manage Budget")
            print("6. Manage Savings Goals & Badges")
            print("7. Add Recurring Transaction Rule")
            print("8. Set/View Periodic Income")
            print("0. Exit")
            print("================================================")

            choice = input("Choose an option: ")

            if choice == '1':
                self.show_dashboard()
            elif choice == '2':
                self.log_transaction()
                input("\nPress Enter to continue...")
            elif choice == '3':
                self.view_transactions()
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.manage_accounts()
            elif choice == '5':
                self.manage_budget()
            elif choice == '6':
                self.manage_goals()
            elif choice == '7':
                self.add_recurring_transaction()
                input("\nPress Enter to continue...")
            elif choice == '8':
                self.set_income()
                input("\nPress Enter to continue...")
            elif choice == '0':
                print("Exiting Financio. Saving data...")
                self._save_data() # Ensure data is saved on exit
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

# --- Script Execution ---
if __name__ == "__main__":
    app = FinancioApp()
    app.run()