from budget_app.models import Transaction, DataManager, Budget
from budget_app.utils import validate_date
import sys
import os
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import patch, MagicMock

# Add budget_app directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'budget_app'))


class TestFuzzing:

    # =========================================================================
    # 1. 工具函数模糊测试 (Utility Fuzzing)
    # =========================================================================
    @given(
        year=st.text(),
        month=st.text(),
        day=st.text()
    )
    def test_fuzz_validate_date(self, year, month, day):
        """
        模糊测试 validate_date 函数。
        输入：任意文本字符串。
        预期：函数不应抛出未捕获的异常（Crash），应该只返回 (False, msg) 或 (True, msg)。
        """
        try:
            is_valid, message = validate_date(year, month, day)
            # 结果必须是布尔值
            assert isinstance(is_valid, bool)
            # 消息必须是字符串
            assert isinstance(message, str)
        except Exception as e:
            # 如果抛出了异常，说明代码没有处理好某些边缘输入
            pytest.fail(
                f"validate_date crashed with input ({year}, {month}, {day}). Error: {e}")

    # =========================================================================
    # 2. 模型层模糊测试 (Model Fuzzing)
    # =========================================================================
    @given(
        amount=st.one_of(st.integers(), st.floats(
            allow_nan=False, allow_infinity=False), st.text()),
        category=st.text(),
        date=st.text(),
        type_=st.text(),
        note=st.text()
    )
    def test_fuzz_transaction_model(self, amount, category, date, type_, note):
        """
        模糊测试 Transaction 类的初始化和 to_dict 方法。
        预期：即使数据类型奇怪，只要能初始化，to_dict 就不应崩溃。
        """
        try:
            # 尝试初始化
            t = Transaction(amount, category, date, type_, note)

            # 尝试转换为字典
            data = t.to_dict()

            # 验证基本属性是否存在
            assert 'transaction_id' in data
            assert data['amount'] == amount

            # 尝试从字典恢复 (Round-trip test)
            # 注意：如果 amount 是字符串，from_dict 可能会直接赋值，这取决于实现
            t2 = Transaction.from_dict(data)
            assert t2.amount == amount

        except Exception as e:
            pytest.fail(
                f"Transaction model crashed with inputs: amount={amount}, category={category}... Error: {e}")

    # =========================================================================
    # 3. 持久化层模糊测试 (Persistence Fuzzing)
    # =========================================================================
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(file_content=st.binary())
    def test_fuzz_data_loading_garbage(self, tmp_path, file_content):
        """
        模糊测试数据加载功能。
        输入：随机二进制数据（模拟文件损坏、乱码、非JSON格式）。
        预期：DataManager.load_data() 应该捕获 JSONDecodeError 或其他 IO 异常，
             并回退到默认状态，而不是让程序崩溃。
        """
        # 创建一个临时文件路径
        fuzz_file = tmp_path / "fuzz_data.json"

        # 写入随机生成的二进制垃圾数据
        with open(fuzz_file, 'wb') as f:
            f.write(file_content)

        # 初始化 DataManager
        dm = DataManager()
        dm.data_file = str(fuzz_file)

        # 模拟 print 以避免控制台输出干扰
        with patch('builtins.print'):
            try:
                dm.load_data()

                # 如果加载失败（预期行为），它应该初始化默认数据
                # 检查是否安全恢复
                assert isinstance(dm.transactions, list)
                assert isinstance(dm.budgets, list)

                # 如果文件完全损坏，应该有默认预算
                if len(dm.budgets) > 0:
                    assert isinstance(dm.budgets[0], Budget)

            except Exception as e:
                pytest.fail(
                    f"DataManager crashed loading garbage file. Content: {file_content[:20]}... Error: {e}")
