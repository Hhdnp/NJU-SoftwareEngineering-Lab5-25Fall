import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models import transactions, budgets, data_manager, categories

class PlaceholderEntry(tk.Entry):
    """支持占位符文本的 Entry 组件"""
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['fg']
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        
        self._put_placeholder()
    
    def _put_placeholder(self):
        """显示占位符文本"""
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)
    
    def _on_focus_in(self, event):
        """获得焦点时移除占位符"""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg_color)
    
    def _on_focus_out(self, event):
        """失去焦点时，如果为空则显示占位符"""
        if not self.get():
            self._put_placeholder()
    
    def get_content(self):
        """获取真实内容（如果不是占位符）"""
        content = self.get()
        if content == self.placeholder:
            return ""
        return content

class BudgetWindow:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        # 标题
        tk.Label(self.frame, text="预算管理", font=("Arial", 16)).pack(pady=10)
        
        # 预算设置框架
        budget_frame = tk.LabelFrame(self.frame, text="预算设置")
        budget_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(budget_frame, text="月度预算:").grid(row=0, column=0, sticky="w", pady=5)
        self.budget_entry = tk.Entry(budget_frame)
        self.budget_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.budget_entry.insert(0, str(budgets[0].amount))
        
        tk.Button(budget_frame, text="更新预算", command=self.update_budget,
                 bg="#4CAF50", fg="white").grid(row=0, column=2, padx=5)
        
        budget_frame.columnconfigure(1, weight=1)
        
        # 月度概览框架
        overview_frame = tk.LabelFrame(self.frame, text="月度概览")
        overview_frame.pack(fill="x", padx=20, pady=10)
        
        self.budget_label = tk.Label(overview_frame, text="预算: 0")
        self.budget_label.pack(side="left", padx=10)
        
        self.expense_label = tk.Label(overview_frame, text="支出: 0")
        self.expense_label.pack(side="left", padx=10)
        
        self.income_label = tk.Label(overview_frame, text="收入: 0")
        self.income_label.pack(side="left", padx=10)
        
        self.balance_label = tk.Label(overview_frame, text="余额: 0")
        self.balance_label.pack(side="left", padx=10)
        
        # 搜索框架
        search_frame = tk.LabelFrame(self.frame, text="交易记录搜索与筛选")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # 第一行：搜索框和搜索列选择
        row1 = tk.Frame(search_frame)
        row1.pack(fill="x", pady=5)
        
        tk.Label(row1, text="搜索:").pack(side="left")
        self.search_entry = tk.Entry(row1)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_transactions)
        
        tk.Label(row1, text="搜索列:").pack(side="left", padx=(10, 0))
        self.search_column = tk.StringVar(value="全部")
        search_column_combo = ttk.Combobox(row1, textvariable=self.search_column, 
                                          values=["全部", "日期", "类型", "类别", "金额", "备注"],
                                          state="readonly", width=8)
        search_column_combo.pack(side="left", padx=5)
        search_column_combo.bind('<<ComboboxSelected>>', self.search_transactions)
        
        # 第二行：筛选条件
        row2 = tk.Frame(search_frame)
        row2.pack(fill="x", pady=5)
        
        # 类型筛选
        tk.Label(row2, text="类型:").pack(side="left")
        self.type_filter = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(row2, textvariable=self.type_filter,
                                 values=["全部", "支出", "收入"], state="readonly", width=8)
        type_combo.pack(side="left", padx=5)
        type_combo.bind('<<ComboboxSelected>>', self.search_transactions)
        
        # 类别筛选
        tk.Label(row2, text="类别:").pack(side="left", padx=(10, 0))
        self.category_filter = tk.StringVar(value="全部")
        category_combo = ttk.Combobox(row2, textvariable=self.category_filter,
                                     values=["全部"] + categories, state="readonly", width=8)
        category_combo.pack(side="left", padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.search_transactions)
        
        # 金额范围筛选
        tk.Label(row2, text="金额范围:").pack(side="left", padx=(10, 0))
        self.amount_min = tk.StringVar()
        amount_min_entry = tk.Entry(row2, textvariable=self.amount_min, width=6)
        amount_min_entry.pack(side="left")
        tk.Label(row2, text="-").pack(side="left")
        self.amount_max = tk.StringVar()
        amount_max_entry = tk.Entry(row2, textvariable=self.amount_max, width=6)
        amount_max_entry.pack(side="left")
        self.amount_min.trace('w', self.search_transactions)
        self.amount_max.trace('w', self.search_transactions)
        
        # 日期范围筛选
        tk.Label(row2, text="日期:").pack(side="left", padx=(10, 0))
        self.date_start = PlaceholderEntry(row2, width=10, placeholder="开始日期")
        self.date_start.pack(side="left")
        tk.Label(row2, text="-").pack(side="left")
        self.date_end = PlaceholderEntry(row2, width=10, placeholder="结束日期")
        self.date_end.pack(side="left")
        
        # 绑定日期输入框的事件
        self.date_start.bind('<KeyRelease>', self.search_transactions)
        self.date_end.bind('<KeyRelease>', self.search_transactions)
        
        # 添加日期格式提示
        tk.Label(row2, text="(格式: YYYY-MM-DD)", font=("Arial", 8), fg="gray").pack(side="left", padx=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="删除选中", command=self.delete_selected,
                 bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="清空筛选", command=self.clear_filters,
                 bg="#9E9E9E", fg="white").pack(side="left", padx=5)
        tk.Button(button_frame, text="刷新", command=self.update_display,
                 bg="#2196F3", fg="white").pack(side="left", padx=5)
        
        # 交易记录表格
        columns = ("日期", "类型", "类别", "金额", "备注")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=15)
        
        # 设置列宽
        self.tree.column("日期", width=100)
        self.tree.column("类型", width=80)
        self.tree.column("类别", width=80)
        self.tree.column("金额", width=100)
        self.tree.column("备注", width=200)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=10)
        
        # 绑定双击事件查看详情
        self.tree.bind('<Double-1>', self.on_item_double_click)
    
    def update_budget(self):
        try:
            new_budget = float(self.budget_entry.get())
            if new_budget < 0:
                messagebox.showerror("错误", "预算不能为负数！")
                return
                
            budgets[0].amount = new_budget
            # 保存数据
            data_manager.save_data()
            self.update_display()
            messagebox.showinfo("成功", "预算更新成功！")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的预算金额！")
    
    def calculate_monthly_data(self):
        """计算月度数据"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_expense = 0
        monthly_income = 0
        
        for transaction in transactions:
            if transaction.date.startswith(current_month):
                if transaction.type == "支出":
                    monthly_expense += transaction.amount
                else:
                    monthly_income += transaction.amount
        
        return monthly_expense, monthly_income
    
    def search_transactions(self, *args):
        """搜索和筛选交易记录"""
        search_term = self.search_entry.get().lower()
        search_column = self.search_column.get()
        type_filter = self.type_filter.get()
        category_filter = self.category_filter.get()
        
        # 获取日期范围
        date_start = self.date_start.get_content()
        date_end = self.date_end.get_content()
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充数据
        for transaction in reversed(transactions):  # 最新的在前面
            # 检查搜索条件
            matches_search = False
            if not search_term:
                matches_search = True
            else:
                if search_column == "全部":
                    # 在所有列中搜索
                    matches_search = (
                        search_term in transaction.date or
                        search_term in transaction.type.lower() or
                        search_term in transaction.category.lower() or
                        search_term in str(transaction.amount) or
                        search_term in transaction.note.lower()
                    )
                else:
                    # 在指定列中搜索
                    if search_column == "日期":
                        matches_search = search_term in transaction.date
                    elif search_column == "类型":
                        matches_search = search_term in transaction.type.lower()
                    elif search_column == "类别":
                        matches_search = search_term in transaction.category.lower()
                    elif search_column == "金额":
                        matches_search = search_term in str(transaction.amount)
                    elif search_column == "备注":
                        matches_search = search_term in transaction.note.lower()
            
            # 检查类型筛选
            matches_type = (type_filter == "全部" or transaction.type == type_filter)
            
            # 检查类别筛选
            matches_category = (category_filter == "全部" or transaction.category == category_filter)
            
            # 检查金额范围
            matches_amount = True
            try:
                if self.amount_min.get():
                    min_val = float(self.amount_min.get())
                    if transaction.amount < min_val:
                        matches_amount = False
                if self.amount_max.get():
                    max_val = float(self.amount_max.get())
                    if transaction.amount > max_val:
                        matches_amount = False
            except ValueError:
                pass  # 如果输入的不是有效数字，忽略金额筛选
            
            # 检查日期范围
            matches_date = True
            if date_start:
                if transaction.date < date_start:
                    matches_date = False
            if date_end:
                if transaction.date > date_end:
                    matches_date = False
            
            # 如果所有条件都满足，显示记录
            if matches_search and matches_type and matches_category and matches_amount and matches_date:
                self.tree.insert("", "end", values=(
                    transaction.date,
                    transaction.type,
                    transaction.category,
                    f"{transaction.amount:.2f}",
                    transaction.note
                ), tags=(transaction.transaction_id,))
    
    def delete_selected(self):
        """删除选中的交易记录"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的记录！")
            return
        
        # 确认删除
        result = messagebox.askyesno("确认删除", f"确定要删除这 {len(selected_items)} 条记录吗？")
        if not result:
            return
        
        # 获取要删除的交易ID
        transaction_ids_to_delete = []
        for item in selected_items:
            transaction_id = self.tree.item(item, "tags")[0]
            transaction_ids_to_delete.append(transaction_id)
        
        # 从数据中删除
        global transactions
        transactions = [tx for tx in transactions if tx.transaction_id not in transaction_ids_to_delete]
        
        # 保存数据
        data_manager.transactions = transactions
        data_manager.save_data()
        
        # 更新显示
        self.update_display()
        messagebox.showinfo("成功", f"已删除 {len(transaction_ids_to_delete)} 条记录")
    
    def on_item_double_click(self, event):
        """双击项目查看详情"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            values = self.tree.item(item, "values")
            # 这里可以添加编辑功能，暂时只显示详情
            messagebox.showinfo("交易详情", 
                              f"日期: {values[0]}\n"
                              f"类型: {values[1]}\n"
                              f"类别: {values[2]}\n"
                              f"金额: {values[3]}\n"
                              f"备注: {values[4]}")
    
    def clear_filters(self):
        """清空所有筛选条件"""
        self.search_entry.delete(0, tk.END)
        self.search_column.set("全部")
        self.type_filter.set("全部")
        self.category_filter.set("全部")
        self.amount_min.set("")
        self.amount_max.set("")
        
        # 清空日期输入框
        self.date_start.delete(0, tk.END)
        self.date_end.delete(0, tk.END)
        self.date_start._put_placeholder()
        self.date_end._put_placeholder()
        
        self.search_transactions()
    
    def update_display(self):
        """更新显示"""
        monthly_expense, monthly_income = self.calculate_monthly_data()
        budget = budgets[0].amount
        balance = budget - monthly_expense
        
        self.budget_label.config(text=f"预算: {budget:.2f}")
        self.expense_label.config(text=f"支出: {monthly_expense:.2f}")
        self.income_label.config(text=f"收入: {monthly_income:.2f}")
        
        # 根据余额设置颜色
        if balance >= 0:
            self.balance_label.config(text=f"余额: {balance:.2f}", fg="green")
        else:
            self.balance_label.config(text=f"超支: {-balance:.2f}", fg="red")
        
        # 更新表格
        self.search_transactions()
    
    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.update_display()
    
    def hide(self):
        self.frame.pack_forget()