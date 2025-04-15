# -*- coding: utf-8 -*-
"""A budgeting app using customtkinter to track income and expenses."""


# Standard library imports
# import tkinter as tk  # F401: Imported but unused - Removed
from collections import defaultdict
from typing import List, Tuple, Dict, Optional, Union  # For type hinting

# Third-party imports
import customtkinter as ctk

# --- Constants ---

# Predefined frequency options used throughout the application
FREQUENCIES: List[str] = ["Weekly", "Fortnightly", "Monthly", "Yearly"]
# Default expense categories
DEFAULT_EXPENSE_CATEGORIES: List[str] = [
    "Food & Groceries", "Housing", "Transport", "Utilities",
    "Entertainment", "Personal Care", "Health", "Debt Payments",
    "Subscriptions", "Clothing", "Gifts/Donations", "Other"
]

# Conversion factors for calculating budget amounts based on frequency.
# Factors to convert any input frequency TO Weekly
FACTORS_TO_WEEKLY: Dict[str, float] = {
    "Weekly": 1.0,
    "Fortnightly": 1.0 / 2.0,
    "Monthly": 12.0 / 52.0,
    "Yearly": 1.0 / 52.0
}
# Factors to convert FROM Weekly TO the desired output frequency
FACTORS_FROM_WEEKLY: Dict[str, float] = {
    "Weekly": 1.0,
    "Fortnightly": 2.0,
    "Monthly": 52.0 / 12.0,
    "Yearly": 52.0
}

# --- Helper Functions ---


def calculate_budgeted_amount(
    amount: Union[float, str],
    freq_in: str,
    budget_freq_out: str
) -> float:
    """
    Convert an amount from its input frequency to the target frequency.

    Args:
        amount: The monetary amount (float or convertible to float).
        freq_in: The frequency of the input amount (e.g., 'Weekly').
        budget_freq_out: The target frequency for calculation (e.g., 'Monthly').

    Returns:
        The equivalent amount calculated for the budget_freq_out,
        or 0.0 if conversion fails or frequencies are unsupported.
    """
    try:
        numeric_amount = float(amount)
    except (ValueError, TypeError):
        print(f"Warning: Could not convert amount '{amount}' to float.")
        return 0.0

    # PEP 8: E501 Line too long - Fixed
    if (freq_in not in FACTORS_TO_WEEKLY or
            budget_freq_out not in FACTORS_FROM_WEEKLY):
        print(
            f"Warning: Unsupported frequency combination: "
            f"{freq_in} -> {budget_freq_out}"
        )
        return 0.0

    # Perform conversion: Input -> Weekly -> Output
    amount_weekly = numeric_amount * FACTORS_TO_WEEKLY[freq_in]
    amount_budgeted = amount_weekly * FACTORS_FROM_WEEKLY[budget_freq_out]
    return amount_budgeted


# --- Main Application Class ---

