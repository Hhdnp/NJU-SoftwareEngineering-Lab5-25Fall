import json
import os
from datetime import datetime


class User:
    def __init__(self, username, password, role="user"):
        self.username = username
        self.password = password
        self.role = role


class Transaction:
    def __init__(self, amount, category, date, type_, note=""):
        self.transaction_id = f"txn_{int(datetime.now().timestamp() * 1000)}"
        self.amount = amount
        self.category = category
        self.date = date
        self.type = type_  # "支出" 或 "收入"
        self.note = note

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'type': self.type,
            'note': self.note
        }

    @classmethod
    def from_dict(cls, data):
        transaction = cls(
            data['amount'],
            data['category'],
            data['date'],
            data['type'],
            data.get('note', '')
        )
        transaction.transaction_id = data['transaction_id']
        return transaction


class Budget:
    def __init__(self, amount, period=None):
        self.budget_id = f"budget_1"
        self.amount = amount
        self.period = period

    def to_dict(self):
        return {
            'budget_id': self.budget_id,
            'amount': self.amount,
            'period': self.period
        }

    @classmethod
    def from_dict(cls, data):
        budget = cls(data['amount'], data.get('period', 'monthly'))
        budget.budget_id = data['budget_id']
        return budget


class DataManager:
    def __init__(self):
        self.data_file = "accounting_data.json"
        self.users = []
        self.transactions = []
        self.budgets = []
        self.categories = ["餐饮", "购物", "交通", "住房", "娱乐", "医疗", "教育", "其他"]

        # 初始化默认数据
        self.initialize_default_data()

    def initialize_default_data(self):
        """初始化默认数据"""
        self.users = [User("admin", "admin", "administrator")]
        if not self.budgets:
            self.budgets = [Budget(5000)]

    def load_data(self):
        """从文件加载数据"""
        if not os.path.exists(self.data_file):
            self.save_data()  # 创建初始文件
            return

        print(f"加载数据中")
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 加载交易记录
        self.transactions = [Transaction.from_dict(
            tx_data) for tx_data in data.get('transactions', [])]
        # 加载预算
        self.budgets = [Budget.from_dict(budget_data)
                        for budget_data in data.get('budgets', [])]

        # 如果没有预算数据，创建默认预算
        if not self.budgets:
            self.budgets = [Budget(5000)]
        print(f"加载完成")

        #except Exception as e:
        #    print(f"加载数据失败: {e}")
        #    # 如果加载失败，使用默认数据
        #    self.initialize_default_data()

    def save_data(self):
        """保存数据到文件"""
        try:
            data = {
                'transactions': [tx.to_dict() for tx in self.transactions],
                'budgets': [budget.to_dict() for budget in self.budgets]
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存数据失败: {e}")

    def delete_transactions(self, transaction_ids):
        """删除指定的交易记录"""
        self.transactions = [
            tx for tx in self.transactions if tx.transaction_id not in transaction_ids]
        self.save_data()

    def add_transaction(self, transaction):
        """添加交易记录"""
        self.transactions.append(transaction)
        self.save_data()

    def get_transaction_by_id(self, transaction_id):
        """根据ID获取交易记录"""
        for tx in self.transactions:
            if tx.transaction_id == transaction_id:
                return tx
        return None


# 全局数据管理器
data_manager = DataManager()
data_manager.load_data()
users = data_manager.users
transactions = data_manager.transactions
budgets = data_manager.budgets
categories = data_manager.categories
