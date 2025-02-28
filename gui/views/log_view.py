import customtkinter as ctk
import logging
from datetime import datetime
import os

class LogView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 标题
        self.title_label = ctk.CTkLabel(self, text="日志查看器",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 日志显示区域
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(self.log_frame, width=600, height=400)
        self.log_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 控制按钮区域
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.clear_button = ctk.CTkButton(self.control_frame, text="清除日志",
                                         command=self.clear_logs)
        self.clear_button.grid(row=0, column=0, padx=10, pady=10)

        self.export_button = ctk.CTkButton(self.control_frame, text="导出日志",
                                          command=self.export_logs)
        self.export_button.grid(row=0, column=1, padx=10, pady=10)

        # 设置日志处理器
        self.setup_logger()

    def setup_logger(self):
        """设置日志处理器"""
        class TextboxHandler(logging.Handler):
            def __init__(self, textbox):
                super().__init__()
                self.textbox = textbox

            def emit(self, record):
                msg = self.format(record)
                self.textbox.insert("end", f"{msg}\n")
                self.textbox.see("end")  # 自动滚动到最新日志

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 创建处理器并设置格式化器
        handler = TextboxHandler(self.log_text)
        handler.setFormatter(formatter)

        # 获取根日志记录器并添加处理器
        logger = logging.getLogger()
        logger.addHandler(handler)

    def clear_logs(self):
        """清除日志内容"""
        self.log_text.delete("1.0", "end")

    def export_logs(self):
        """导出日志到文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/cursor_pro_{timestamp}.log"
            os.makedirs("logs", exist_ok=True)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", "end"))

            logging.info(f"日志已导出到: {filename}")
        except Exception as e:
            logging.error(f"导出日志失败: {str(e)}")

    def add_log(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }

        level = level.upper()
        if level in log_levels:
            logging.log(log_levels[level], message)