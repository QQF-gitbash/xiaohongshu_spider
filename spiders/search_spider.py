"""关键词搜索爬虫"""
from urllib.parse import quote
from core.base_spider import BaseSpider
from config.settings import XHS_BASE


class SearchSpider(BaseSpider):
    """task = {'keyword': str, 'page': int}"""

    async def fetch(self, task: dict):
        kw = quote(task["keyword"])
        url = f"{XHS_BASE}/search_result?keyword={kw}&page={task.get('page', 1)}"
        return self.browser.fetch_html(url, wait_ele="css:.note-item", timeout=20)

    def parse(self, raw):
        # 简化：交给 NoteParser 解析 __INITIAL_STATE__
        item = self.parser.parse(raw)
        return [item] if item else []
