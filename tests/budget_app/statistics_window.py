import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from models import transactions, categories


class StatisticsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        plt.rcParams['font.family'] = 'SimHei'
        self.create_widgets()

    def create_widgets(self):
        # 标题
        tk.Label(self.frame, text="统计报表", font=("Arial", 16)).pack(pady=10)

        # 控制框架
        control_frame = tk.Frame(self.frame)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="统计类型:").pack(side="left")
        self.stats_type = tk.StringVar(value="daily")
        ttk.Radiobutton(control_frame, text="按日", variable=self.stats_type,
                        value="daily", command=self.update_charts).pack(side="left", padx=5)
        ttk.Radiobutton(control_frame, text="按月", variable=self.stats_type,
                        value="monthly", command=self.update_charts).pack(side="left", padx=5)

        # 图表框架
        self.chart_frame = tk.Frame(self.frame)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.update_charts()

    def get_transaction_data(self):
        """获取交易数据"""
        expense_data = {}
        income_data = {}
        category_data = {category: 0 for category in categories}

        for transaction in transactions:
            date_obj = datetime.strptime(transaction.date, "%Y-%m-%d")

            if self.stats_type.get() == "daily":
                key = transaction.date
            else:  # monthly
                key = f"{date_obj.year}-{date_obj.month:02d}"

            if transaction.type == "支出":
                if key not in expense_data:
                    expense_data[key] = 0
                expense_data[key] += transaction.amount
                category_data[transaction.category] += transaction.amount
            else:
                if key not in income_data:
                    income_data[key] = 0
                income_data[key] += transaction.amount

        return expense_data, income_data, category_data

    def update_charts(self):
        """更新图表"""
        # 清除现有图表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        expense_data, income_data, category_data = self.get_transaction_data()

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 折线图
        if expense_data or income_data:
            dates = sorted(
                set(list(expense_data.keys()) + list(income_data.keys())))
            expense_values = [expense_data.get(date, 0) for date in dates]
            income_values = [income_data.get(date, 0) for date in dates]

            ax1.plot(dates, expense_values, 'r-', label='支出', marker='o')
            ax1.plot(dates, income_values, 'g-', label='收入', marker='o')
            ax1.set_title(
                f"{'每日' if self.stats_type.get() == 'daily' else '每月'}收支趋势")
            ax1.set_xlabel('时间')
            ax1.set_ylabel('金额')
            ax1.legend()
            ax1.tick_params(axis='x', rotation=45)

        # 饼图
        if any(category_data.values()):
            labels = [cat for cat, amount in category_data.items()
                      if amount > 0]
            sizes = [amount for amount in category_data.values() if amount > 0]

            if labels and sizes:
                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax2.set_title('支出类别占比')

        plt.tight_layout()

        # 嵌入到tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.update_charts()

    def hide(self):
        self.frame.pack_forget()
