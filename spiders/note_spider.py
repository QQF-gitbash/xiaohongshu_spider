"""笔记详情爬虫"""
from core.base_spider import BaseSpider
from config.settings import XHS_BASE


class NoteSpider(BaseSpider):
    """task = {'note_id': str, 'xsec_token': str}  或  str(note_id)（仅用于浏览器降级）"""

    async def fetch(self, task):
        if isinstance(task, dict):
            note_id = task["note_id"]
            xsec_token = task.get("xsec_token", "")
            xsec_source = task.get("xsec_source", "pc_feed")
        else:
            note_id, xsec_token, xsec_source = task, "", "pc_feed"

        if xsec_token:
            url = (f"{XHS_BASE}/explore/{note_id}"
                   f"?xsec_token={xsec_token}&xsec_source={xsec_source}")
        else:
            url = f"{XHS_BASE}/explore/{note_id}"
            self.log.warning("缺少 xsec_token，httpx 大概率拿不到数据，将直接降级浏览器")

        # 没 token 直接走浏览器；有 token 优先 httpx，失败再降级
        if not xsec_token:
            return self.browser.fetch_html(url, wait_ele="css:#noteContainer", timeout=20)
        try:
            r = await self.http.get(url)
            html = r.text
            if "__INITIAL_STATE__" not in html or '"note":{}' in html:
                raise RuntimeError("HTML 未水合，降级浏览器")
            return html
        except Exception as e:
            self.log.warning(f"httpx 取页失败/未水合，降级浏览器: {e}")
            return self.browser.fetch_html(url, wait_ele="css:#noteContainer", timeout=20)

    def parse(self, raw):
        item = self.parser.parse(raw)
        return [item] if item else []
