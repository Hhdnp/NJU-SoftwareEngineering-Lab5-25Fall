import tkinter as tk
from transaction_window import TransactionWindow
from statistics_window import StatisticsWindow
from budget_window import BudgetWindow


class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("记账管理系统")
        self.window.geometry("800x600")

        self.current_window = None
        self.windows = {}

        self.create_navigation()
        self.create_windows()
        self.show_window("transaction")

    def create_navigation(self):
        # 导航栏
        nav_frame = tk.Frame(self.window, bg="#333", height=50)
        nav_frame.pack(fill="x", side="bottom")
        nav_frame.pack_propagate(False)

        # 导航按钮
        buttons = [
            ("记账", "transaction"),
            ("统计", "statistics"),
            ("预算", "budget")
        ]

        for text, key in buttons:
            btn = tk.Button(nav_frame, text=text, command=lambda k=key: self.show_window(k),
                            bg="#555", fg="white", relief="flat", height=2)
            btn.pack(side="left", fill="x", expand=True)

    def create_windows(self):
        # 创建各个功能窗口
        self.windows["transaction"] = TransactionWindow(self.window)
        self.windows["statistics"] = StatisticsWindow(self.window)
        self.windows["budget"] = BudgetWindow(self.window)

    def show_window(self, window_key):
        # 隐藏当前窗口
        if self.current_window:
            self.current_window.hide()

        # 显示新窗口
        self.current_window = self.windows[window_key]
        self.current_window.show()

    def run(self):
        self.window.mainloop()
