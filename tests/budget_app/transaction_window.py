import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import transactions, categories, data_manager
from utils import validate_date


class TransactionWindow:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        # 标题
        tk.Label(self.frame, text="记账管理", font=("Arial", 16)).pack(pady=10)

        # 表单框架
        form_frame = tk.Frame(self.frame)
        form_frame.pack(pady=10, padx=20, fill="x")

        # 金额
        tk.Label(form_frame, text="金额:").grid(
            row=0, column=0, sticky="w", pady=5)
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

        # 类型
        tk.Label(form_frame, text="类型:").grid(
            row=1, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="支出")
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var,
                                  values=["支出", "收入"], state="readonly")
        type_combo.grid(row=1, column=1, pady=5, padx=5, sticky="ew")

        # 类别
        tk.Label(form_frame, text="类别:").grid(
            row=2, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var,
                                      values=categories, state="readonly")
        category_combo.grid(row=2, column=1, pady=5, padx=5, sticky="ew")

        # 日期
        tk.Label(form_frame, text="日期:").grid(
            row=3, column=0, sticky="w", pady=5)
        date_frame = tk.Frame(form_frame)
        date_frame.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        today = datetime.now()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=str(today.month))
        self.day_var = tk.StringVar(value=str(today.day))

        tk.Entry(date_frame, textvariable=self.year_var,
                 width=5).pack(side="left")
        tk.Label(date_frame, text="年").pack(side="left")
        tk.Entry(date_frame, textvariable=self.month_var,
                 width=3).pack(side="left")
        tk.Label(date_frame, text="月").pack(side="left")
        tk.Entry(date_frame, textvariable=self.day_var,
                 width=3).pack(side="left")
        tk.Label(date_frame, text="日").pack(side="left")

        # 备注
        tk.Label(form_frame, text="备注:").grid(
            row=4, column=0, sticky="w", pady=5)
        self.note_entry = tk.Entry(form_frame)
        self.note_entry.grid(row=4, column=1, pady=5, padx=5, sticky="ew")

        # 按钮
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="添加记录", command=self.add_transaction,
                  bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="清空", command=self.clear_form,
                  bg="#FF9800", fg="white").pack(side="left", padx=5)

        # 配置列权重
        form_frame.columnconfigure(1, weight=1)

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            transaction_type = self.type_var.get()
            note = self.note_entry.get()

            # 验证日期
            year = self.year_var.get()
            month = self.month_var.get()
            day = self.day_var.get()

            is_valid, message = validate_date(year, month, day)
            if not is_valid:
                messagebox.showerror("错误", f"日期无效: {message}")
                return

            if not category:
                messagebox.showerror("错误", "请选择类别！")
                return

            if amount <= 0:
                messagebox.showerror("错误", "金额必须大于0！")
                return

            # 创建交易记录
            from models import Transaction
            date_str = f"{int(year)}-{int(month):02d}-{int(day):02d}"
            transaction = Transaction(
                amount, category, date_str, transaction_type, note)

            # 保存数据
            data_manager.add_transaction(transaction)

            messagebox.showinfo("成功", "交易记录添加成功！")
            self.clear_form()

        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的金额！")

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.category_var.set("")
        self.type_var.set("支出")

        today = datetime.now()
        self.year_var.set(str(today.year))
        self.month_var.set(str(today.month))
        self.day_var.set(str(today.day))

    def show(self):
        self.frame.pack(fill="both", expand=True)

    def hide(self):
        self.frame.pack_forget()
