import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'budget_app'))

from utils import validate_date
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add budget_app directory to sys.path



class TestValidateDate:

    @pytest.fixture
    def mock_datetime(self):
        with patch('utils.datetime') as mock_dt:
            # Set "now" to 2023-01-01
            mock_dt.now.return_value = datetime(2023, 1, 1)
            mock_dt.side_effect = lambda *args, **kwargs: datetime(
                *args, **kwargs)
            yield mock_dt

    def test_valid_date(self):
        # 2022-12-31 is before 2023-01-01 (assuming now is 2023)
        # But wait, validate_date uses datetime.now() directly.
        # If I run this test in 2025, 2022 is valid.
        # Let's just use a past date relative to real now, or mock it.
        # Using real dates is easier if we pick something definitely in the past.
        assert validate_date("2020", "1", "1") == (True, "日期有效")

    def test_leap_year_feb_29(self):
        assert validate_date("2020", "2", "29") == (True, "日期有效")

    def test_non_leap_year_feb_28(self):
        assert validate_date("2021", "2", "28") == (True, "日期有效")

    def test_invalid_year_format(self):
        assert validate_date("abc", "1", "1") == (False, "日期必须为数字")

    def test_invalid_month_format(self):
        assert validate_date("2020", "a", "1") == (False, "日期必须为数字")

    def test_invalid_day_format(self):
        assert validate_date("2020", "1", "a") == (False, "日期必须为数字")

    def test_year_too_small(self):
        assert validate_date("1899", "1", "1") == (False, "年份必须在1900-2100之间")

    def test_year_too_large(self):
        assert validate_date("2101", "1", "1") == (False, "年份必须在1900-2100之间")

    def test_month_too_small(self):
        assert validate_date("2020", "0", "1") == (False, "月份必须在1-12之间")

    def test_month_too_large(self):
        assert validate_date("2020", "13", "1") == (False, "月份必须在1-12之间")

    def test_day_too_small(self):
        # This is caught by 1 <= day_int <= days_in_month
        # days_in_month[0] is 31. 0 is < 1.
        assert validate_date("2020", "1", "0") == (False, "1月没有0号")

    def test_day_too_large_jan(self):
        assert validate_date("2020", "1", "32") == (False, "1月没有32号")

    def test_day_too_large_feb_leap(self):
        assert validate_date("2020", "2", "30") == (False, "2月没有30号")

    def test_day_too_large_feb_non_leap(self):
        assert validate_date("2021", "2", "29") == (False, "2月没有29号")

    def test_future_date(self):
        # Need to mock datetime.now() to ensure this test is stable
        # Or use a date far in the future like 2099 (valid year range is up to 2100)
        # If today is 2025, 2099 is future.
        assert validate_date("2099", "1", "1") == (False, "不能选择未来日期")

    def test_today(self):
        now = datetime.now()
        assert validate_date(str(now.year), str(now.month),
                             str(now.day)) == (True, "日期有效")
