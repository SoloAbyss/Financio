import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budgeting App")
        self.root.geometry("600x750")
        self.root.resizable(False, False)

        self.income = tk.DoubleVar(value=0.0)
        self.total_expenses = tk.DoubleVar(value=0.0)
        self.remaining_budget = tk.DoubleVar(value=0.0)

        self.expenses = []
        self.savings_goals = []  

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        self.tab_budget = ttk.Frame(self.notebook)
        self.tab_expenses = ttk.Frame(self.notebook)
        self.tab_savings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_budget, text="Budget")
        self.notebook.add(self.tab_expenses, text="Log Expenses")
        self.notebook.add(self.tab_savings, text="Savings & Goals")

        self.create_budget_widgets()
        self.create_expenses_widgets()
        self.create_savings_widgets()

    def create_budget_widgets(self):
        ttk.Label(self.tab_budget, text="Budgeting App", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.tab_budget, text="Enter Income:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        ttk.Entry(self.tab_budget, textvariable=self.income).grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.tab_budget, text="Total Expenses:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        ttk.Label(self.tab_budget, textvariable=self.total_expenses).grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.tab_budget, text="Remaining Budget:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        ttk.Label(self.tab_budget, textvariable=self.remaining_budget).grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self.tab_budget, text="Calculate Remaining Budget", command=self.calculate_remaining_budget).grid(row=4, column=0, columnspan=2, pady=10)

    def create_expenses_widgets(self):
        ttk.Label(self.tab_expenses, text="Log Expenses", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(self.tab_expenses, text="Payee:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.payee_entry = ttk.Entry(self.tab_expenses)
        self.payee_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.tab_expenses, text="Date:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.date_entry = DateEntry(self.tab_expenses, date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.tab_expenses, text="Amount:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.amount_entry = ttk.Entry(self.tab_expenses)
        self.amount_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self.tab_expenses, text="Add Expense", command=self.add_expense_details).grid(row=4, column=0, columnspan=2, pady=10)

        self.expenses_listbox = tk.Listbox(self.tab_expenses, width=50, height=10)
        self.expenses_listbox.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def add_expense_details(self):
        payee = self.payee_entry.get().strip()
        amount_str = self.amount_entry.get().strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")

            expense = {'payee': payee, 'amount': amount, 'date': self.date_entry.get()}
            self.expenses.append(expense)
            self.expenses_listbox.insert(tk.END, f"{expense['date']} - {payee}: ${amount:.2f}")

            self.total_expenses.set(sum(exp['amount'] for exp in self.expenses))
            self.calculate_remaining_budget()

            self.payee_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")

    def create_savings_widgets(self):
        ttk.Label(self.tab_savings, text="Savings & Goal Setting", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.tab_savings, text="Goal Name:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.goal_name_entry = ttk.Entry(self.tab_savings)
        self.goal_name_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.tab_savings, text="Target Amount ($):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.target_amount_entry = ttk.Entry(self.tab_savings)
        self.target_amount_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(self.tab_savings, text="Add Goal", command=self.add_savings_goal).grid(row=3, column=0, columnspan=2, pady=10)

        self.savings_listbox = tk.Listbox(self.tab_savings, width=50, height=10)
        self.savings_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Section to contribute money to a goal
        ttk.Label(self.tab_savings, text="Contribution Amount:").grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.contribution_entry = ttk.Entry(self.tab_savings)
        self.contribution_entry.grid(row=5, column=1, padx=10, pady=10)

        ttk.Button(self.tab_savings, text="Contribute", command=self.contribute_to_goal).grid(row=6, column=0, columnspan=2, pady=10)

    def add_savings_goal(self):
        goal_name = self.goal_name_entry.get().strip()
        target_amount_str = self.target_amount_entry.get().strip()

        try:
            target_amount = float(target_amount_str)
            if target_amount <= 0:
                raise ValueError("Amount must be positive.")

            goal = {'name': goal_name, 'target': target_amount, 'saved': 0}
            self.savings_goals.append(goal)

            self.savings_listbox.insert(tk.END, f"{goal_name} - Target: ${target_amount:.2f}, Saved: $0.00")

            self.goal_name_entry.delete(0, tk.END)
            self.target_amount_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")

    def contribute_to_goal(self):
        selected_index = self.savings_listbox.curselection()
        if not selected_index:
            messagebox.showerror("No Goal Selected", "Please select a goal from the list.")
            return

        contribution_str = self.contribution_entry.get().strip()

        try:
            contribution_amount = float(contribution_str)
            if contribution_amount <= 0:
                raise ValueError("Contribution must be positive.")

            # Get selected goal and update savings
            goal = self.savings_goals[selected_index[0]]
            goal['saved'] += contribution_amount

            # Update listbox display
            self.savings_listbox.delete(selected_index[0])
            self.savings_listbox.insert(selected_index[0], f"{goal['name']} - Target: ${goal['target']:.2f}, Saved: ${goal['saved']:.2f}")

            self.contribution_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid contribution amount.")


    def calculate_remaining_budget(self):
        income = self.income.get()
        total_expenses = sum(exp['amount'] for exp in self.expenses)
        self.remaining_budget.set(f"${income - total_expenses:.2f}")

root = tk.Tk()
app = BudgetApp(root)
root.mainloop()
