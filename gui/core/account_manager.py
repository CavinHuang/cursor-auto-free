import json
import os
import logging
import platform
from datetime import datetime, timedelta

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

class AccountManager:
    def __init__(self):
        self.config_dir = get_app_config_dir()
        self.accounts_file = os.path.join(self.config_dir, "accounts.json")
        self._ensure_config_dir()
        self.current_account = self.load_current_account()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.accounts_file):
            self._save_accounts({"accounts": [], "current_account": None})

    def _save_accounts(self, data):
        """保存账号数据到文件"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存账号数据失败: {str(e)}")

    def _load_accounts(self):
        """从文件加载账号数据"""
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"accounts": [], "current_account": None}
        except Exception as e:
            logging.error(f"加载账号数据失败: {str(e)}")
            return {"accounts": [], "current_account": None}

    def save_account(self, email: str, password: str):
        """保存新账号"""
        data = self._load_accounts()

        # 创建新账号记录
        account = {
            "email": email,
            "password": password,
            "created_at": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat()
        }

        # 更新账号列表
        data["accounts"].append(account)
        data["current_account"] = account

        self._save_accounts(data)
        self.current_account = account
        logging.info(f"已保存新账号: {email}")

    def load_current_account(self):
        """加载当前账号信息"""
        data = self._load_accounts()
        return data.get("current_account")

    def get_account_info(self):
        """获取当前账号信息"""
        if not self.current_account:
            return {
                "email": "未登录",
                "created_at": "",
                "valid_until": "",
                "remaining_days": 0
            }

        try:
            valid_until = datetime.fromisoformat(self.current_account["valid_until"])
            remaining = valid_until - datetime.now()
            remaining_days = max(0, remaining.days)

            return {
                "email": self.current_account["email"],
                "created_at": datetime.fromisoformat(self.current_account["created_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                "valid_until": valid_until.strftime("%Y-%m-%d %H:%M:%S"),
                "remaining_days": remaining_days
            }
        except Exception as e:
            logging.error(f"获取账号信息失败: {str(e)}")
            return {
                "email": "错误",
                "created_at": "",
                "valid_until": "",
                "remaining_days": 0
            }

    def is_account_valid(self):
        """检查当前账号是否有效"""
        if not self.current_account:
            return False

        try:
            valid_until = datetime.fromisoformat(self.current_account["valid_until"])
            return datetime.now() < valid_until
        except Exception as e:
            logging.error(f"检查账号有效性失败: {str(e)}")
            return False