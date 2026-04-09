"""爬虫父类（编排者）"""
from abc import ABC, abstractmethod
from typing import Any
from utils.logger import get_logger


class BaseSpider(ABC):
    """模板方法模式：run = ensure_login → fetch → parse → save。"""

    def __init__(self, browser=None, http_client=None,
                 parser=None, store=None, ai_agent=None):
        self.browser = browser
        self.http = http_client
        self.parser = parser
        self.store = store
        self.ai = ai_agent
        self.log = get_logger(self.__class__.__name__)

    async def run(self, task: Any):
        await self.ensure_login()
        try:
            raw = await self.fetch(task)
            items = self.parse(raw)
            await self.save(items)
            return items
        except Exception as e:
            self.log.exception(f"任务失败: {e}")
            raise

    async def ensure_login(self):
        if not self.browser:
            return
        if not self.browser.is_logged_in():
            await self.browser.login()
        # 不论本来就登录还是刚登录，都把关键 cookie 同步给 httpx
        if self.http:
            self.http.update_cookies(self.browser.get_key_cookies())
            self.log.info(f"已注入 cookie: {list(self.browser.get_key_cookies().keys())}")

    async def handle_captcha(self, image_bytes: bytes) -> str:
        if not self.ai:
            raise RuntimeError("未配置 AI agent，无法识别验证码")
        return await self.ai.recognize(image_bytes)

    @abstractmethod
    async def fetch(self, task) -> Any: ...

    @abstractmethod
    def parse(self, raw) -> Any: ...

    async def save(self, items) -> None:
        if self.store and items:
            await self.store.save_many(items)
