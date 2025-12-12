from datetime import datetime


def validate_date(year, month, day):
    """验证日期是否合法"""
    try:
        # 检查是否为数字
        year_int = int(year)
        month_int = int(month)
        day_int = int(day)

        # 检查范围
        if not (1900 <= year_int <= 2100):
            return False, "年份必须在1900-2100之间"
        if not (1 <= month_int <= 12):
            return False, "月份必须在1-12之间"

        # 检查每月天数
        days_in_month = [31, 29 if year_int % 4 == 0 and (year_int % 100 != 0 or year_int % 400 == 0) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if not (1 <= day_int <= days_in_month[month_int - 1]):
            return False, f"{month_int}月没有{day_int}号"

        # 检查是否为未来日期
        input_date = datetime(year_int, month_int, day_int)
        if input_date > datetime.now():
            return False, "不能选择未来日期"

        return True, "日期有效"

    except ValueError:
        return False, "日期必须为数字"
