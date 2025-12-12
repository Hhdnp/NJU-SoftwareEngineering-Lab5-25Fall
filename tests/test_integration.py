import budget_app.models as models_module
from budget_app.models import DataManager, Transaction, Budget
import sys
import os
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime

# Add budget_app directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'budget_app'))

# Mock UI libraries just in case, but we will avoid using them
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['matplotlib.backends.backend_tkagg'] = MagicMock()


class TestIntegration:

    @pytest.fixture
    def data_manager(self, tmp_path):
        """Fixture to provide a DataManager with a temporary file"""
        dm = DataManager()
        dm.data_file = str(tmp_path / "integration_test_data.json")
        # Reset global lists in models module to ensure isolation
        models_module.transactions.clear()
        models_module.budgets.clear()
        # Also reset instance lists
        dm.transactions = models_module.transactions
        dm.budgets = models_module.budgets

        # Initialize with some default budget if needed
        if not dm.budgets:
            dm.budgets.append(Budget(5000))

        return dm

    def test_transaction_persistence_flow(self, data_manager):
        """
        Integration Test 1: Transaction Persistence Flow (Bottom-up: Data Layer)
        Test adding a transaction, saving it, and reloading it in a new manager.
        """
        # 1. Add a transaction
        t1 = Transaction(150.0, "餐饮", "2023-10-01", "支出", "Lunch")
        data_manager.add_transaction(t1)

        # Verify it's in memory
        assert len(data_manager.transactions) == 1
        assert data_manager.transactions[0].amount == 150.0

        # 2. Save data
        data_manager.save_data()

        # 3. Create a NEW DataManager instance pointing to the same file
        new_dm = DataManager()
        new_dm.data_file = data_manager.data_file
        new_dm.load_data()

        # 4. Verify data is loaded correctly
        assert len(new_dm.transactions) == 1
        loaded_t = new_dm.transactions[0]
        assert loaded_t.amount == 150.0
        assert loaded_t.category == "餐饮"
        assert loaded_t.note == "Lunch"

        # 5. Delete transaction
        new_dm.delete_transactions([loaded_t.transaction_id])
        assert len(new_dm.transactions) == 0

        # 6. Reload again to verify deletion persisted
        final_dm = DataManager()
        final_dm.data_file = data_manager.data_file
        final_dm.load_data()
        assert len(final_dm.transactions) == 0

    def test_statistics_logic_integration(self, data_manager):
        """
        Integration Test 2: Statistics Logic Integration
        Verify that transaction data can be correctly aggregated for statistics,
        simulating the logic used in StatisticsWindow without instantiating it.
        """
        # 1. Setup data
        t1 = Transaction(100.0, "餐饮", "2023-10-01", "支出", "Lunch")
        t2 = Transaction(200.0, "交通", "2023-10-01", "支出", "Bus")
        t3 = Transaction(500.0, "工资", "2023-10-01", "收入", "Salary")
        t4 = Transaction(50.0, "餐饮", "2023-10-02", "支出", "Dinner")

        data_manager.add_transaction(t1)
        data_manager.add_transaction(t2)
        data_manager.add_transaction(t3)
        data_manager.add_transaction(t4)

        # 2. Simulate Aggregation Logic (Daily)
        expense_data = {}
        income_data = {}
        category_data = {}

        for transaction in data_manager.transactions:
            date = transaction.date
            if transaction.type == "支出":
                expense_data[date] = expense_data.get(
                    date, 0) + transaction.amount
                category_data[transaction.category] = category_data.get(
                    transaction.category, 0) + transaction.amount
            else:
                income_data[date] = income_data.get(
                    date, 0) + transaction.amount

        # 3. Verify Results
        # Daily Expenses
        assert expense_data["2023-10-01"] == 300.0  # 100 + 200
        assert expense_data["2023-10-02"] == 50.0   # 50

        # Daily Income
        assert income_data["2023-10-01"] == 500.0

        # Category Expenses
        assert category_data["餐饮"] == 150.0  # 100 + 50
        assert category_data["交通"] == 200.0

    def test_budget_logic_integration(self, data_manager):
        """
        Integration Test 3: Budget Logic Integration
        Verify that monthly expenses are correctly calculated against the budget,
        simulating the logic used in BudgetWindow without instantiating it.
        """
        # 1. Setup Data
        current_month_str = datetime.now().strftime("%Y-%m")

        # Transaction in current month
        t1 = Transaction(
            1000.0, "餐饮", f"{current_month_str}-01", "支出", "Big Meal")
        t2 = Transaction(
            2000.0, "工资", f"{current_month_str}-05", "收入", "Salary")

        # Transaction in DIFFERENT month (should be ignored)
        past_month = "2020-01"
        if past_month == current_month_str:
            past_month = "2019-01"  # Just in case
        t3 = Transaction(500.0, "餐饮", f"{past_month}-01", "支出", "Old Meal")

        data_manager.add_transaction(t1)
        data_manager.add_transaction(t2)
        data_manager.add_transaction(t3)

        # Set budget
        models_module.budgets[0].amount = 5000.0

        # 2. Simulate Budget Calculation Logic
        monthly_expense = 0
        monthly_income = 0

        for transaction in data_manager.transactions:
            if transaction.date.startswith(current_month_str):
                if transaction.type == "支出":
                    monthly_expense += transaction.amount
                else:
                    monthly_income += transaction.amount

        budget_amount = models_module.budgets[0].amount
        balance = budget_amount - monthly_expense

        # 3. Verify Results
        assert monthly_expense == 1000.0  # Only t1
        assert monthly_income == 2000.0  # Only t2
        assert budget_amount == 5000.0
        assert balance == 4000.0
