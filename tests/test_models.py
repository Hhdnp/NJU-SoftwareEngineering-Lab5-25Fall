from unittest.mock import patch, mock_open
import pytest
import json
from models import DataManager, Transaction, Budget, User
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'budget_app'))


# Add budget_app directory to sys.path


class TestTransaction:
    def test_transaction_creation(self):
        t = Transaction(100, "Food", "2023-01-01", "支出", "Lunch")
        assert t.amount == 100
        assert t.category == "Food"
        assert t.date == "2023-01-01"
        assert t.type == "支出"
        assert t.note == "Lunch"
        assert t.transaction_id.startswith("txn_")

    def test_to_dict(self):
        t = Transaction(100, "Food", "2023-01-01", "支出", "Lunch")
        t.transaction_id = "txn_123"
        data = t.to_dict()
        assert data['transaction_id'] == "txn_123"
        assert data['amount'] == 100
        assert data['category'] == "Food"

    def test_from_dict(self):
        data = {
            'transaction_id': 'txn_123',
            'amount': 100,
            'category': 'Food',
            'date': '2023-01-01',
            'type': '支出',
            'note': 'Lunch'
        }
        t = Transaction.from_dict(data)
        assert t.transaction_id == 'txn_123'
        assert t.amount == 100
        assert t.category == 'Food'


class TestBudget:
    def test_budget_creation(self):
        b = Budget(5000)
        assert b.amount == 5000
        assert b.period == "monthly"

    def test_to_dict(self):
        b = Budget(5000)
        b.budget_id = "budget_1"
        data = b.to_dict()
        assert data['amount'] == 5000
        assert data['budget_id'] == "budget_1"

    def test_from_dict(self):
        data = {
            'budget_id': 'budget_1',
            'amount': 6000,
            'period': 'monthly'
        }
        b = Budget.from_dict(data)
        assert b.amount == 6000
        assert b.budget_id == 'budget_1'


class TestDataManager:
    @pytest.fixture
    def dm(self, tmp_path):
        # Use a temporary file for data
        d = DataManager()
        d.data_file = str(tmp_path / "test_data.json")
        # Reset data
        d.transactions = []
        d.budgets = []
        return d

    def test_initialize_default_data(self, dm):
        dm.initialize_default_data()
        assert len(dm.users) > 0
        assert len(dm.budgets) > 0
        assert dm.users[0].username == "admin"

    def test_save_data(self, dm):
        t = Transaction(100, "Food", "2023-01-01", "支出")
        dm.transactions.append(t)
        dm.save_data()

        assert os.path.exists(dm.data_file)
        with open(dm.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data['transactions']) == 1
            assert data['transactions'][0]['amount'] == 100

    def test_load_data_exists(self, dm):
        # Create a dummy file
        data = {
            'transactions': [{
                'transaction_id': 'txn_1',
                'amount': 200,
                'category': 'Food',
                'date': '2023-01-01',
                'type': '支出',
                'note': ''
            }],
            'budgets': []
        }
        with open(dm.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

        dm.load_data()
        assert len(dm.transactions) == 1
        assert dm.transactions[0].amount == 200

    def test_load_data_not_exists(self, dm):
        if os.path.exists(dm.data_file):
            os.remove(dm.data_file)
        dm.load_data()
        # Should create file and init defaults
        assert os.path.exists(dm.data_file)
        assert len(dm.budgets) > 0

    def test_add_transaction(self, dm):
        t = Transaction(300, "Food", "2023-01-01", "支出")
        dm.add_transaction(t)
        assert len(dm.transactions) == 1
        assert dm.transactions[0].amount == 300
        # Check if saved
        with open(dm.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data['transactions']) == 1

    def test_delete_transactions(self, dm):
        t1 = Transaction(100, "Food", "2023-01-01", "支出")
        t1.transaction_id = "id1"
        t2 = Transaction(200, "Food", "2023-01-01", "支出")
        t2.transaction_id = "id2"
        dm.transactions = [t1, t2]

        dm.delete_transactions(["id1"])
        assert len(dm.transactions) == 1
        assert dm.transactions[0].transaction_id == "id2"

    def test_get_transaction_by_id_found(self, dm):
        t = Transaction(100, "Food", "2023-01-01", "支出")
        t.transaction_id = "find_me"
        dm.transactions = [t]

        found = dm.get_transaction_by_id("find_me")
        assert found is not None
        assert found.amount == 100

    def test_get_transaction_by_id_not_found(self, dm):
        found = dm.get_transaction_by_id("non_existent")
        assert found is None

    def test_load_data_invalid_json(self, dm):
        # 写入非法 JSON 内容
        with open(dm.data_file, 'w', encoding='utf-8') as f:
            f.write("This is not a valid json")

        # 尝试加载数据
        dm.load_data()

        # 验证是否回退到默认数据（例如默认预算）
        assert len(dm.budgets) > 0
        assert dm.budgets[0].amount == 5000
        # 验证交易记录是否为空
        assert len(dm.transactions) == 0
