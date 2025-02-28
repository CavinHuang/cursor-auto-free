import customtkinter as ctk
import sys
import os
from PIL import Image
import logging

# 导入视图
from ..views.settings_view import SettingsView
from ..views.log_view import LogView
from .automation_manager import AutomationManager

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

        # 初始化自动化管理器
        self.automation_manager = AutomationManager(
            on_status_change=self.update_status,
            on_progress=self.add_log
        )

        # 创建主框架
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 创建侧边栏
        self.create_sidebar()

        # 创建主内容区
        self.create_main_content()

        # 创建状态栏
        self.create_status_bar()

        # 初始化视图
        self.current_view = None
        self.show_home()

    def create_sidebar(self):
        # 侧边栏框架
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Cursor Pro",
                                      font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 导航按钮
        self.home_button = ctk.CTkButton(self.sidebar_frame, text="主页",
                                        command=self.show_home)
        self.home_button.grid(row=1, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="设置",
                                            command=self.show_settings)
        self.settings_button.grid(row=2, column=0, padx=20, pady=10)

        self.logs_button = ctk.CTkButton(self.sidebar_frame, text="日志",
                                        command=self.show_logs)
        self.logs_button.grid(row=3, column=0, padx=20, pady=10)

    def create_main_content(self):
        # 主内容框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # 状态指示器
        self.status_indicator = ctk.CTkLabel(self.main_frame, text="状态: 未运行",
                                           font=ctk.CTkFont(size=14))
        self.status_indicator.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # 控制按钮
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

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
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(self.log_frame)
        self.log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def create_status_bar(self):
        # 状态栏
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=3, column=1, sticky="ew")

        self.status_label = ctk.CTkLabel(self.status_bar, text="就绪")
        self.status_label.grid(row=0, column=0, padx=10)

    def show_home(self):
        self.clear_main_content()
        self.main_frame.grid()
        self.current_view = None
        logging.info("显示主页")

    def show_settings(self):
        self.clear_main_content()
        self.settings_view = SettingsView(self)
        self.settings_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.current_view = self.settings_view
        logging.info("显示设置页面")

    def show_logs(self):
        self.clear_main_content()
        self.log_view = LogView(self)
        self.log_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.current_view = self.log_view
        logging.info("显示日志页面")

    def clear_main_content(self):
        if self.current_view:
            self.current_view.grid_forget()
        self.main_frame.grid_forget()

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
        if hasattr(self, "settings_view"):
            config = self.settings_view.get_settings()
        else:
            config = {}

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