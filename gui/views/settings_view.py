import customtkinter as ctk
from typing import Callable
import json
import os
import logging
import sys
import re
import platform

def get_app_config_dir():
    """获取应用配置目录"""
    if platform.system() == "Darwin":  # macOS
        app_data = os.path.expanduser("~/Library/Application Support/CursorPro")
    elif platform.system() == "Windows":  # Windows
        app_data = os.path.join(os.getenv("APPDATA"), "CursorPro")
    else:  # Linux
        app_data = os.path.expanduser("~/.config/cursorpro")

    config_dir = os.path.join(app_data, "config")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

class SettingsSection(ctk.CTkFrame):
    """设置部分的基类"""
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.title = title
        self.widgets = {}

        # 设置字体
        self.section_font = ctk.CTkFont(size=16, weight="bold")
        self.label_font = ctk.CTkFont(size=13)

        # 创建分隔线和标题
        separator = ctk.CTkFrame(self, height=1)
        separator.grid(row=0, column=0, sticky="ew", padx=5, pady=(10, 5))

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=self.section_font,
            text_color=("gray10", "gray90")
        )
        title_label.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")

        self.current_row = 2

    def add_setting_item(self, key, label_text, placeholder, is_password=False, width=400):
        """添加设置项"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=self.current_row, column=0, pady=(5, 10), sticky="ew")

        # 标签
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 域名特殊处理使用文本框
        if key == "domain":
            widget = ctk.CTkTextbox(
                frame,
                width=width,
                height=80,
                font=self.label_font,
                wrap="word"
            )
            widget._placeholder = placeholder
            widget._has_content = False
            widget.bind("<FocusIn>", lambda e: self._on_textbox_focus_in(widget))
            widget.bind("<FocusOut>", lambda e: self._on_textbox_focus_out(widget))
        else:
            widget = ctk.CTkEntry(
                frame,
                placeholder_text=placeholder,
                show="*" if is_password else "",
                width=width,
                height=32,
                font=self.label_font,
                border_width=2
            )

        widget.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        self.widgets[key] = widget
        self.current_row += 1
        return widget

    def add_option_item(self, key, label_text, values, command=None):
        """添加选项菜单项"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=self.current_row, column=0, pady=(5, 10), sticky="ew")

        # 标签
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 选项菜单
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

        self.widgets[key] = option
        self.current_row += 1
        return option

    def add_switch_item(self, key, label_text, default_value=False):
        """添加开关项"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=self.current_row, column=0, pady=(5, 10), sticky="ew")

        # 标签
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 开关
        switch = ctk.CTkSwitch(
            frame,
            text="",
            height=32,
            switch_height=16,
            switch_width=40,
        )
        switch.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")

        if default_value:
            switch.select()

        self.widgets[key] = switch
        self.current_row += 1
        return switch

    def add_browser_path_item(self, key, label_text, placeholder, default_path="", select_callback=None):
        """添加浏览器路径选择项"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=self.current_row, column=0, pady=(5, 10), sticky="ew")

        # 标签
        label = ctk.CTkLabel(
            frame,
            text=f"{label_text}:",
            font=self.label_font,
            text_color=("gray25", "gray75"),
        )
        label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="w", columnspan=2)

        # 子框架容纳输入框和按钮
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=5, pady=(5, 10), sticky="w")
        input_frame.grid_columnconfigure(0, weight=0)
        input_frame.grid_columnconfigure(1, weight=0)

        # 输入框和按钮
        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=placeholder,
            width=400,
            height=32,
            font=self.label_font,
            border_width=2
        )
        entry.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")

        # 如果有默认路径，填入
        if default_path and os.path.exists(default_path):
            entry.insert(0, default_path)

        select_button = ctk.CTkButton(
            input_frame,
            text="选择",
            width=60,
            height=32,
            command=lambda: select_callback(entry) if select_callback else None
        )
        select_button.grid(row=0, column=1, padx=0, pady=0, sticky="w")

        self.widgets[key] = entry
        self.current_row += 1
        return entry

    def _on_textbox_focus_in(self, textbox):
        """文本框获得焦点时的处理"""
        if not textbox._has_content:
            textbox.delete("1.0", "end")

    def _on_textbox_focus_out(self, textbox):
        """文本框失去焦点时的处理"""
        current_text = textbox.get("1.0", "end-1c").strip()
        if not current_text:
            textbox._has_content = False
            textbox.delete("1.0", "end")
            textbox.insert("1.0", textbox._placeholder)
        else:
            textbox._has_content = True

    def get_values(self):
        """获取所有设置项的值"""
        values = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, ctk.CTkTextbox):
                values[key] = widget.get("1.0", "end-1c").strip()
            elif isinstance(widget, ctk.CTkEntry):
                values[key] = widget.get().strip()
            elif isinstance(widget, ctk.CTkOptionMenu):
                values[key] = widget.get()
            elif isinstance(widget, ctk.CTkSwitch):
                values[key] = 1 if widget.get() else 0
        return values

    def set_values(self, values_dict):
        """设置所有项的值"""
        for key, widget in self.widgets.items():
            if key in values_dict:
                value = values_dict.get(key, "")
                if isinstance(widget, ctk.CTkTextbox):
                    widget.delete("1.0", "end")
                    if value:
                        widget.insert("1.0", value)
                        widget._has_content = True
                    else:
                        widget.insert("1.0", widget._placeholder)
                        widget._has_content = False
                elif isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, str(value))
                elif isinstance(widget, ctk.CTkOptionMenu):
                    if value in widget.cget("values"):
                        widget.set(value)
                elif isinstance(widget, ctk.CTkSwitch):
                    if value:
                        widget.select()
                    else:
                        widget.deselect()

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config_dir = get_app_config_dir()

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

        # 创建滚动容器
        self.scrollable_frame = ctk.CTkScrollableFrame(
            master=self,
            fg_color="transparent",
            height=500,  # 设置固定高度
            scrollbar_button_color=("gray75", "gray15"),  # 优化滚动条按钮颜色
            scrollbar_button_hover_color=("gray85", "gray25")  # 优化滚动条悬停颜色
        )
        self.scrollable_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)  # 让内容居中

        # 初始化设置部分
        self.sections = {}
        self.initialize_sections()

        # 添加底部填充框架
        bottom_padding = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent", height=20)
        bottom_padding.grid(row=len(self.sections)+2, column=0, sticky="ew")

        # 保存按钮放在填充框之前
        self.save_button = ctk.CTkButton(
            self.scrollable_frame,
            text="保存设置",
            command=self.save_settings,
            height=40,
            corner_radius=8
        )
        self.save_button.grid(row=len(self.sections)+1, column=0, pady=(20, 30), padx=20, sticky="ew")

        # 加载已保存的设置
        self.load_settings()

    def initialize_sections(self):
        """初始化所有设置部分"""
        current_row = 0

        # === 邮箱设置部分 ===
        email_section = SettingsSection(self.scrollable_frame, "📧 邮箱设置")
        email_section.grid(row=current_row, column=0, sticky="ew")
        email_section.add_setting_item("domain", "域名 (DOMAIN)", "你的 Cloudflare 域名")
        email_section.add_setting_item("temp_mail", "临时邮箱 (TEMP_MAIL)", "设置为 null 启用 IMAP 模式")
        self.sections["email"] = email_section
        current_row += 1

        # === IMAP 设置部分 ===
        imap_section = SettingsSection(self.scrollable_frame, "IMAP 设置")
        imap_section.grid(row=current_row, column=0, sticky="ew")
        imap_section.add_setting_item("imap_server", "IMAP 服务器", "例如：imap.gmail.com")
        imap_section.add_setting_item("imap_port", "IMAP 端口", "993")
        imap_section.add_setting_item("imap_user", "IMAP 用户", "邮箱地址")
        imap_section.add_setting_item("imap_pass", "IMAP 密码", "邮箱授权码", is_password=True)
        imap_section.add_option_item("imap_protocol", "IMAP 协议", ["IMAP", "POP3"])
        self.sections["imap"] = imap_section
        current_row += 1

        # === 浏览器设置部分 ===
        browser_section = SettingsSection(self.scrollable_frame, "浏览器设置")
        browser_section.grid(row=current_row, column=0, sticky="ew")
        browser_section.add_setting_item("user_agent", "User Agent", "浏览器 User Agent")
        browser_section.add_switch_item("headless", "无头模式", True)
        browser_section.add_browser_path_item(
            "browser_path",
            "浏览器路径",
            f"Chrome 浏览器路径，例如：{self.default_browser_paths.get(self.current_os, '')}",
            self.default_browser_paths.get(self.current_os, ''),
            self._select_browser_path
        )
        self.sections["browser"] = browser_section
        current_row += 1

        # === 代理设置部分 ===
        proxy_section = SettingsSection(self.scrollable_frame, "代理设置")
        proxy_section.grid(row=current_row, column=0, sticky="ew")
        proxy_section.add_setting_item("proxy", "代理服务器", "http://proxy:port")
        self.sections["proxy"] = proxy_section
        current_row += 1

        # === 自动化设置部分 ===
        automation_section = SettingsSection(self.scrollable_frame, "自动化设置")
        automation_section.grid(row=current_row, column=0, sticky="ew")
        automation_section.add_setting_item("retry", "重试次数", "3", width=100)
        self.sections["automation"] = automation_section
        current_row += 1

        # === 日志设置部分 ===
        log_section = SettingsSection(self.scrollable_frame, "日志设置")
        log_section.grid(row=current_row, column=0, sticky="ew")
        log_section.add_option_item("log_level", "日志级别", ["DEBUG", "INFO", "WARNING", "ERROR"])
        self.sections["log"] = log_section
        current_row += 1

        # === 主题设置部分 ===
        theme_section = SettingsSection(self.scrollable_frame, "主题设置")
        theme_section.grid(row=current_row, column=0, sticky="ew")
        theme_section.add_option_item("appearance_mode", "外观模式", ["Light", "Dark", "System"],
                                     command=self.change_appearance_mode)
        self.sections["theme"] = theme_section
        current_row += 1

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
            settings = {}
            # 从每个部分收集设置
            for section_name, section in self.sections.items():
                section_values = section.get_values()
                settings.update(section_values)

            # 特别处理一些设置值
            if "temp_mail" in settings and not settings["temp_mail"]:
                settings["temp_mail"] = "null"

            if "retry" in settings and settings["retry"]:
                try:
                    settings["retry_count"] = int(settings["retry"])
                except ValueError:
                    settings["retry_count"] = 3
                settings.pop("retry")

            # 浏览器设置转换
            if "user_agent" in settings:
                settings["browser_user_agent"] = settings.pop("user_agent")

            if "headless" in settings:
                settings["browser_headless"] = settings.pop("headless")

            # 记录日志
            logging.debug(f"获取的设置: {settings}")
            return settings

        except Exception as e:
            logging.error(f"获取设置时出错: {str(e)}")
            self.show_error_message(f"获取设置失败: {str(e)}\n请确保所有必填项都已填写。")
            return {}

    def save_settings(self):
        """保存设置到文件"""
        settings = self.get_settings()
        os.makedirs(self.config_dir, exist_ok=True)

        try:
            # 保存到 settings.json
            settings_file = os.path.join(self.config_dir, "settings.json")
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            # 生成 .env 文件内容
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

            env_content_str = "\n".join(env_content)

            # 保存到用户配置目录的 .env 文件
            env_file = os.path.join(self.config_dir, ".env")
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(env_content_str)

            # 同时保存到应用程序目录中的 .env 文件（如果是打包应用）
            try:
                if getattr(sys, "frozen", False):
                    app_env_file = os.path.join(os.path.dirname(sys.executable), ".env")
                    with open(app_env_file, "w", encoding="utf-8") as f:
                        f.write(env_content_str)
                    logging.info(f"配置也已保存到应用程序目录: {app_env_file}")
            except Exception as e:
                logging.warning(f"无法将配置保存到应用程序目录: {str(e)}")

            self.show_success_message()
            return True

        except Exception as e:
            error_msg = f"保存设置失败: {str(e)}"
            logging.error(error_msg)
            self.show_error_message(error_msg)
            return False

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
            settings_file = os.path.join(self.config_dir, "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                logging.info("从 settings.json 加载设置")

                # 转换设置键名为适合各部分的格式
                converted_settings = settings.copy()
                # 特殊处理浏览器设置
                if "browser_user_agent" in settings:
                    converted_settings["user_agent"] = settings["browser_user_agent"]
                if "browser_headless" in settings:
                    converted_settings["headless"] = settings["browser_headless"]
                if "retry_count" in settings:
                    converted_settings["retry"] = str(settings["retry_count"])

                # 更新每个部分的设置
                for section_name, section in self.sections.items():
                    section.set_values(converted_settings)

                # 设置外观模式
                if "appearance_mode" in settings:
                    appearance = settings["appearance_mode"]
                    if appearance in ["Light", "Dark", "System"]:
                        self.change_appearance_mode(appearance)

                # 设置日志级别
                if "log_level" in settings:
                    log_level = settings["log_level"]
                    if log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
                        logging.getLogger().setLevel(log_level)

                logging.info("设置加载完成")

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
                # 转换设置
                converted_settings = {}
                mapping = {
                    "domain": "domain",
                    "temp_mail": "temp_mail",
                    "imap_server": "imap_server",
                    "imap_port": "imap_port",
                    "imap_user": "imap_user",
                    "imap_pass": "imap_pass",
                    "imap_protocol": "imap_protocol",
                    "browser_user_agent": "user_agent",
                    "browser_headless": "headless",
                    "browser_path": "browser_path"
                }

                for env_key, section_key in mapping.items():
                    if env_key in settings:
                        converted_settings[section_key] = settings[env_key]

                # 更新每个部分的设置
                for section_name, section in self.sections.items():
                    section.set_values(converted_settings)
            else:
                logging.info("没有找到设置文件，使用默认设置")
                return

        except Exception as e:
            logging.error(f"加载设置失败: {str(e)}")
            logging.exception("详细错误信息:")
            # 不显示错误消息框，只记录日志
            # self.show_error_message(f"加载设置失败: {str(e)}")