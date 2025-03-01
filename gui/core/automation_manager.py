import threading
import logging
from typing import Optional, Callable
import time
import json
import random
import os
from enum import Enum
from datetime import datetime
from fake_useragent import UserAgent
import platform

from cursor_auth_manager import CursorAuthManager
from browser_utils import BrowserManager
from get_email_code import EmailVerificationHandler
from reset_machine import MachineIDResetter
from exit_cursor import ExitCursor
import patch_cursor_get_machine_id
import go_cursor_help
from config import Config
from .account_manager import AccountManager

# 定义 EMOJI 字典
EMOJI = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}

class VerificationStatus(Enum):
    """验证状态枚举"""
    PASSWORD_PAGE = "@name=password"
    CAPTCHA_PAGE = "@data-index=0"
    ACCOUNT_SETTINGS = "Account Settings"

class TurnstileError(Exception):
    """Turnstile 验证相关异常"""
    pass

class EmailGenerator:
    def __init__(
        self,
        password="".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
                k=12,
            )
        ),
    ):
        configInstance = Config()
        configInstance.print_config()
        # 获取域名列表并去除空行
        self.domains = [domain.strip() for domain in configInstance.get_domain().split('\n') if domain.strip()]
        self.names = self.load_names()
        self.default_password = password
        self.default_first_name = self.generate_random_name()
        self.default_last_name = self.generate_random_name()
        # 随机选择一个域名
        self.selected_domain = random.choice(self.domains)
        logging.info(f"已选择域名: {self.selected_domain}")

    def load_names(self):
        with open('names-dataset.txt', 'r') as file:
            return file.read().split()

    def generate_random_name(self):
        """生成随机用户名"""
        return random.choice(self.names)

    def generate_email(self, length=4):
        """生成随机邮箱地址"""
        timestamp = str(int(time.time()))[-length:]  # 使用时间戳后n位
        return f"{self.default_first_name}{timestamp}@{self.selected_domain}"

    def get_account_info(self):
        """获取完整的账号信息"""
        return {
            "email": self.generate_email(),
            "password": self.default_password,
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        }

