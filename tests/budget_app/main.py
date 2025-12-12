from login_window import LoginWindow
from main_window import MainWindow
from models import data_manager

def main():
    # 加载数据
    data_manager.load_data()
    def on_login_success():
        main_app = MainWindow()
        main_app.run()
    
    login_app = LoginWindow(on_login_success)
    login_app.run()

if __name__ == "__main__":
    main()