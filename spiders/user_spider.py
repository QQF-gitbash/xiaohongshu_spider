"""用户主页爬虫"""
from core.base_spider import BaseSpider
from config.settings import XHS_BASE


class UserSpider(BaseSpider):
    """task = user_id"""

    async def fetch(self, task: str):
        url = f"{XHS_BASE}/user/profile/{task}"
        r = await self.http.get(url)
        return r.text

    def parse(self, raw):
        item = self.parser.parse(raw)
        return [item] if item else []
