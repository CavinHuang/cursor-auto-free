import logging
import os
import platform
from datetime import datetime

def get_app_log_dir():
    """获取应用日志目录"""
    if platform.system() == "Darwin":  # macOS
        app_data = os.path.expanduser("~/Library/Application Support/CursorPro")
    elif platform.system() == "Windows":  # Windows
        app_data = os.path.join(os.getenv("APPDATA"), "CursorPro")
    else:  # Linux
        app_data = os.path.expanduser("~/.config/cursorpro")

    log_dir = os.path.join(app_data, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

# 配置日志
log_dir = get_app_log_dir()

class PrefixFormatter(logging.Formatter):
    """自定义格式化器，为 DEBUG 级别日志添加开源项目前缀"""
    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"[开源项目：https://github.com/chengazhen/cursor-auto-free] {record.msg}"
        return super().format(record)

# 配置日志处理器
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
            encoding="utf-8",
            mode="a"  # 追加模式
        ),
    ],
)

# 为文件处理器设置自定义格式化器
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setFormatter(PrefixFormatter("%(asctime)s - %(levelname)s - %(message)s"))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(PrefixFormatter("%(message)s"))

# 将控制台处理器添加到日志记录器
logging.getLogger().addHandler(console_handler)

# 打印日志目录所在路径
logging.info(f"Logger initialized, log directory: {os.path.abspath(log_dir)}")

def main_task():
    """
    Main task execution function. Simulates a workflow and handles errors.
    """
    try:
        logging.info("Starting the main task...")
        logging.info("Main task completed successfully.")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}", exc_info=True)
    finally:
        logging.info("Task execution finished.")

if __name__ == "__main__":
    logging.info("Application started.")
    main_task()
    logging.info("Application exited.")
