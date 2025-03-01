from dotenv import load_dotenv
import os
import sys
from logger import logging
import platform


class Config:
    def __init__(self, settings_dict=None):
        self.imap = False
        self.imap_protocol = 'POP3'  # 设置默认值

        # 设置默认值
        self.temp_mail = ""
        self.temp_mail_epin = ""
        self.temp_mail_ext = ""
        self.domain = ""

        if settings_dict:
            # 从设置字典加载配置
            self._load_from_settings(settings_dict)
        else:
            # 从 .env 文件加载配置
            try:
                self._load_from_env()
            except FileNotFoundError as e:
                logging.warning(f"{str(e)}，将使用默认配置")
                # 使用默认配置继续运行

        self.check_config()

    def _load_from_settings(self, settings):
        """从设置字典加载配置"""
        self.domain = settings.get('domain', '').strip()
        self.temp_mail = settings.get('temp_mail', '').strip()

        # 如果临时邮箱为 null，则加载 IMAP 设置
        if self.temp_mail == 'null':
            self.imap = True
            self.imap_server = settings.get('imap_server', '').strip()
            self.imap_port = settings.get('imap_port', '').strip()
            self.imap_user = settings.get('imap_user', '').strip()
            self.imap_pass = settings.get('imap_pass', '').strip()
            self.imap_dir = settings.get('imap_dir', 'inbox').strip()
            self.imap_protocol = settings.get('imap_protocol', 'POP3')
        else:
            self.temp_mail_epin = settings.get('temp_mail_epin', '').strip()
            self.temp_mail_ext = settings.get('temp_mail_ext', '').strip()

    def _load_from_env(self):
        """从 .env 文件加载配置"""
        # 首先尝试从用户配置目录加载
        try:
            # 获取用户配置目录
            if platform.system() == "Darwin":  # macOS
                app_data = os.path.expanduser("~/Library/Application Support/CursorPro")
            elif platform.system() == "Windows":  # Windows
                app_data = os.path.join(os.getenv("APPDATA"), "CursorPro")
            else:  # Linux
                app_data = os.path.expanduser("~/.config/cursorpro")

            config_dir = os.path.join(app_data, "config")
            dotenv_path = os.path.join(config_dir, ".env")

            if os.path.exists(dotenv_path):
                # 加载 .env 文件
                load_dotenv(dotenv_path)
                logging.info(f"从用户配置目录加载配置: {dotenv_path}")
            else:
                # 如果用户配置目录不存在.env，尝试从应用程序目录加载
                if getattr(sys, "frozen", False):
                    application_path = os.path.dirname(sys.executable)
                else:
                    application_path = os.path.dirname(os.path.abspath(__file__))

                # 指定 .env 文件的路径
                dotenv_path = os.path.join(application_path, ".env")

                if not os.path.exists(dotenv_path):
                    raise FileNotFoundError(f"文件 {dotenv_path} 不存在")

                # 加载 .env 文件
                load_dotenv(dotenv_path)
                logging.info(f"从应用程序目录加载配置: {dotenv_path}")
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            logging.error(f"加载配置文件时出错: {str(e)}")
            raise FileNotFoundError(f"加载配置文件失败: {str(e)}")

        # 从环境变量读取配置
        self.temp_mail = os.getenv("TEMP_MAIL", "").strip()
        if '@' in self.temp_mail:
            self.temp_mail = self.temp_mail.split("@")[0]
        self.temp_mail_epin = os.getenv("TEMP_MAIL_EPIN", "").strip()
        self.temp_mail_ext = os.getenv("TEMP_MAIL_EXT", "").strip()
        self.domain = os.getenv("DOMAIN", "").strip()

        # 如果临时邮箱为null则加载IMAP
        if self.temp_mail == "null":
            self.imap = True
            self.imap_server = os.getenv("IMAP_SERVER", "").strip()
            self.imap_port = os.getenv("IMAP_PORT", "").strip()
            self.imap_user = os.getenv("IMAP_USER", "").strip()
            self.imap_pass = os.getenv("IMAP_PASS", "").strip()
            self.imap_dir = os.getenv("IMAP_DIR", "inbox").strip()
            self.imap_protocol = os.getenv("IMAP_PROTOCOL", "POP3").strip()

    def get_temp_mail(self):

        return self.temp_mail

    def get_temp_mail_epin(self):

        return self.temp_mail_epin

    def get_temp_mail_ext(self):

        return self.temp_mail_ext

    def get_imap(self):
        if not self.imap:
            return False
        return {
            "imap_server": self.imap_server,
            "imap_port": self.imap_port,
            "imap_user": self.imap_user,
            "imap_pass": self.imap_pass,
            "imap_dir": self.imap_dir,
        }

    def get_domain(self):
        return self.domain

    def get_protocol(self):
        """获取邮件协议类型

        Returns:
            str: 'IMAP' 或 'POP3'
        """
        return self.imap_protocol

    def check_config(self):
        """检查配置项是否有效

        检查规则：
        1. 如果使用 tempmail.plus，需要配置 TEMP_MAIL 和 DOMAIN
        2. 如果使用 IMAP，需要配置 IMAP_SERVER、IMAP_PORT、IMAP_USER、IMAP_PASS
        3. IMAP_DIR 是可选的
        """
        # 基础配置检查
        required_configs = {
            "domain": "域名",
        }

        # 检查基础配置 - 改为警告而非抛出异常
        for key, name in required_configs.items():
            if not self.check_is_valid(getattr(self, key)):
                logging.warning(f"{name}未配置，使用默认值")
                # 设置一个默认域名
                if key == "domain" and not getattr(self, key):
                    setattr(self, key, "example.com tempmail.org snapmail.cc")

        # 检查邮箱配置
        if self.temp_mail != "null":
            # tempmail.plus 模式
            if not self.check_is_valid(self.temp_mail):
                logging.warning("临时邮箱未配置，使用默认值")
                self.temp_mail = "cursor"  # 设置默认值
        else:
            # IMAP 模式
            imap_configs = {
                "imap_server": "IMAP服务器",
                "imap_port": "IMAP端口",
                "imap_user": "IMAP用户名",
                "imap_pass": "IMAP密码",
            }

            has_invalid_config = False
            for key, name in imap_configs.items():
                value = getattr(self, key, "")
                if value == "null" or not self.check_is_valid(value):
                    logging.warning(f"{name}未配置，IMAP模式将不可用")
                    has_invalid_config = True

            if has_invalid_config:
                # 如果IMAP配置不完整，切换到默认邮箱模式
                self.imap = False
                self.temp_mail = "cursor"
                logging.warning("由于IMAP配置不完整，已切换到默认邮箱模式")

            # IMAP_DIR 是可选的，如果设置了就检查其有效性
            elif hasattr(self, "imap_dir") and self.imap_dir != "null" and not self.check_is_valid(self.imap_dir):
                logging.warning("IMAP收件箱目录配置无效，使用默认值inbox")
                self.imap_dir = "inbox"

    def check_is_valid(self, value):
        """检查配置项是否有效

        Args:
            value: 配置项的值

        Returns:
            bool: 配置项是否有效
        """
        return isinstance(value, str) and len(str(value).strip()) > 0

    def print_config(self):
        if self.imap:
            logging.info(f"\033[32mIMAP服务器: {self.imap_server}\033[0m")
            logging.info(f"\033[32mIMAP端口: {self.imap_port}\033[0m")
            logging.info(f"\033[32mIMAP用户名: {self.imap_user}\033[0m")
            logging.info(f"\033[32mIMAP密码: {'*' * len(self.imap_pass)}\033[0m")
            logging.info(f"\033[32mIMAP收件箱目录: {self.imap_dir}\033[0m")
        if self.temp_mail != "null":
            logging.info(
                f"\033[32m临时邮箱: {self.temp_mail}{self.temp_mail_ext}\033[0m"
            )
        logging.info(f"\033[32m域名: {self.domain}\033[0m")


# 使用示例
if __name__ == "__main__":
    try:
        config = Config()
        print("环境变量加载成功！")
        config.print_config()
    except ValueError as e:
        print(f"错误: {e}")
