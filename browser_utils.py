from DrissionPage import ChromiumOptions, Chromium
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()


class BrowserManager:
    def __init__(self, browser_path=None, headless=True, user_agent=None, proxy=None):
        self.browser = None
        self.browser_path = browser_path
        self.headless = headless
        self.user_agent = user_agent
        self.proxy = proxy

    def init_browser(self):
        """初始化浏览器"""
        co = self._get_browser_options()
        self.browser = Chromium(co)
        return self.browser

    def _get_browser_options(self):
        """获取浏览器配置"""
        co = ChromiumOptions()
        try:
            extension_path = self._get_extension_path("turnstilePatch")
            co.add_extension(extension_path)
        except FileNotFoundError as e:
            logging.warning(f"警告: {e}")

        if self.browser_path:
            co.set_paths(browser_path=self.browser_path)

        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")

        if self.proxy:
            co.set_proxy(self.proxy)

        co.auto_port()
        if self.user_agent:
            co.set_user_agent(self.user_agent)

        co.headless(self.headless)  # 使用配置的无头模式设置

        # Mac 系统特殊处理
        if sys.platform == "darwin":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self,exname='turnstilePatch'):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, exname)

        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, exname)

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