class FinancioApp(ctk.CTk):
    """
    Define a personal budgeting application built with customtkinter.

    Allows users to log income and categorized expenses, view summaries,
    and get insights based on a selected budget frequency.
    """

    def __init__(self) -> None:
        # PEP 8: D200 One-line docstring should fit on one line - Fixed
        """Initialize the main application window, UI, and data storage."""
        super().__init__()

        # --- Window Setup ---
        self.title("Financio Budgeting App")
        self.geometry("1000x750")  # Set initial size

        # --- Data Storage ---
        # (name, amount, frequency)
        self.income_data: List[Tuple[str, float, str]] = []
        # (name, amount, frequency, category)
        self.expense_data: List[Tuple[str, float, str, str]] = []

        # --- State Variables ---
        self.selected_budget_freq: str = "Weekly"  # Default frequency
        self.expense_categories: List[str] = DEFAULT_EXPENSE_CATEGORIES[:]  # Copy
        # Key: category_name (str), Value: is_collapsed (bool)
        self.category_collapse_state: Dict[str, bool] = {}
        self.current_view: Optional[str] = None  # Track current page
        self.success_label: Optional[ctk.CTkLabel] = None  # For temp messages

        # --- Appearance Settings ---
        ctk.set_appearance_mode("System")  # Use system theme (Light/Dark)
        ctk.set_default_color_theme("blue")  # Default widget color theme

        # --- UI Element Styles ---
        self.active_button_color = "#3696e0"
        self.default_button_color = "#1F6AA5"
        self.hover_button_color = "#2A82C4"
        self.sidebar_bg_color = "#222f42"
        self.content_bg_color = ("#f0f0f0", "#2b2b2b")  # Light/Dark modes
        self.item_frame_bg_color = ("#e9e9e9", "#3a3a3a")
        self.category_header_fg_color = ("#d0d0d0", "#4a4a4a")
        self.category_header_text_color = ("#101010", "#f0f0f0")
        self.category_header_hover_color = ("#b0b0b0", "#5a5a5a")
        self.positive_balance_color = "#5cb85c"  # Green
        self.negative_balance_color = "#d9534f"  # Red

        # --- Build UI ---
        self._setup_sidebar()
        self._setup_content_area()

        # --- Initial Page Load ---
        self.show_income()

    def _setup_sidebar(self) -> None:
        """Create and configure the sidebar frame and its buttons."""
        self.sidebar = ctk.CTkFrame(
            self, width=180, fg_color=self.sidebar_bg_color, corner_radius=10
        )
        self.sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10)

        # App Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Financio",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(20, 15), padx=10)

        # Common button styles
        button_font = ctk.CTkFont(family="Arial", size=14)
        button_pady = 10
        button_padx = 20
        button_corner_radius = 8

        # Sidebar Buttons
        self.income_btn = ctk.CTkButton(
            self.sidebar, text="Income", command=self.show_income,
            fg_color=self.default_button_color,
            hover_color=self.hover_button_color,
            font=button_font, corner_radius=button_corner_radius
        )
        self.expenses_btn = ctk.CTkButton(
            self.sidebar, text="Expenses", command=self.show_expenses,
            fg_color=self.default_button_color,
            hover_color=self.hover_button_color,
            font=button_font, corner_radius=button_corner_radius
        )
        self.insight_btn = ctk.CTkButton(
            self.sidebar, text="Insights", command=self.show_insights,
            fg_color=self.default_button_color,
            hover_color=self.hover_button_color,
            font=button_font, corner_radius=button_corner_radius
        )

        # Pack buttons
        self.income_btn.pack(fill="x", padx=button_padx, pady=button_pady)
        self.expenses_btn.pack(fill="x", padx=button_padx, pady=button_pady)
        self.insight_btn.pack(fill="x", padx=button_padx, pady=button_pady)

    def _setup_content_area(self) -> None:
        """Create the main frame where page content will be displayed."""
        self.content_frame = ctk.CTkFrame(
            self, corner_radius=10, fg_color=self.content_bg_color
        )
        self.content_frame.pack(
            side="right", expand=True, fill="both", padx=10, pady=10
        )

    def clear_content_frame(self) -> None:
        """Remove all widgets currently inside the main content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def highlight_active_button(self, active_button: ctk.CTkButton) -> None:
        """Set the active sidebar button to the highlight color and reset others."""
        buttons = [self.income_btn, self.expenses_btn, self.insight_btn]
        for button in buttons:
            button.configure(fg_color=self.default_button_color)
        active_button.configure(fg_color=self.active_button_color)

    def show_income(self) -> None:
        """Display the Income entry page."""
        self.clear_content_frame()
        self.highlight_active_button(self.income_btn)
        self.current_view = "income"

        # Constants for this view
        INPUT_WIDGET_WIDTH = 300

        # Page Title
        ctk.CTkLabel(
            self.content_frame, text="Log Your Income",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))

        # Input Area Frame (for centering)
        input_area = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        input_area.pack(pady=10)

        # Income Input Widgets
        self.income_name_entry = ctk.CTkEntry(
            input_area, placeholder_text="Income Source (e.g., Salary)",
            width=INPUT_WIDGET_WIDTH
        )
        self.income_name_entry.pack(pady=8)

        self.income_amount_entry = ctk.CTkEntry(
            input_area, placeholder_text="Income Amount (e.g., 1500)",
            width=INPUT_WIDGET_WIDTH
        )
        self.income_amount_entry.pack(pady=8)

        ctk.CTkLabel(
            input_area, text="Frequency:", font=ctk.CTkFont(size=13)
        ).pack(pady=(10, 2))
        self.income_freq_combo = ctk.CTkComboBox(
            input_area, values=FREQUENCIES, width=INPUT_WIDGET_WIDTH
        )
        self.income_freq_combo.set(FREQUENCIES[0])  # Default 'Weekly'
        self.income_freq_combo.pack(pady=(0, 10))

        self.income_add_btn = ctk.CTkButton(
            input_area, text="Add Income", command=self._add_income_action,
            width=INPUT_WIDGET_WIDTH / 1.5
        )
        self.income_add_btn.pack(pady=(15, 10))

        # Budget Calculation Frequency Setting
        budget_area = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        budget_area.pack(pady=(15, 5))
        ctk.CTkLabel(
            budget_area, text="Calculate Budget As:",
            font=ctk.CTkFont(size=13)
        ).pack(pady=(5, 2))
        # Limit options here if desired (e.g., exclude 'Yearly')
        budget_freq_values = ["Weekly", "Fortnightly", "Monthly"]
        # PEP 8: E501 Line too long - Fixed
        budget_freq_combo = ctk.CTkComboBox(
            budget_area,
            values=budget_freq_values,
            command=self._update_selected_budget_freq_action,
            width=INPUT_WIDGET_WIDTH
        )
        budget_freq_combo.set(self.selected_budget_freq)
        budget_freq_combo.pack(pady=(0, 10))

        # Separator
        separator = ctk.CTkFrame(
            self.content_frame, height=1, fg_color="gray"
        )
        separator.pack(fill="x", padx=40, pady=(15, 10))

        # Income Display Area
        ctk.CTkLabel(
            self.content_frame, text="Logged Income",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(5, 5))
        self.income_display_frame = ctk.CTkScrollableFrame(
            self.content_frame, label_text="", fg_color="transparent"
        )
        self.income_display_frame.pack(
            fill="both", expand=True, pady=(0, 10), padx=30
        )
        self._update_income_display_list()

    def _update_selected_budget_freq_action(self, choice: str) -> None:
        """Update stored budget frequency and refresh relevant views."""
        self.selected_budget_freq = choice
        # Refresh view if it depends on this frequency
        if self.current_view == "expenses":
            self._update_expense_display_list()
        elif self.current_view == "insights":
            self.show_insights()  # Recalculates totals

    def _add_income_action(self) -> None:
        """Get income details, validate, add to data, and update UI."""
        income_name = self.income_name_entry.get()
        amount_str = self.income_amount_entry.get()
        freq = self.income_freq_combo.get()

        # Validation
        if not income_name:
            self.show_error_message("Please enter an income source/name.")
            return
        if not amount_str:
            self.show_error_message("Please enter an income amount.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            self.show_error_message(
                "Please enter a valid positive number for the amount."
            )
            return
        if freq not in FREQUENCIES:
            self.show_error_message("Please select a valid frequency.")
            return

        # Add Data and Update UI
        self.income_data.append((income_name, amount, freq))
        self._update_income_display_list()
        self.show_success_popup(
            f"Logged income '{income_name}': ${amount:.2f}"
        )

        # Clear input fields
        self.income_name_entry.delete(0, 'end')
        self.income_amount_entry.delete(0, 'end')
        # Reset frequency dropdown
        self.income_freq_combo.set(FREQUENCIES[0])

    def _update_income_display_list(self) -> None:
        """Clear and repopulate the income display scrollable frame."""
        # Clear previous items
        for widget in self.income_display_frame.winfo_children():
            widget.destroy()

        if not self.income_data:
            ctk.CTkLabel(
                self.income_display_frame,
                text="No income logged yet.", text_color="gray"
            ).pack(pady=20)
            return

        # Populate with current data
        # Index 'idx' kept for potential future delete functionality
        for idx, (name, amount, freq) in enumerate(self.income_data):
            item_frame = ctk.CTkFrame(
                self.income_display_frame,
                fg_color=self.item_frame_bg_color,
                corner_radius=6
            )
            item_frame.pack(fill="x", pady=4, padx=5)

            # Right side: Amount and Frequency
            label_text = f"${amount:.2f} ({freq})"
            ctk.CTkLabel(
                item_frame, text=label_text, anchor="e"
            ).pack(side="right", padx=(10, 15), pady=7)

            # Left side: Income Name (expands to fill space)
            ctk.CTkLabel(
                item_frame, text=f"{name}", anchor="w"
            ).pack(side="left", padx=(15, 10), pady=7, fill="x", expand=True)
            # TODO: Add delete button here if needed using 'idx'

    def show_expenses(self) -> None:
        """Display the Expense entry page."""
        self.clear_content_frame()
        self.highlight_active_button(self.expenses_btn)
        self.current_view = "expenses"

        # Constants for this view
        INPUT_WIDGET_WIDTH = 300

        # Page Title
        ctk.CTkLabel(
            self.content_frame, text="Log Your Expenses",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))

        # Input Area Frame
        input_area = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        input_area.pack(pady=5)

        # Expense Input Widgets
        self.expense_name_entry = ctk.CTkEntry(
            input_area, placeholder_text="Expense Name (e.g., Groceries)",
            width=INPUT_WIDGET_WIDTH
        )
        self.expense_name_entry.pack(pady=6)

        self.expense_amount_entry = ctk.CTkEntry(
            input_area, placeholder_text="Expense Amount (e.g., 150.75)",
            width=INPUT_WIDGET_WIDTH
        )
        self.expense_amount_entry.pack(pady=6)

        ctk.CTkLabel(
            input_area, text="Frequency:", font=ctk.CTkFont(size=13)
        ).pack(pady=(8, 2))
        self.expense_freq_combo = ctk.CTkComboBox(
            input_area, values=FREQUENCIES, width=INPUT_WIDGET_WIDTH
        )
        self.expense_freq_combo.set(FREQUENCIES[0])
        self.expense_freq_combo.pack(pady=(0, 6))

        ctk.CTkLabel(
            input_area, text="Category:", font=ctk.CTkFont(size=13)
        ).pack(pady=(8, 2))
        self.expense_category_combo = ctk.CTkComboBox(
            input_area, values=self.expense_categories,
            width=INPUT_WIDGET_WIDTH
        )
        # Ensure a valid default category is set
        default_category = (self.expense_categories[0]
                            if self.expense_categories else "Other")
        self.expense_category_combo.set(default_category)
        self.expense_category_combo.pack(pady=(0, 10))

        self.expense_add_btn = ctk.CTkButton(
            input_area, text="Add Expense", command=self._add_expense_action,
            width=INPUT_WIDGET_WIDTH / 1.5
        )
        self.expense_add_btn.pack(pady=(15, 10))

        # Separator
        separator = ctk.CTkFrame(
            self.content_frame, height=1, fg_color="gray"
        )
        separator.pack(fill="x", padx=40, pady=(15, 10))

        # Expense Display Area
        ctk.CTkLabel(
            self.content_frame, text="Logged Expenses",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(5, 5))
        self.expense_list_frame = ctk.CTkScrollableFrame(
            self.content_frame, label_text="", fg_color="transparent"
        )
        self.expense_list_frame.pack(
            fill="both", expand=True, pady=(0, 10), padx=30
        )
        self._update_expense_display_list()

    def _add_expense_action(self) -> None:
        """Get expense details, validate, add to data, and update UI."""
        name = self.expense_name_entry.get()
        amount_str = self.expense_amount_entry.get()
        freq = self.expense_freq_combo.get()
        category = self.expense_category_combo.get()

        # Validation
        if not name:
            self.show_error_message("An expense name is required.")
            return
        if not amount_str:
            self.show_error_message("Please enter an expense amount.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            self.show_error_message(
                "Please enter a valid positive number for the amount."
            )
            return
        if freq not in FREQUENCIES:
            self.show_error_message("Please select a valid frequency.")
            return
        if not category or category not in self.expense_categories:
            self.show_error_message("Please select a valid category.")
            return

        # Add Data and Update UI
        self.expense_data.append((name, amount, freq, category))
        # Ensure category exists in collapse state (default: expanded)
        if category not in self.category_collapse_state:
            self.category_collapse_state[category] = False

        self._update_expense_display_list()
        self.show_success_popup(
            f"Logged '{name}' (${amount:.2f}) in {category}"
        )

        # Clear input fields
        self.expense_name_entry.delete(0, 'end')
        self.expense_amount_entry.delete(0, 'end')
        self.expense_freq_combo.set(FREQUENCIES[0])  # Reset frequency
        default_category = (self.expense_categories[0]
                            if self.expense_categories else "Other")
        self.expense_category_combo.set(default_category)  # Reset category

    def _toggle_category_collapse(self, category_name: str) -> None:
        """Toggle the collapse state for a category and redraw the list."""
        if category_name in self.category_collapse_state:
            self.category_collapse_state[category_name] = \
                not self.category_collapse_state[category_name]
            self._update_expense_display_list()  # Redraw needed

    def _update_expense_display_list(self) -> None:
        """Clear and repopulate the expense list, grouped by category."""
        # Clear previous display
        for widget in self.expense_list_frame.winfo_children():
            widget.destroy()

        if not self.expense_data:
            ctk.CTkLabel(
                self.expense_list_frame,
                text="No expenses logged yet.", text_color="gray"
            ).pack(pady=20)
            return

        # Group expenses by category
        grouped_expenses: Dict[str, List[Tuple[str, float, str]]] = \
            defaultdict(list)
        for name, amount, freq, category in self.expense_data:
            grouped_expenses[category].append((name, amount, freq))

        # Sort categories alphabetically for consistent display
        sorted_categories = sorted(grouped_expenses.keys())

        # Display each category
        for category in sorted_categories:
            is_collapsed = self.category_collapse_state.get(category, False)
            # Up arrow (collapsed), Down arrow (expanded)
            arrow = "▲" if is_collapsed else "▼"

            # Calculate category total based on *selected budget frequency*
            category_total = sum(
                calculate_budgeted_amount(amt, frq, self.selected_budget_freq)
                for _, amt, frq in grouped_expenses[category]
            )

            # --- Category Header Row ---
            header_frame = ctk.CTkFrame(
                self.expense_list_frame, fg_color="transparent"
            )
            header_frame.pack(fill="x", pady=(5, 0))

            # Category Total Label (Right Aligned)
            total_label_font = ctk.CTkFont(size=13, weight="bold")
            total_label_text = (f"${category_total:.2f} / "
                                f"{self.selected_budget_freq}")
            total_label = ctk.CTkLabel(
                header_frame, text=total_label_text,
                font=total_label_font, anchor="e"
            )
            total_label.pack(side="right", padx=(5, 10), pady=4)

            # Category Header Button (Left Aligned, Clickable)
            header_btn = ctk.CTkButton(
                header_frame,
                text=f"{arrow} {category}",
                # Use lambda to pass the correct category name at runtime
                command=lambda cat=category: self._toggle_category_collapse(cat),
                fg_color=self.category_header_fg_color,
                text_color=self.category_header_text_color,
                hover_color=self.category_header_hover_color,
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            )
            header_btn.pack(
                side="left", fill="x", expand=True, padx=5, pady=4
            )

            # --- Items Frame (for indentation and conditional display) ---
            items_frame = ctk.CTkFrame(
                self.expense_list_frame, fg_color="transparent"
            )

            # Populate items only if the category is expanded
            if not is_collapsed:
                items_frame.pack(fill="x", padx=0, pady=0)
                # Sort items within category (optional, by name here)
                sorted_items = sorted(grouped_expenses[category])
                for name, amount, freq in sorted_items:
                    item_frame = ctk.CTkFrame(
                        items_frame,
                        fg_color=self.item_frame_bg_color,
                        corner_radius=6
                    )
                    # Indent items slightly relative to header
                    item_frame.pack(fill="x", pady=3, padx=(20, 5))

                    # Right side: Amount and Frequency
                    amount_freq_text = f"${amount:.2f} ({freq})"
                    ctk.CTkLabel(
                        item_frame, text=amount_freq_text,
                        font=ctk.CTkFont(size=13), anchor="e"
                    ).pack(side="right", padx=(10, 15), pady=6)

                    # Left side: Expense Name
                    ctk.CTkLabel(
                        item_frame, text=f"{name}",
                        font=ctk.CTkFont(size=13), anchor="w"
                    ).pack(side="left", padx=(15, 10), pady=6, fill="x",
                           expand=True)
                    # TODO: Add delete button here if needed

            # If collapsed, items_frame is created but not packed, hiding items

    def show_insights(self) -> None:
        """Display the Insights page with calculated summaries."""
        self.clear_content_frame()
        self.highlight_active_button(self.insight_btn)
        self.current_view = "insights"

        # Page Title
        ctk.CTkLabel(
            self.content_frame, text="Budget Insights",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(15, 15))

        # --- Calculate Totals based on selected frequency ---
        total_income = sum(
            calculate_budgeted_amount(amount, freq, self.selected_budget_freq)
            for _, amount, freq in self.income_data
        ) if self.income_data else 0.0

        total_expenses = sum(
            calculate_budgeted_amount(amount, freq, self.selected_budget_freq)
            for _, amount, freq, _ in self.expense_data  # Ignore category
        ) if self.expense_data else 0.0

        balance = total_income - total_expenses

        # --- Display Summary Frame (using grid for alignment) ---
        results_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )
        results_frame.pack(pady=10, padx=40, fill="x")
        # Configure grid columns: 0 for labels, 1 for values
        results_frame.grid_columnconfigure(0, weight=0)  # Fixed width
        results_frame.grid_columnconfigure(1, weight=1)  # Expandable

        # Define fonts and padding
        label_font = ctk.CTkFont(size=14)
        value_font = ctk.CTkFont(size=14, weight="bold")
        pady_val = 6  # Vertical padding between rows

        # Row 0: Budget Frequency
        ctk.CTkLabel(
            results_frame, text="Budget Calculated:", font=label_font
        ).grid(row=0, column=0, pady=pady_val, sticky="w")
        ctk.CTkLabel(
            results_frame, text=f"{self.selected_budget_freq}", font=value_font
        ).grid(row=0, column=1, pady=pady_val, sticky="w", padx=5)

        # Row 1: Total Income
        ctk.CTkLabel(
            results_frame, text="Total Income:", font=label_font
        ).grid(row=1, column=0, pady=pady_val, sticky="w")
        ctk.CTkLabel(
            results_frame, text=f"${total_income:.2f}", font=value_font,
            text_color=self.positive_balance_color  # Green
        ).grid(row=1, column=1, pady=pady_val, sticky="w", padx=5)

        # Row 2: Total Expenses
        ctk.CTkLabel(
            results_frame, text="Total Expenses:", font=label_font
        ).grid(row=2, column=0, pady=pady_val, sticky="w")
        ctk.CTkLabel(
            results_frame, text=f"${total_expenses:.2f}", font=value_font,
            text_color=self.negative_balance_color  # Red
        ).grid(row=2, column=1, pady=pady_val, sticky="w", padx=5)

        # Separator
        separator = ctk.CTkFrame(
            self.content_frame, height=1, fg_color="gray"
        )
        separator.pack(fill="x", padx=40, pady=(15, 10))

        # --- Display Balance ---
        balance_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )
        balance_frame.pack(pady=10, padx=40, fill="x")
        balance_frame.grid_columnconfigure(0, weight=0)
        balance_frame.grid_columnconfigure(1, weight=1)

        balance_color = (self.positive_balance_color if balance >= 0
                         else self.negative_balance_color)
        balance_font = ctk.CTkFont(size=18, weight="bold")

        ctk.CTkLabel(
            balance_frame, text="Remaining Balance:", font=balance_font
        ).grid(row=0, column=0, pady=10, sticky="w")
        ctk.CTkLabel(
            balance_frame, text=f"${balance:.2f}", font=balance_font,
            text_color=balance_color
        ).grid(row=0, column=1, pady=10, padx=10, sticky="w")

        # --- Display Status Message ---
        status_message = ""
        status_color = "gray"  # Default color

        if not self.income_data and not self.expense_data:
            status_message = "Enter income and expenses to see insights."
        elif balance > 0:
            status_message = "You are within your budget!"
            status_color = self.positive_balance_color
        elif balance < 0:
            status_message = "Your expenses currently exceed your income."
            status_color = self.negative_balance_color
        else:  # balance == 0
            status_message = "Your income perfectly matches your expenses."
            # Use default text color based on theme
            status_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

        ctk.CTkLabel(
            self.content_frame, text=status_message,
            font=ctk.CTkFont(size=13), text_color=status_color
        ).pack(pady=15, padx=40)

    def show_error_message(self, message: str) -> None:
        """Display a modal error pop-up window centered on the main app."""
        error_popup = ctk.CTkToplevel(self)
        error_popup.geometry("350x150")
        error_popup.title("Error")
        error_popup.transient(self)  # Associate with main window
        error_popup.grab_set()       # Make modal
        error_popup.attributes("-topmost", True)  # Keep on top

        # Center the popup
        self.update_idletasks()  # Ensure main window geometry is current
        main_x, main_y = self.winfo_x(), self.winfo_y()
        main_w, main_h = self.winfo_width(), self.winfo_height()
        popup_w, popup_h = 350, 150
        center_x = main_x + (main_w // 2) - (popup_w // 2)
        center_y = main_y + (main_h // 2) - (popup_h // 2)
        error_popup.geometry(f"{popup_w}x{popup_h}+{center_x}+{center_y}")

        # Layout content using grid (simpler for centering vertically)
        error_popup.grid_columnconfigure(0, weight=1)  # Center content H
        error_popup.grid_rowconfigure(0, weight=0)      # Title row
        error_popup.grid_rowconfigure(1, weight=1)      # Message row (expands)
        error_popup.grid_rowconfigure(2, weight=0)      # Button row

        # Title
        ctk.CTkLabel(
            error_popup, text="Oops!",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, pady=(10, 5))

        # Message (with wrapping)
        ctk.CTkLabel(
            error_popup, text=message,
            font=ctk.CTkFont(size=14),
            wraplength=320  # Wrap text if it's too long
        ).grid(row=1, column=0, pady=5, padx=15, sticky="nsew")

        # OK Button
        ctk.CTkButton(
            error_popup, text="OK", command=error_popup.destroy, width=80
        ).grid(row=2, column=0, pady=(5, 15))

        # Ensure proper cleanup if window 'X' is clicked
        error_popup.protocol("WM_DELETE_WINDOW", error_popup.destroy)
        error_popup.wait_window()  # Wait for popup to be closed

    def show_success_popup(self, message: str) -> None:
        """Display a temporary success message label at the window bottom."""
        # Destroy previous success label if it exists
        if self.success_label and self.success_label.winfo_exists():
            self.success_label.destroy()

        # Create the new label
        self.success_label = ctk.CTkLabel(
            self,  # Parent is the main window (self)
            text=message,
            font=ctk.CTkFont(size=12),
            fg_color=self.positive_balance_color,  # Green background
            text_color="white",                     # White text
            corner_radius=8,
            padx=10,
            pady=5
        )
        # Place it at the bottom center, slightly offset from the edge
        self.success_label.place(relx=0.5, rely=1.0, anchor="s", y=-20)

        # Schedule its destruction after 2.5 seconds
        # Use lambda to ensure the check happens *when* the 'after' runs
        self.after(
            2500,
            lambda: self.success_label.destroy()
            if self.success_label and self.success_label.winfo_exists() else None
        )


# --- Application Entry Point ---

if __name__ == "__main__":
    app = FinancioApp()
    app.mainloop()