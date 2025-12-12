import tkinter as tk
from tkinter import messagebox
from models import users


class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.window = tk.Tk()
        self.window.title("记账管理系统 - 登录")
        self.window.geometry("300x200")
        self.window.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # 标题
        tk.Label(self.window, text="记账管理系统", font=("Arial", 16)).pack(pady=20)

        # 用户名
        tk.Label(self.window, text="用户名:").pack()
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack(pady=5)

        # 密码
        tk.Label(self.window, text="密码:").pack()
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack(pady=5)

        # 登录按钮
        tk.Button(self.window, text="登录", command=self.login,
                  bg="#4CAF50", fg="white").pack(pady=10)

        # 绑定回车键
        self.window.bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # 验证登录
        for user in users:
            if user.username == username and user.password == password:
                self.window.destroy()
                self.on_login_success()
                return

        messagebox.showerror("错误", "用户名或密码错误！")

    def run(self):
        self.window.mainloop()
