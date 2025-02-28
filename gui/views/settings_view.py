import customtkinter as ctk
from typing import Callable
import json
import os
import logging
import sys

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 配置主框架
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 设置默认字体
        self.title_font = ctk.CTkFont(size=24, weight="bold")
        self.section_font = ctk.CTkFont(size=18, weight="bold")
        self.label_font = ctk.CTkFont(size=14)

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
        self.title_label.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="nw")

        # 创建滚动容器
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

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
        separator = ctk.CTkFrame(self.scrollable_frame, height=2)
        separator.grid(row=row, column=0, sticky="ew", padx=20, pady=(30, 10))

        # 创建标签
        label = ctk.CTkLabel(
            self.scrollable_frame,
            text=text,
            font=self.section_font,
            text_color=("gray10", "gray90")
        )
        label.grid(row=row+1, column=0, padx=20, pady=(10, 20), sticky="w")
        return row + 2

    def create_setting_item(self, label_text: str, placeholder: str,
                          is_password: bool = False, width: int = 250) -> ctk.CTkFrame:
        """创建设置项框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 标签列不伸缩
        frame.grid_columnconfigure(1, weight=0)  # 输入框列不伸缩

        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75")
        )
        label.grid(row=0, column=0, padx=(20, 15), pady=12, sticky="w")

        # 生成一个统一的属性名
        attr_map = {
            "域名 (DOMAIN)": "domain",
            "临时邮箱 (TEMP_MAIL)": "temp_mail",
            "IMAP 服务器": "imap_server",
            "IMAP 端口": "imap_port",
            "IMAP 用户": "imap_user",
            "IMAP 密码": "imap_pass",
            "User Agent": "user_agent",
            "浏览器路径": "browser_path",
            "代理服务器": "proxy",
            "重试次数": "retry"
        }

        attr_name = attr_map.get(label_text, label_text.lower().replace(" ", "_"))
        attr_name = f"{attr_name}_entry"

        # 对于域名使用文本框
        if label_text == "域名 (DOMAIN)":
            entry = ctk.CTkTextbox(
                frame,
                width=width,
                height=80,  # 设置文本框高度
                font=self.label_font,
                wrap="word"  # 启用自动换行
            )
            entry.insert("1.0", placeholder)  # 设置占位符
            # 添加焦点事件来处理占位符
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
        entry.grid(row=0, column=1, padx=(0, 20), pady=12, sticky="w")

        # 保存组件引用
        setattr(self, attr_name, entry)

        # 调试日志
        logging.debug(f"Created setting item with attribute name: {attr_name}")
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
        frame.grid_columnconfigure(0, weight=0)  # 标签列不伸缩
        frame.grid_columnconfigure(1, weight=0)  # 选项列不伸缩

        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75")
        )
        label.grid(row=0, column=0, padx=(20, 15), pady=12, sticky="w")

        # 选项属性名映射
        option_map = {
            "IMAP 协议": "imap_protocol",
            "日志级别": "log_level",
            "外观模式": "appearance_mode"
        }

        # 生成属性名
        attr_name = option_map.get(label_text, label_text.lower().replace(" ", "_"))
        attr_name = f"{attr_name}_option"

        option = ctk.CTkOptionMenu(
            frame,
            values=values,
            command=command,
            width=250,
            height=32,
            font=self.label_font,
            dropdown_font=self.label_font
        )
        option.grid(row=0, column=1, padx=(0, 20), pady=12, sticky="w")
        option.set(values[0])

        # 保存组件引用
        setattr(self, attr_name, option)

        # 调试日志
        logging.debug(f"Created option item with attribute name: {attr_name}")
        return frame

    def create_switch_item(self, label_text: str, default_value: bool = False) -> ctk.CTkFrame:
        """创建开关框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 开关列不伸缩

        # 开关属性名映射
        switch_map = {
            "无头模式": "headless"
        }

        # 生成属性名
        attr_name = switch_map.get(label_text, label_text.lower().replace(" ", "_"))
        attr_name = f"{attr_name}_switch"

        switch = ctk.CTkSwitch(
            frame,
            text=label_text,
            font=self.label_font,
            height=32,
            switch_height=16,
            switch_width=40,
            text_color=("gray25", "gray75")
        )
        switch.grid(row=0, column=0, padx=20, pady=12, sticky="w")
        if default_value:
            switch.select()

        # 保存组件引用
        setattr(self, attr_name, switch)

        # 调试日志
        logging.debug(f"Created switch item with attribute name: {attr_name}")
        return frame

    def create_browser_path_item(self, label_text: str, placeholder: str) -> ctk.CTkFrame:
        """创建浏览器路径选择框架"""
        frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)  # 标签列不伸缩
        frame.grid_columnconfigure(1, weight=0)  # 输入框列不伸缩
        frame.grid_columnconfigure(2, weight=0)  # 按钮列不伸缩

        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75")
        )
        label.grid(row=0, column=0, padx=(20, 15), pady=12, sticky="w")

        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            width=400,
            height=32,
            font=self.label_font,
            border_width=2
        )
        entry.grid(row=0, column=1, padx=(0, 10), pady=12, sticky="w")

        # 添加选择按钮
        select_button = ctk.CTkButton(
            frame,
            text="选择",
            width=60,
            height=32,
            command=lambda: self._select_browser_path(entry)
        )
        select_button.grid(row=0, column=2, padx=(0, 20), pady=12, sticky="w")

        # 设置默认值
        default_path = self.default_browser_paths.get('darwin', '')
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
                "domain": self.domain_entry.get("1.0", "end-1c") if isinstance(self.domain_entry, ctk.CTkTextbox) else self.domain_entry.get(),
                "temp_mail": self.temp_mail_entry.get() or "null",

                # IMAP 设置
                "imap_server": self.imap_server_entry.get(),
                "imap_port": self.imap_port_entry.get(),
                "imap_user": self.imap_user_entry.get(),
                "imap_pass": self.imap_pass_entry.get(),
                "imap_protocol": self.imap_protocol_option.get(),

                # 浏览器设置
                "browser_user_agent": self.user_agent_entry.get(),
                "browser_headless": self.headless_switch.get(),
                "browser_path": self.browser_path_entry.get(),

                # 代理设置
                "proxy": self.proxy_entry.get(),

                # 自动化设置
                "retry_count": int(self.retry_entry.get() or 3),

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

    def load_settings(self):
        """从文件加载设置"""
        try:
            if os.path.exists("config/settings.json"):
                with open("config/settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)

                # 更新界面
                self._update_entry_if_exists("domain", settings)
                self._update_entry_if_exists("temp_mail", settings)
                self._update_entry_if_exists("imap_server", settings)
                self._update_entry_if_exists("imap_port", settings)
                self._update_entry_if_exists("imap_user", settings)
                self._update_entry_if_exists("imap_pass", settings)

                if "imap_protocol" in settings:
                    self.imap_protocol_option.set(settings["imap_protocol"])

                self._update_entry_if_exists("user_agent", settings, "browser_user_agent")
                self._update_entry_if_exists("browser_path", settings)

                if "browser_headless" in settings:
                    if settings["browser_headless"]:
                        self.headless_switch.select()
                    else:
                        self.headless_switch.deselect()

                self._update_entry_if_exists("proxy", settings)
                self._update_entry_if_exists("retry_count", settings)

                if "log_level" in settings:
                    self.log_level_option.set(settings["log_level"])
                    logging.getLogger().setLevel(settings["log_level"])

                if "appearance_mode" in settings:
                    self.appearance_mode_option.set(settings["appearance_mode"])
                    self.change_appearance_mode(settings["appearance_mode"])

        except Exception as e:
            logging.error(f"加载设置失败: {str(e)}")

    def _update_entry_if_exists(self, entry_name: str, settings: dict, settings_key: str = None):
        """更新输入框的值"""
        if not settings_key:
            settings_key = entry_name

        entry = getattr(self, f"{entry_name}_entry", None)
        if entry and settings_key in settings:
            if isinstance(entry, ctk.CTkTextbox):
                entry.delete("1.0", "end")
                entry.insert("1.0", str(settings[settings_key]))
            else:
                entry.delete(0, "end")
                entry.insert(0, str(settings[settings_key]))