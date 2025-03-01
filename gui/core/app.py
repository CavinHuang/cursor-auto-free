import customtkinter as ctk
import sys
import os
from PIL import Image
import logging

# 导入视图
from ..views.settings_view import SettingsView
from ..views.log_view import LogView
from .automation_manager import AutomationManager
from .account_manager import AccountManager

# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CursorProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 配置主窗口
        self.title("Cursor Pro 自动化工具")
        self.geometry("1000x700")

        # 配置日志
        logging.basicConfig(level=logging.INFO)

        # 创建主框架
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 初始化账号管理器
        self.account_manager = AccountManager()

        # 创建选项卡视图
        self.create_tab_view()

        # 创建状态栏
        self.create_status_bar()

        # 初始化自动化管理器
        self.automation_manager = AutomationManager(
            on_status_change=self.update_status,
            on_progress=self.add_log
        )
        self.automation_manager.parent_app = self  # 添加对GUI的引用

    def create_tab_view(self):
        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="nsew")

        # 添加选项卡
        self.tab_home = self.tabview.add("主页")
        self.tab_settings = self.tabview.add("设置")
        self.tab_logs = self.tabview.add("日志")

        # 配置选项卡网格
        for tab in [self.tab_home, self.tab_settings, self.tab_logs]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(2, weight=1)

        # 创建主页内容
        self.create_home_tab()

        # 创建设置页面
        self.settings_view = SettingsView(self.tab_settings)
        self.settings_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # 创建日志页面
        self.log_view = LogView(self.tab_logs)
        self.log_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def create_home_tab(self):
        # 账号信息框架
        self.account_frame = ctk.CTkFrame(self.tab_home)
        self.account_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # 账号信息标签
        self.account_info = {
            "email": ctk.CTkLabel(self.account_frame, text="当前账号: 未登录", font=ctk.CTkFont(size=14)),
            "created": ctk.CTkLabel(self.account_frame, text="创建时间: -", font=ctk.CTkFont(size=14)),
            "valid_until": ctk.CTkLabel(self.account_frame, text="有效期至: -", font=ctk.CTkFont(size=14)),
            "remaining": ctk.CTkLabel(self.account_frame, text="剩余天数: -", font=ctk.CTkFont(size=14))
        }

        # 布局账号信息
        row = 0
        for label in self.account_info.values():
            label.grid(row=row, column=0, padx=10, pady=2, sticky="w")
            row += 1

        # 状态指示器
        self.status_indicator = ctk.CTkLabel(self.tab_home, text="状态: 未运行",
                                           font=ctk.CTkFont(size=14))
        self.status_indicator.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # 控制按钮
        self.control_frame = ctk.CTkFrame(self.tab_home)
        self.control_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.start_button = ctk.CTkButton(self.control_frame, text="开始运行",
                                         command=self.start_automation)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self.control_frame, text="停止",
                                        command=self.stop_automation,
                                        state="disabled")
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.reset_button = ctk.CTkButton(self.control_frame, text="重置机器码",
                                         command=self.reset_machine_id)
        self.reset_button.grid(row=0, column=2, padx=10, pady=10)

        # 日志区域
        self.log_frame = ctk.CTkFrame(self.tab_home)
        self.log_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(self.log_frame)
        self.log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 更新账号显示
        self.update_account_display()

    def update_account_display(self):
        """更新账号信息显示"""
        account_info = self.account_manager.get_account_info()

        self.account_info["email"].configure(text=f"当前账号: {account_info['email']}")
        self.account_info["created"].configure(text=f"创建时间: {account_info['created_at']}")
        self.account_info["valid_until"].configure(text=f"有效期至: {account_info['valid_until']}")
        self.account_info["remaining"].configure(text=f"剩余天数: {account_info['remaining_days']} 天")

    def create_status_bar(self):
        # 状态栏
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=1, column=0, sticky="ew")

        self.status_label = ctk.CTkLabel(self.status_bar, text="就绪")
        self.status_label.grid(row=0, column=0, padx=10)

    def update_status(self, status: str):
        """更新状态显示"""
        self.status_indicator.configure(text=f"状态: {status}")
        self.status_label.configure(text=status)

    def add_log(self, message: str):
        """添加日志"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def start_automation(self):
        """开始自动化任务"""
        config = self.settings_view.get_settings()
        self.automation_manager.start_automation(config)
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.reset_button.configure(state="disabled")

    def stop_automation(self):
        """停止自动化任务"""
        self.automation_manager.stop_automation()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.reset_button.configure(state="normal")

    def reset_machine_id(self):
        """重置机器码"""
        self.reset_button.configure(state="disabled")
        try:
            if self.automation_manager.reset_machine_id():
                self.add_log("机器码重置成功")
            else:
                self.add_log("机器码重置失败")
        finally:
            self.reset_button.configure(state="normal")

def main():
    app = CursorProApp()
    app.mainloop()

if __name__ == "__main__":
    main()