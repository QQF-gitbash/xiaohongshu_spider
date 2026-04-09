"""评论爬取：完全复刻 FeedHarvester 的"导航 + 监听"套路
让浏览器自己打开笔记详情页，小红书 JS 会自动调 comment API 并带上
新鲜的 x-s / x-s-common / x-t，我们在 page.listen 旁边抓响应即可。
"""
import time
import json as _json
from utils.logger import get_logger

log = get_logger("CommentSpider")

TARGET_API = "/api/sns/web/v2/comment/page"
XHS_BASE = "https://www.xiaohongshu.com"


class CommentSpider:
    def __init__(self, dp_manager):
        self.dp = dp_manager
        self.page = dp_manager.page
        log.info("CommentSpider 初始化（导航+监听模式，签名由浏览器实时生成）")

    def fetch_one(self, note_id: str, xsec_token: str,
                  xsec_source: str = "pc_feed", timeout: int = 8) -> dict:
        """打开笔记详情页，等小红书 JS 自己调评论接口，截获响应返回。"""
        url = (f"{XHS_BASE}/explore/{note_id}"
               f"?xsec_token={xsec_token}&xsec_source={xsec_source}")

        # 先挂监听，再导航
        self.page.listen.start(TARGET_API)
        try:
            self.page.get(url)
            # 等浏览器内 JS 发请求并回包
            packet = self.page.listen.wait(count=1, timeout=timeout, fit_count=False)
            if not packet:
                log.warning(f"{note_id} 未捕获评论响应（可能无评论区或加载超时）")
                return {"error": "no packet captured"}
            if isinstance(packet, list):
                packet = packet[0]
            body = packet.response.body
            if isinstance(body, (bytes, str)):
                try:
                    body = _json.loads(body)
                except Exception:
                    return {"raw": body if isinstance(body, str) else body.decode("utf-8", "ignore")}
            return body if isinstance(body, dict) else {"raw": str(body)}
        finally:
            self.page.listen.stop()

    def close(self):
        pass
