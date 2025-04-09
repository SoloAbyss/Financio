import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budgeting App")
        self.root.geometry("600x800")
        self.root.resizable(False, False)

        # Set up styles for modern UI
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        self.style.configure('TLabel', font=('Arial', 10), padding=5)

        # Budget variables
        self.income = tk.DoubleVar(value=0.0)
        self.total_expenses = tk.DoubleVar(value=0.0)
        self.remaining_budget = tk.StringVar(value="$0.00")

        self.income_frequency = tk.StringVar(value="Monthly")
        self.budget_frequency = tk.StringVar(value="Monthly")

        self.expenses = []  # List of expense dictionaries
        self.savings_goals = []  # List of savings goal dictionaries

        # Create tabs using ttk.Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # Create three frames for tabs
        self.tab_budget = ttk.Frame(self.notebook)
        self.tab_expenses = ttk.Frame(self.notebook)
        self.tab_savings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_budget, text="Budget")
        self.notebook.add(self.tab_expenses, text="Log Expenses")
        self.notebook.add(self.tab_savings, text="Savings Goals")

        # Create widgets for all tabs
        self.create_budget_widgets()
        self.create_expenses_widgets()
        self.create_savings_widgets()

    def create_budget_widgets(self):
        ttk.Label(self.tab_budget, text="Budgeting App", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.tab_budget, text="Enter Income:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        ttk.Entry(self.tab_budget, textvariable=self.income).grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.tab_budget, text="Select Income Frequency:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        ttk.Combobox(self.tab_budget, textvariable=self.income_frequency, values=["Weekly", "Biweekly", "Monthly"], state="readonly").grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.tab_budget, text="Total Expenses:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        ttk.Label(self.tab_budget, textvariable=self.total_expenses).grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self.tab_budget, text="Remaining Budget:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        ttk.Label(self.tab_budget, textvariable=self.remaining_budget).grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(self.tab_budget, text="Select Budget Frequency:").grid(row=5, column=0, padx=10, pady=10, sticky='e')
        ttk.Combobox(self.tab_budget, textvariable=self.budget_frequency, values=["Weekly", "Biweekly", "Monthly"], state="readonly").grid(row=5, column=1, padx=10, pady=10)

        ttk.Button(self.tab_budget, text="Calculate Remaining Budget", command=self.calculate_remaining_budget).grid(row=6, column=0, columnspan=2, pady=10)

    def create_expenses_widgets(self):
        ttk.Label(self.tab_expenses, text="Log Expenses", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(self.tab_expenses, text="Payee (e.g., Netflix, McDonald's):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.payee_entry = ttk.Entry(self.tab_expenses)
        self.payee_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.tab_expenses, text="Date:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.date_entry = DateEntry(self.tab_expenses, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(self.tab_expenses, text="Set Date to Today", command=self.set_date_to_today).grid(row=2, column=2, padx=10, pady=10)

        ttk.Label(self.tab_expenses, text="Payment Frequency:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.payment_frequency = ttk.Combobox(self.tab_expenses, values=["One-time", "Weekly", "Monthly"], state="readonly")
        self.payment_frequency.grid(row=3, column=1, padx=10, pady=10)
        self.payment_frequency.set("One-time")

        ttk.Label(self.tab_expenses, text="Amount:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.amount_entry = ttk.Entry(self.tab_expenses)
        self.amount_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Button(self.tab_expenses, text="Add Expense", command=self.add_expense_details).grid(row=5, column=0, columnspan=2, pady=10)

        self.expenses_listbox = tk.Listbox(self.tab_expenses, width=50, height=10)
        self.expenses_listbox.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def create_savings_widgets(self):
        ttk.Label(self.tab_savings, text="Savings Goals", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(self.tab_savings, text="Goal Name:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.goal_name_entry = ttk.Entry(self.tab_savings)
        self.goal_name_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.tab_savings, text="Target Amount:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.target_amount_entry = ttk.Entry(self.tab_savings)
        self.target_amount_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.tab_savings, text="Target Date:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.goal_date_entry = DateEntry(self.tab_savings, date_pattern="yyyy-mm-dd")
        self.goal_date_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self.tab_savings, text="Amount Saved:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.amount_saved_entry = ttk.Entry(self.tab_savings)
        self.amount_saved_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Button(self.tab_savings, text="Add Goal", command=self.add_savings_goal).grid(row=5, column=0, columnspan=2, pady=10)

        self.savings_listbox = tk.Listbox(self.tab_savings, width=60, height=10)
        self.savings_listbox.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def set_date_to_today(self):
        self.date_entry.set_date(datetime.today())

    def add_expense_details(self):
        payee = self.payee_entry.get().strip()
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d")
        payment_frequency = self.payment_frequency.get()
        amount_str = self.amount_entry.get().strip()

        if not payee or not date_str or not payment_frequency or not amount_str:
            messagebox.showerror("Missing Information", "Please fill in all fields before adding an expense.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be a positive number.")

            expense = {'payee': payee, 'date': date_str, 'payment_frequency': payment_frequency, 'amount': amount}
            self.expenses.append(expense)

            self.expenses_listbox.insert(tk.END, f"{payee} - {date_str} - {payment_frequency} - ${amount:.2f}")

            self.payee_entry.delete(0, tk.END)
            self.date_entry.set_date(datetime.today())
            self.payment_frequency.set("One-time")
            self.amount_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")

    def calculate_remaining_budget(self):
        try:
            income = self.income.get()
            income_frequency = self.income_frequency.get()

            if income_frequency == "Weekly":
                income *= 4
            elif income_frequency == "Biweekly":
                income *= 2

            total_expenses = sum(exp['amount'] * (4 if exp['payment_frequency'] == "Weekly" else 1) for exp in self.expenses)
            remaining = income - total_expenses

            self.total_expenses.set(f"${total_expenses:.2f}")
            self.remaining_budget.set(f"${remaining:.2f}")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid income amount.")

    def add_savings_goal(self):
        goal_name = self.goal_name_entry.get().strip()
        target_amount = self.target_amount_entry.get().strip()
        goal_date = self.goal_date_entry.get_date().strftime("%Y-%m-%d")
        amount_saved = self.amount_saved_entry.get().strip()

        if not goal_name or not target_amount or not goal_date or not amount_saved:
            messagebox.showerror("Missing Information", "Please fill in all fields to add a goal.")
            return

        try:
            target_amount = float(target_amount)
            amount_saved = float(amount_saved)
            if target_amount <= 0 or amount_saved < 0:
                raise ValueError

            goal = {
                'name': goal_name,
                'target': target_amount,
                'date': goal_date,
                'saved': amount_saved
            }
            self.savings_goals.append(goal)

            progress = (amount_saved / target_amount) * 100
            self.savings_listbox.insert(tk.END, f"{goal_name} - ${amount_saved:.2f}/${target_amount:.2f} - {progress:.1f}% - Target: {goal_date}")

            self.goal_name_entry.delete(0, tk.END)
            self.target_amount_entry.delete(0, tk.END)
            self.goal_date_entry.set_date(datetime.today())
            self.amount_saved_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for savings goal.")


root = tk.Tk()
app = BudgetApp(root)
root.mainloop()
