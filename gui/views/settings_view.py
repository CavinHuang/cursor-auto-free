import customtkinter as ctk
from typing import Callable
import json
import os
import logging
import sys
from datetime import datetime, timedelta

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 配置主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 设置默认字体
        self.title_font = ctk.CTkFont(size=20, weight="bold")
        self.section_font = ctk.CTkFont(size=16, weight="bold")
        self.label_font = ctk.CTkFont(size=13)

        # 设置默认的浏览器路径
        self.default_browser_paths = {
            "darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
            "linux": "/usr/bin/google-chrome",  # Linux
            "win32": r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # Windows
        }

        # 获取当前操作系统
        self.current_os = "darwin" if os.name == "posix" and sys.platform == "darwin" else \
                         "linux" if os.name == "posix" else "win32"

        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="系统设置",
            font=self.title_font,
            text_color=("gray10", "gray90")
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        # 账号信息区域
        self.account_frame = ctk.CTkFrame(self)
        self.account_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.account_frame.grid_columnconfigure(1, weight=1)

        # 账号信息标题
        account_title = ctk.CTkLabel(
            self.account_frame,
            text="账号信息",
            font=self.section_font,
            text_color=("gray10", "gray90")
        )
        account_title.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 账号
        account_label = ctk.CTkLabel(
            self.account_frame,
            text="账号：",
            font=self.label_font,
            text_color=("gray25", "gray75")
        )
        account_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")

        self.account_value = ctk.CTkLabel(
            self.account_frame,
            text="未登录",
            font=self.label_font
        )
        self.account_value.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        # 密码
        password_label = ctk.CTkLabel(
            self.account_frame,
            text="密码：",
            font=self.label_font,
            text_color=("gray25", "gray75")
        )
        password_label.grid(row=2, column=0, padx=10, pady=2, sticky="w")

        self.password_value = ctk.CTkLabel(
            self.account_frame,
            text="******",
            font=self.label_font
        )
        self.password_value.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        # 到期时间
        expiry_label = ctk.CTkLabel(
            self.account_frame,
            text="到期时间：",
            font=self.label_font,
            text_color=("gray25", "gray75")
        )
        expiry_label.grid(row=3, column=0, padx=10, pady=2, sticky="w")

        self.expiry_value = ctk.CTkLabel(
            self.account_frame,
            text="未知",
            font=self.label_font
        )
        self.expiry_value.grid(row=3, column=1, padx=10, pady=(2, 10), sticky="w")

        # 创建滚动容器
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=500,  # 设置固定高度
            scrollbar_button_color=("gray75", "gray15"),  # 优化滚动条按钮颜色
            scrollbar_button_hover_color=("gray85", "gray25")  # 优化滚动条悬停颜色
        )
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 10))

        # 配置滚动容器的网格
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame._scrollbar.grid_configure(padx=(0, 5))  # 调整滚动条位置

        current_row = 0

        # === 邮箱设置 ===
        self.create_section_label("📧 邮箱设置", current_row)
        current_row += 1

        # 域名设置
        self.domain_frame = self.create_setting_item("域名 (DOMAIN)", "你的 Cloudflare 域名")
        self.domain_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # 临时邮箱设置
        self.temp_mail_frame = self.create_setting_item("临时邮箱 (TEMP_MAIL)", "设置为 null 启用 IMAP 模式")
        self.temp_mail_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # === IMAP 设置 ===
        self.create_section_label("IMAP 设置", current_row)
        current_row += 1

        # IMAP 服务器
        self.imap_server_frame = self.create_setting_item("IMAP 服务器", "例如：imap.gmail.com")
        self.imap_server_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # IMAP 端口
        self.imap_port_frame = self.create_setting_item("IMAP 端口", "993")
        self.imap_port_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # IMAP 用户
        self.imap_user_frame = self.create_setting_item("IMAP 用户", "邮箱地址")
        self.imap_user_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # IMAP 密码
        self.imap_pass_frame = self.create_setting_item("IMAP 密码", "邮箱授权码", is_password=True)
        self.imap_pass_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # IMAP 协议
        self.imap_protocol_frame = self.create_option_item("IMAP 协议", ["IMAP", "POP3"])
        self.imap_protocol_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # === 浏览器设置 ===
        self.create_section_label("浏览器设置", current_row)
        current_row += 1

        # User Agent
        self.user_agent_frame = self.create_setting_item("User Agent", "浏览器 User Agent")
        self.user_agent_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # 无头模式
        self.headless_frame = self.create_switch_item("无头模式", True)
        self.headless_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # 浏览器路径
        self.browser_path_frame = self.create_browser_path_item(
            "浏览器路径",
            f"Chrome 浏览器路径，例如：{self.default_browser_paths.get('darwin', '')}"
        )
        self.browser_path_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # === 代理设置 ===
        self.create_section_label("代理设置", current_row)
        current_row += 1

        self.proxy_frame = self.create_setting_item("代理服务器", "http://proxy:port")
        self.proxy_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # === 自动化设置 ===
        self.create_section_label("自动化设置", current_row)
        current_row += 1

        # 重试次数
        self.retry_frame = self.create_setting_item("重试次数", "3", width=100)
        self.retry_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # === 日志设置 ===
        self.create_section_label("日志设置", current_row)
        current_row += 1

        # 日志级别
        self.log_level_frame = self.create_option_item("日志级别", ["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # === 主题设置 ===
        self.create_section_label("主题设置", current_row)
        current_row += 1

        # 外观模式
        self.appearance_frame = self.create_option_item("外观模式", ["Light", "Dark", "System"],
                                                      command=self.change_appearance_mode)
        self.appearance_frame.grid(row=current_row, column=0, pady=(5, 10))
        current_row += 1

        # 保存按钮
        self.save_button = ctk.CTkButton(self.scrollable_frame, text="保存设置",
                                        command=self.save_settings)
        self.save_button.grid(row=current_row, column=0, pady=20)

        # 加载已保存的设置
        self.load_settings()

    def create_section_label(self, text: str, row: int):
        """创建分节标签"""
        # 创建分隔线
        separator = ctk.CTkFrame(self.scrollable_frame, height=1)
        separator.grid(row=row, column=0, sticky="ew", padx=5, pady=(15, 5))

        # 创建标签
        label = ctk.CTkLabel(
            self.scrollable_frame,
            text=text,
            font=self.section_font,
            text_color=("gray10", "gray90")
        )
        label.grid(row=row+1, column=0, padx=5, pady=(5, 10), sticky="w")
        return row + 2

    def create_setting_item(self, label_text: str, placeholder: str,
                          is_password: bool = False, width: int = 400) -> ctk.CTkFrame:
        """创建设置项框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 不伸缩，保持靠左
        frame.grid_columnconfigure(1, weight=1)  # 右侧填充

        # 标签放在上面
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 输入框放在下面
        if label_text == "域名 (DOMAIN)":
            entry = ctk.CTkTextbox(
                frame,
                width=width,
                height=80,
                font=self.label_font,
                wrap="word"
            )
            entry.insert("1.0", placeholder)
            entry.bind("<FocusIn>", lambda e: self._on_textbox_focus_in(entry, placeholder))
            entry.bind("<FocusOut>", lambda e: self._on_textbox_focus_out(entry, placeholder))
        else:
            entry = ctk.CTkEntry(
                frame,
                placeholder_text=placeholder,
                show="*" if is_password else "",
                width=width,
                height=32,
                font=self.label_font,
                border_width=2
            )
        entry.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")

        setattr(self, f"{label_text.lower().replace(' ', '_')}_entry", entry)
        return frame

    def _on_textbox_focus_in(self, textbox: ctk.CTkTextbox, placeholder: str):
        """文本框获得焦点时的处理"""
        if textbox.get("1.0", "end-1c") == placeholder:
            textbox.delete("1.0", "end")

    def _on_textbox_focus_out(self, textbox: ctk.CTkTextbox, placeholder: str):
        """文本框失去焦点时的处理"""
        if not textbox.get("1.0", "end-1c").strip():
            textbox.delete("1.0", "end")
            textbox.insert("1.0", placeholder)

    def create_option_item(self, label_text: str, values: list,
                          command: Callable = None) -> ctk.CTkFrame:
        """创建选项框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 不伸缩，保持靠左
        frame.grid_columnconfigure(1, weight=1)  # 右侧填充

        # 标签放在上面
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 选项菜单放在下面
        option = ctk.CTkOptionMenu(
            frame,
            values=values,
            command=command,
            width=400,
            height=32,
            font=self.label_font,
            dropdown_font=self.label_font
        )
        option.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        option.set(values[0])

        setattr(self, f"{label_text.lower().replace(' ', '_')}_option", option)
        return frame

    def create_switch_item(self, label_text: str, default_value: bool = False) -> ctk.CTkFrame:
        """创建开关框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 不伸缩，保持靠左
        frame.grid_columnconfigure(1, weight=1)  # 右侧填充

        # 标签放在上面
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 开关放在下面
        switch = ctk.CTkSwitch(
            frame,
            text="",  # 移除开关的文本
            height=32,
            switch_height=16,
            switch_width=40,
        )
        switch.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")

        if default_value:
            switch.select()

        setattr(self, f"{label_text.lower().replace(' ', '_')}_switch", switch)
        return frame

    def create_browser_path_item(self, label_text: str, placeholder: str) -> ctk.CTkFrame:
        """创建浏览器路径选择框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 不伸缩，保持靠左
        frame.grid_columnconfigure(1, weight=1)  # 右侧填充

        # 标签放在上面
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 创建一个子框架来容纳输入框和按钮
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        input_frame.grid_columnconfigure(0, weight=0)  # 输入框不伸缩
        input_frame.grid_columnconfigure(1, weight=0)  # 按钮不伸缩

        # 输入框和按钮放在下面
        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=placeholder,
            width=400,
            height=32,
            font=self.label_font,
            border_width=2
        )
        entry.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")

        select_button = ctk.CTkButton(
            input_frame,
            text="选择",
            width=60,
            height=32,
            command=lambda: self._select_browser_path(entry)
        )
        select_button.grid(row=0, column=1, padx=0, pady=0, sticky="w")

        # 设置默认值
        default_path = self.default_browser_paths.get(self.current_os, '')
        if os.path.exists(default_path):
            entry.insert(0, default_path)

        setattr(self, "browser_path_entry", entry)
        return frame

    def _select_browser_path(self, entry: ctk.CTkEntry):
        """选择浏览器路径"""
        from tkinter import filedialog
        import sys

        # 获取初始目录
        if sys.platform == "darwin":  # macOS
            initial_dir = "/Applications"
        elif sys.platform == "win32":  # Windows
            initial_dir = r"C:\Program Files"
        else:  # Linux
            initial_dir = "/usr/bin"

        # 根据操作系统设置文件类型
        if sys.platform == "darwin":
            filetypes = [("应用程序", "*.app"), ("所有文件", "*.*")]
        elif sys.platform == "win32":
            filetypes = [("可执行文件", "*.exe"), ("所有文件", "*.*")]
        else:
            filetypes = [("所有文件", "*.*")]

        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择浏览器可执行文件",
            initialdir=initial_dir,
            filetypes=filetypes
        )

        if file_path:
            # 如果选择的是 .app 文件，自动添加可执行文件路径
            if sys.platform == "darwin" and file_path.endswith('.app'):
                chrome_path = os.path.join(file_path, 'Contents/MacOS/Google Chrome')
                if os.path.exists(chrome_path) and os.access(chrome_path, os.X_OK):
                    file_path = chrome_path
                else:
                    self.show_error_message("所选应用程序不是有效的 Chrome 浏览器或没有执行权限")
                    return

            # 验证文件是否存在且可执行
            if not os.path.exists(file_path):
                self.show_error_message("所选文件不存在")
                return

            if not os.access(file_path, os.X_OK):
                self.show_error_message("所选文件没有执行权限")
                return

            # 更新输入框的值
            entry.delete(0, "end")
            entry.insert(0, file_path)

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode.lower())

    def get_settings(self) -> dict:
        """获取当前设置"""
        try:
            # 调试信息：打印所有的 entry 属性
            all_attrs = [attr for attr in dir(self) if attr.endswith('_entry')]
            logging.debug(f"Available entry attributes: {all_attrs}")

            settings = {
                # 邮箱设置
                "domain": self.domain_entry.get("1.0", "end-1c").strip() if isinstance(self.domain_entry, ctk.CTkTextbox) else self.domain_entry.get().strip(),
                "temp_mail": self.temp_mail_entry.get().strip() or "null",

                # IMAP 设置
                "imap_server": self.imap_server_entry.get().strip(),
                "imap_port": self.imap_port_entry.get().strip(),
                "imap_user": self.imap_user_entry.get().strip(),
                "imap_pass": self.imap_pass_entry.get().strip(),
                "imap_protocol": self.imap_protocol_option.get(),

                # 浏览器设置
                "browser_user_agent": self.user_agent_entry.get().strip(),
                "browser_headless": 1 if self.headless_switch.get() else 0,  # 转换为数字
                "browser_path": self.browser_path_entry.get().strip(),

                # 代理设置
                "proxy": self.proxy_entry.get().strip(),

                # 自动化设置
                "retry_count": int(self.retry_entry.get().strip() or 3),

                # 其他设置
                "log_level": self.log_level_option.get(),
                "appearance_mode": self.appearance_mode_option.get()
            }

            # 调试日志
            logging.debug(f"Retrieved settings: {settings}")
            return settings

        except AttributeError as e:
            logging.error(f"获取设置时出错: {str(e)}")
            self.show_error_message(f"获取设置失败: {str(e)}\n请确保所有必填项都已填写。")
            return {}

    def save_settings(self):
        """保存设置到文件"""
        settings = self.get_settings()
        os.makedirs("config", exist_ok=True)

        try:
            # 保存到 settings.json
            with open("config/settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            # 生成 .env 文件
            env_content = [
                f"DOMAIN='{settings['domain']}'",
                f"TEMP_MAIL={settings['temp_mail']}",
                "",
                "# IMAP服务器配置",
                f"IMAP_SERVER={settings['imap_server']}",
                f"IMAP_PORT={settings['imap_port']}",
                f"IMAP_USER={settings['imap_user']}",
                f"IMAP_PASS={settings['imap_pass']}",
                f"IMAP_PROTOCOL={settings['imap_protocol']}",
                "",
                f"BROWSER_USER_AGENT={settings['browser_user_agent']}",
                "",
                f"BROWSER_HEADLESS='{str(settings['browser_headless'])}'",
                "",
                "# 浏览器路径",
                f"BROWSER_PATH='{settings['browser_path']}'"
            ]

            with open(".env", "w", encoding="utf-8") as f:
                f.write("\n".join(env_content))

            # 更新日志级别
            logging.getLogger().setLevel(settings["log_level"])
            logging.info("设置已保存")

            # 显示保存成功提示
            self.show_success_message()
        except Exception as e:
            logging.error(f"保存设置失败: {str(e)}")
            self.show_error_message(str(e))

    def show_success_message(self):
        """显示保存成功提示"""
        success_window = ctk.CTkToplevel(self)
        success_window.title("成功")
        success_window.geometry("300x150")
        success_window.resizable(False, False)

        # 居中显示
        success_window.update_idletasks()
        x = (success_window.winfo_screenwidth() - success_window.winfo_width()) // 2
        y = (success_window.winfo_screenheight() - success_window.winfo_height()) // 2
        success_window.geometry(f"+{x}+{y}")

        message = ctk.CTkLabel(
            success_window,
            text="设置已成功保存",
            font=ctk.CTkFont(size=16)
        )
        message.pack(pady=20)

        ok_button = ctk.CTkButton(
            success_window,
            text="确定",
            width=100,
            command=success_window.destroy
        )
        ok_button.pack(pady=10)

    def show_error_message(self, error_message: str):
        """显示错误提示"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("错误")
        error_window.geometry("400x200")
        error_window.resizable(False, False)

        # 居中显示
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() - error_window.winfo_width()) // 2
        y = (error_window.winfo_screenheight() - error_window.winfo_height()) // 2
        error_window.geometry(f"+{x}+{y}")

        message = ctk.CTkLabel(
            error_window,
            text=f"保存设置时出错：\n{error_message}",
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        message.pack(pady=20)

        ok_button = ctk.CTkButton(
            error_window,
            text="确定",
            width=100,
            command=error_window.destroy
        )
        ok_button.pack(pady=10)

    def update_account_info(self, account: str = None, password: str = None, register_time: str = None):
        """更新账号信息显示"""
        if account:
            self.account_value.configure(text=account)
        if password:
            self.password_value.configure(text="*" * len(password))

        if register_time:
            try:
                # 将注册时间字符串转换为datetime对象
                reg_time = datetime.strptime(register_time, "%Y-%m-%d %H:%M:%S")
                # 计算到期时间（注册时间+15天）
                expiry_time = reg_time + timedelta(days=15)
                # 格式化显示
                expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")
                self.expiry_value.configure(text=expiry_str)
            except Exception as e:
                logging.error(f"计算到期时间出错: {str(e)}")
                self.expiry_value.configure(text="计算错误")

    def load_settings(self):
        """从文件加载设置"""
        try:
            # 首先尝试从 settings.json 加载
            if os.path.exists("config/settings.json"):
                with open("config/settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                logging.info("从 settings.json 加载设置")
            # 如果 settings.json 不存在，尝试从 .env 加载
            elif os.path.exists(".env"):
                settings = {}
                with open(".env", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            try:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip().strip("'\"")  # 移除引号
                                settings[key.lower()] = value
                            except ValueError:
                                continue
                logging.info("从 .env 加载设置")
            else:
                logging.info("没有找到设置文件，使用默认设置")
                return

            # 更新界面，添加属性检查
            # 邮箱设置
            if hasattr(self, "domain_entry"):
                if isinstance(self.domain_entry, ctk.CTkTextbox):
                    self.domain_entry.delete("1.0", "end")
                    self.domain_entry.insert("1.0", str(settings.get("domain", "")))

            if hasattr(self, "temp_mail_entry"):
                self.temp_mail_entry.delete(0, "end")
                self.temp_mail_entry.insert(0, str(settings.get("temp_mail", "null")))

            # IMAP 设置
            if hasattr(self, "imap_server_entry"):
                self.imap_server_entry.delete(0, "end")
                self.imap_server_entry.insert(0, str(settings.get("imap_server", "")))

            if hasattr(self, "imap_port_entry"):
                self.imap_port_entry.delete(0, "end")
                self.imap_port_entry.insert(0, str(settings.get("imap_port", "993")))

            if hasattr(self, "imap_user_entry"):
                self.imap_user_entry.delete(0, "end")
                self.imap_user_entry.insert(0, str(settings.get("imap_user", "")))

            if hasattr(self, "imap_pass_entry"):
                self.imap_pass_entry.delete(0, "end")
                self.imap_pass_entry.insert(0, str(settings.get("imap_pass", "")))

            # IMAP 协议
            if hasattr(self, "imap_protocol_option"):
                protocol = str(settings.get("imap_protocol", "IMAP"))
                if protocol in ["IMAP", "POP3"]:
                    self.imap_protocol_option.set(protocol)

            # 浏览器设置
            if hasattr(self, "user_agent_entry"):
                self.user_agent_entry.delete(0, "end")
                self.user_agent_entry.insert(0, str(settings.get("browser_user_agent", "")))

            if hasattr(self, "browser_path_entry"):
                self.browser_path_entry.delete(0, "end")
                self.browser_path_entry.insert(0, str(settings.get("browser_path", "")))

            # 无头模式
            if hasattr(self, "headless_switch"):
                if settings.get("browser_headless", 1):  # 1 表示开启
                    self.headless_switch.select()
                else:
                    self.headless_switch.deselect()

            # 代理设置
            if hasattr(self, "proxy_entry"):
                self.proxy_entry.delete(0, "end")
                self.proxy_entry.insert(0, str(settings.get("proxy", "")))

            # 重试次数
            if hasattr(self, "retry_entry"):
                self.retry_entry.delete(0, "end")
                self.retry_entry.insert(0, str(settings.get("retry_count", 3)))

            # 日志级别
            if hasattr(self, "log_level_option"):
                log_level = str(settings.get("log_level", "INFO"))
                if log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
                    self.log_level_option.set(log_level)
                    logging.getLogger().setLevel(log_level)

            # 外观模式
            if hasattr(self, "appearance_mode_option"):
                appearance = str(settings.get("appearance_mode", "System"))
                if appearance in ["Light", "Dark", "System"]:
                    self.appearance_mode_option.set(appearance)
                    self.change_appearance_mode(appearance)

            logging.info("设置加载完成")

        except Exception as e:
            logging.error(f"加载设置失败: {str(e)}")
            # 不显示错误消息框，只记录日志
            # self.show_error_message(f"加载设置失败: {str(e)}")