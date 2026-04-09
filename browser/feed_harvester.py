"""利用 DrissionPage 监听小红书自己的接口，批量收割 (note_id, xsec_token)"""
import time
from typing import List, Dict, Set
from urllib.parse import quote
from utils.logger import get_logger

log = get_logger("FeedHarvester")

# 一刀宽匹配，把 sns/web/v1 下所有接口全收
TARGET_APIS = "sns/web/v1"


class FeedHarvester:
    """依赖一个已登录的 DPManager。"""

    def __init__(self, dp_manager):
        self.dp = dp_manager
        self.page = dp_manager.page

    # ---------- 公共入口 ----------
    def harvest_homefeed(self, max_notes: int = 30, scroll_times: int = 6) -> List[Dict]:
        url = "https://www.xiaohongshu.com/explore"
        return self._collect(url, max_notes, scroll_times)

    def harvest_search(self, keyword: str, max_notes: int = 30, scroll_times: int = 6) -> List[Dict]:
        url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&source=web_explore_feed"
        return self._collect(url, max_notes, scroll_times)

    def harvest_user(self, user_id: str, max_notes: int = 30, scroll_times: int = 6) -> List[Dict]:
        url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        return self._collect(url, max_notes, scroll_times)

    # ---------- 核心逻辑 ----------
    def _collect(self, url: str, max_notes: int, scroll_times: int) -> List[Dict]:
        max_notes = int(max_notes)
        scroll_times = int(scroll_times)
        results: List[Dict] = []
        seen: Set[str] = set()

        # 必须先 start 再 get
        self.page.listen.start(TARGET_APIS)
        log.info(f"打开 {url}（监听 {TARGET_APIS}）")
        self.page.get(url)
        time.sleep(2)  # 等首屏请求完成

        def drain():
            """非阻塞地把当前已捕获的包全部取出。"""
            n_before = len(results)
            for pkt in self.page.listen.steps(timeout=2):
                self._extract(pkt, results, seen)
                if len(results) >= max_notes:
                    break
            return len(results) - n_before

        try:
            got = drain()
            log.info(f"首屏抓到 {got} 条")

            for i in range(scroll_times):
                if len(results) >= max_notes:
                    break
                self.page.scroll.to_bottom()
                time.sleep(1.8)
                got = drain()
                log.info(f"滚动 {i + 1}/{scroll_times}，本轮+{got}，累计 {len(results)} 条")
        finally:
            self.page.listen.stop()

        log.info(f"收割完成，共 {len(results)} 条")
        return results[:max_notes]

    def _extract(self, packet, results: List[Dict], seen: Set[str]):
        """从接口响应里挖 note_id + xsec_token。"""
        try:
            body = packet.response.body
            url = packet.url
        except Exception as e:
            log.warning(f"读包失败: {e}")
            return
        if isinstance(body, (bytes, str)):
            import json as _json
            try:
                body = _json.loads(body)
            except Exception:
                log.warning(f"包非 JSON: {url}")
                return
        if not isinstance(body, dict):
            return
        log.info(f"命中接口 {url[:80]}")

        data = body.get("data") or {}
        # 几种常见结构都覆盖
        items = (
            data.get("items")
            or data.get("notes")
            or (data.get("note") and [data["note"]])
            or []
        )
        for it in items:
            if not isinstance(it, dict):
                continue
            note_card = it.get("note_card") or {}
            note_id = it.get("id") or it.get("note_id") or note_card.get("note_id")
            xsec = it.get("xsec_token") or note_card.get("xsec_token")
            user = note_card.get("user") or it.get("user") or {}
            user_id = user.get("user_id") or user.get("userId") or user.get("id")
            if not (note_id and xsec) or note_id in seen:
                continue
            seen.add(note_id)
            results.append({
                "note_id": note_id,
                "xsec_token": xsec,
                "user_id": user_id or "",
                "xsec_source": "pc_feed",
            })