class AutomationManager:
    def __init__(self, on_status_change: Optional[Callable[[str], None]] = None,
                 on_progress: Optional[Callable[[str], None]] = None):
        self.on_status_change = on_status_change or (lambda x: None)
        self.on_progress = on_progress or (lambda x: None)
        self.is_running = False
        self.browser_manager = None
        self.current_task = None
        self.account_manager = AccountManager()
        # 初始化时获取并显示Cursor版本
        self.cursor_version = self.get_cursor_version()
        self.update_status(f"当前 Cursor 版本: {self.cursor_version}")

    def update_status(self, status: str):
        """更新状态"""
        logging.info(status)
        if self.on_status_change:
            self.on_status_change(status)

    def update_progress(self, message: str):
        """更新进度"""
        logging.info(message)
        if self.on_progress:
            self.on_progress(message)

    def save_screenshot(self, tab, stage: str, timestamp: bool = True) -> None:
        """保存页面截图"""
        try:
            screenshot_dir = "screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)

            if timestamp:
                filename = f"turnstile_{stage}_{int(time.time())}.png"
            else:
                filename = f"turnstile_{stage}.png"

            filepath = os.path.join(screenshot_dir, filename)
            tab.get_screenshot(filepath)
            logging.debug(f"截图已保存: {filepath}")
        except Exception as e:
            logging.warning(f"截图保存失败: {str(e)}")

    def check_verification_success(self, tab) -> Optional[VerificationStatus]:
        """检查验证是否成功"""
        for status in VerificationStatus:
            if tab.ele(status.value):
                logging.info(f"验证成功 - 已到达{status.name}页面")
                return status
        return None

    def handle_turnstile(self, tab, max_retries: int = 2, retry_interval: tuple = (1, 2)) -> bool:
        """处理 Turnstile 验证"""
        logging.info("正在检测 Turnstile 验证...")
        self.save_screenshot(tab, "start")

        retry_count = 0

        try:
            while retry_count < max_retries:
                retry_count += 1
                logging.debug(f"第 {retry_count} 次尝试验证")

                try:
                    challenge_check = (
                        tab.ele("@id=cf-turnstile", timeout=2)
                        .child()
                        .shadow_root.ele("tag:iframe")
                        .ele("tag:body")
                        .sr("tag:input")
                    )

                    if challenge_check:
                        logging.info("检测到 Turnstile 验证框，开始处理...")
                        time.sleep(random.uniform(1, 3))
                        challenge_check.click()
                        time.sleep(2)

                        self.save_screenshot(tab, "clicked")

                        if self.check_verification_success(tab):
                            logging.info("Turnstile 验证通过")
                            self.save_screenshot(tab, "success")
                            return True

                except Exception as e:
                    logging.debug(f"当前尝试未成功: {str(e)}")

                if self.check_verification_success(tab):
                    return True

                time.sleep(random.uniform(*retry_interval))

            logging.error(f"验证失败 - 已达到最大重试次数 {max_retries}")
            self.save_screenshot(tab, "failed")
            return False

        except Exception as e:
            error_msg = f"Turnstile 验证过程发生异常: {str(e)}"
            logging.error(error_msg)
            self.save_screenshot(tab, "error")
            raise TurnstileError(error_msg)

    def get_cursor_session_token(self, tab, max_attempts=3, retry_interval=2):
        """获取Cursor会话token"""
        logging.info("开始获取cookie")
        attempts = 0

        while attempts < max_attempts:
            try:
                cookies = tab.cookies()
                for cookie in cookies:
                    if cookie.get("name") == "WorkosCursorSessionToken":
                        return cookie["value"].split("%3A%3A")[1]

                attempts += 1
                if attempts < max_attempts:
                    logging.warning(f"第 {attempts} 次尝试未获取到CursorSessionToken，{retry_interval}秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logging.error(f"已达到最大尝试次数({max_attempts})，获取CursorSessionToken失败")

            except Exception as e:
                logging.error(f"获取cookie失败: {str(e)}")
                attempts += 1
                if attempts < max_attempts:
                    logging.info(f"将在 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)

        return None

    def update_cursor_auth(self, email=None, access_token=None, refresh_token=None):
        """更新Cursor的认证信息"""
        auth_manager = CursorAuthManager()
        return auth_manager.update_auth(email, access_token, refresh_token)

    def get_user_agent(self):
        """获取随机user_agent"""
        try:
            # 首先尝试使用fake-useragent生成随机UA
            ua = UserAgent()
            # 获取最新的Chrome浏览器UA
            user_agent = ua.chrome
            logging.info(f"成功生成随机user-agent: {user_agent}")
            return user_agent
        except Exception as e:
            logging.error(f"生成随机user agent失败: {str(e)}")
            try:
                # 如果随机生成失败，尝试获取真实浏览器的UA
                browser_manager = BrowserManager()
                browser = browser_manager.init_browser()
                user_agent = browser.latest_tab.run_js("return navigator.userAgent")
                browser_manager.quit()
                return user_agent
            except Exception as e:
                logging.error(f"获取真实浏览器user agent也失败: {str(e)}")
                # 使用默认UA
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def get_cursor_version(self) -> str:
        """获取Cursor版本"""
        try:
            # 获取系统类型
            system = platform.system()
            logging.info(f"当前操作系统: {system}")

            # 获取路径
            paths = patch_cursor_get_machine_id.get_cursor_paths()
            logging.info(f"获取到的路径: {paths}")

            # 确保我们使用正确的路径 - paths[0]是package.json的路径
            pkg_path = paths[0]
            logging.info(f"package.json路径: {pkg_path}")

            if not os.path.exists(pkg_path):
                raise FileNotFoundError(f"找不到文件: {pkg_path}")

            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                version = data.get("version")
                if not version:
                    raise ValueError("package.json中未找到version字段")

                # 获取安装路径 - 需要往上两级目录才是Cursor的安装根目录
                cursor_path = os.path.dirname(os.path.dirname(pkg_path))
                return f"{version} (安装路径: {cursor_path})"
        except FileNotFoundError as e:
            logging.error(f"文件不存在: {str(e)}")
            return "未知版本 (找不到Cursor安装目录)"
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析错误: {str(e)}")
            return "未知版本 (package.json格式错误)"
        except Exception as e:
            logging.error(f"获取Cursor版本失败: {str(e)}")
            return "未知版本"

    def check_cursor_version(self):
        """检查 Cursor 版本"""
        try:
            package_path, main_path = patch_cursor_get_machine_id.get_cursor_paths()
            # 确保我们使用正确的路径
            with open(package_path, "r", encoding="utf-8") as f:
                version = json.load(f)["version"]
            return patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")
        except Exception as e:
            logging.error(f"检查Cursor版本失败: {str(e)}")
            return False

    def reset_machine_id(self):
        """重置机器码"""
        try:
            self.update_status("正在检查 Cursor 版本...")
            greater_than_0_45 = self.check_cursor_version()

            self.update_status("正在关闭 Cursor...")
            ExitCursor()

            self.update_status("正在重置机器码...")
            if greater_than_0_45:
                try:
                    go_cursor_help.go_cursor_help()
                except Exception as e:
                    logging.error(f"使用go_cursor_help重置失败: {str(e)}")
                    # 如果go_cursor_help失败，尝试使用备选方案
                    MachineIDResetter().reset_machine_ids()
            else:
                MachineIDResetter().reset_machine_ids()

            self.update_status("机器码重置完成")

            # 重启 Cursor
            self.update_status("正在重启 Cursor...")
            try:
                if platform.system() == "Darwin":  # macOS
                    os.system("open -a Cursor")
                elif platform.system() == "Windows":  # Windows
                    cursor_path = os.path.join(os.getenv("LOCALAPPDATA", ""), "Programs", "Cursor", "Cursor.exe")
                    if os.path.exists(cursor_path):
                        os.system(f'start "" "{cursor_path}"')
                    else:
                        logging.warning("找不到Cursor可执行文件，请手动启动")
                elif platform.system() == "Linux":  # Linux
                    os.system("cursor")
                else:
                    logging.warning("不支持的操作系统，请手动启动Cursor")

                self.update_status("Cursor 已重启")
            except Exception as e:
                logging.error(f"重启Cursor失败: {str(e)}")
                self.update_status("请手动重启Cursor")

            return True
        except Exception as e:
            error_msg = f"重置机器码失败: {str(e)}"
            logging.error(error_msg)
            self.update_status(error_msg)
            return False

    def sign_up_account(self, browser, tab, account_info):
        """注册账号流程"""
        logging.info("=== 开始注册账号流程 ===")
        sign_up_url = "https://authenticator.cursor.sh/sign-up"
        logging.info(f"正在访问注册页面: {sign_up_url}")
        tab.get(sign_up_url)

        try:
            if tab.ele("@name=first_name"):
                logging.info("正在填写个人信息...")
                tab.actions.click("@name=first_name").input(account_info["first_name"])
                logging.info(f"已输入名字: {account_info['first_name']}")
                time.sleep(random.uniform(1, 3))

                tab.actions.click("@name=last_name").input(account_info["last_name"])
                logging.info(f"已输入姓氏: {account_info['last_name']}")
                time.sleep(random.uniform(1, 3))

                tab.actions.click("@name=email").input(account_info["email"])
                logging.info(f"已输入邮箱: {account_info['email']}")
                time.sleep(random.uniform(1, 3))

                logging.info("提交个人信息...")
                tab.actions.click("@type=submit")

        except Exception as e:
            logging.error(f"注册页面访问失败: {str(e)}")
            return False

        self.handle_turnstile(tab)

        try:
            if tab.ele("@name=password"):
                logging.info("正在设置密码...")
                tab.ele("@name=password").input(account_info["password"])
                time.sleep(random.uniform(1, 3))

                logging.info("提交密码...")
                tab.ele("@type=submit").click()
                logging.info("密码设置完成，等待系统响应...")

        except Exception as e:
            logging.error(f"密码设置失败: {str(e)}")
            return False

        if tab.ele("This email is not available."):
            logging.error("注册失败：邮箱已被使用")
            return False

        self.handle_turnstile(tab)

        while True:
            try:
                if tab.ele("Account Settings"):
                    logging.info("注册成功 - 已进入账户设置页面")
                    break
                if tab.ele("@data-index=0"):
                    logging.info("正在获取邮箱验证码...")
                    email_handler = EmailVerificationHandler(account_info["email"])
                    code = email_handler.get_verification_code()
                    if not code:
                        logging.error("获取验证码失败")
                        return False

                    logging.info(f"成功获取验证码: {code}")
                    logging.info("正在输入验证码...")
                    i = 0
                    for digit in code:
                        tab.ele(f"@data-index={i}").input(digit)
                        time.sleep(random.uniform(0.1, 0.3))
                        i += 1
                    logging.info("验证码输入完成")
                    break
            except Exception as e:
                logging.error(f"验证码处理过程出错: {str(e)}")

        self.handle_turnstile(tab)
        wait_time = random.randint(3, 6)
        for i in range(wait_time):
            logging.info(f"等待系统处理中... 剩余 {wait_time-i} 秒")
            time.sleep(1)

        logging.info("正在获取账户信息...")
        settings_url = "https://www.cursor.com/settings"
        tab.get(settings_url)
        try:
            usage_selector = (
                "css:div.col-span-2 > div > div > div > div > "
                "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
                "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
            )
            usage_ele = tab.ele(usage_selector)
            if usage_ele:
                usage_info = usage_ele.text
                total_usage = usage_info.split("/")[-1].strip()
                logging.info(f"账户可用额度上限: {total_usage}")

                # 保存账号信息
                self.account_manager.save_account(account_info["email"], account_info["password"])
                # 更新GUI显示
                if hasattr(self, 'parent_app'):
                    self.parent_app.update_account_display()
        except Exception as e:
            logging.error(f"获取账户额度信息失败: {str(e)}")

        logging.info("\n=== 注册完成 ===")
        account_info_str = f"Cursor 账号信息:\n邮箱: {account_info['email']}\n密码: {account_info['password']}"
        logging.info(account_info_str)
        time.sleep(5)
        return True

    def start_automation(self, config: dict):
        """启动自动化任务"""
        if self.is_running:
            return

        self.is_running = True
        self.current_task = threading.Thread(target=self._run_automation, args=(config,))
        self.current_task.start()

    def stop_automation(self):
        """停止自动化任务"""
        self.is_running = False
        if self.browser_manager:
            self.browser_manager.quit()

    def _run_automation(self, config: dict):
        """运行自动化任务"""
        try:
            self.update_status(f"正在初始化... (Cursor版本: {self.cursor_version})")

            # 获取user-agent
            self.update_progress("正在获取user-agent...")
            user_agent = self.get_user_agent()
            if not user_agent:
                self.update_progress("获取user agent失败，使用默认值")
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

            # 剔除user_agent中的"HeadlessChrome"
            user_agent = user_agent.replace("HeadlessChrome", "Chrome")

            # 初始化浏览器
            self.update_progress("正在启动浏览器...")
            self.browser_manager = BrowserManager(
                browser_path=config.get('browser_path'),
                headless=config.get('browser_headless', False),
                user_agent=user_agent,
                proxy=config.get('proxy')
            )
            browser = self.browser_manager.init_browser()
            tab = browser.latest_tab

            # 配置信息
            login_url = "https://authenticator.cursor.sh"
            sign_up_url = "https://authenticator.cursor.sh/sign-up"
            settings_url = "https://www.cursor.com/settings"

            # 生成账号信息
            self.update_progress("正在生成账号信息...")
            config_instance = Config(settings_dict=config)
            email_generator = EmailGenerator()
            account_info = email_generator.get_account_info()

            # 初始化邮箱验证
            self.update_progress("正在初始化邮箱验证...")
            email_handler = EmailVerificationHandler(account_info["email"])

            # 重置turnstile
            tab.run_js("try { turnstile.reset() } catch(e) { }")

            # 开始注册流程
            self.update_status("开始注册流程...")
            tab.get(login_url)

            # 使用注册逻辑
            if self.sign_up_account(browser, tab, account_info):
                self.update_progress("正在获取会话令牌...")
                token = self.get_cursor_session_token(tab)
                if token:
                    self.update_progress("更新认证信息...")
                    self.update_cursor_auth(
                        email=account_info["email"],
                        access_token=token,
                        refresh_token=token
                    )

                    self.update_progress("重置机器码...")
                    self.reset_machine_id()

                    self.update_status("自动化任务完成")
                else:
                    self.update_status("获取会话令牌失败")

        except Exception as e:
            error_msg = f"自动化任务失败: {str(e)}"
            logging.error(error_msg)
            self.update_status(error_msg)
        finally:
            self.is_running = False
            if self.browser_manager:
                self.browser_manager.quit()