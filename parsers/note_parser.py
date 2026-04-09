"""笔记解析器"""
import re
import json
from typing import Any, Dict
from core.base_parser import BaseParser
from utils.logger import get_logger

log = get_logger("NoteParser")


class NoteParser(BaseParser):
    # 抓到 = 后到 </script> 前的整段，再自己平衡括号
    INITIAL_STATE_RE = re.compile(
        r"window\.__INITIAL_STATE__\s*=\s*(\{.+?\})\s*</script>", re.S
    )

    def parse(self, raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict):
            return self._from_dict(raw)
        return self._from_html(raw or "")

    # ---------- HTML ----------
    def _from_html(self, html: str) -> Dict[str, Any]:
        json_str = self._extract_initial_state(html)
        if not json_str:
            log.warning("未匹配到 __INITIAL_STATE__，可能未登录或被风控")
            return {}
        # 小红书源码里有 undefined，需要替换
        json_str = re.sub(r"\bundefined\b", "null", json_str)
        try:
            data = json.loads(json_str)
        except Exception as e:
            log.warning(f"JSON 解析失败: {e}")
            return {}
        return self._from_dict(data)

    def _extract_initial_state(self, html: str) -> str:
        """用括号平衡法精确截取 JSON 串。"""
        key = "window.__INITIAL_STATE__"
        i = html.find(key)
        if i == -1:
            return ""
        i = html.find("{", i)
        if i == -1:
            return ""
        depth, in_str, esc = 0, False, False
        for j in range(i, len(html)):
            ch = html[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return html[i : j + 1]
        return ""

    # ---------- DICT ----------
    def _from_dict(self, data: Dict) -> Dict[str, Any]:
        note_map = (
            self._dig(data, "note", "noteDetailMap")
            or self._dig(data, "noteData", "noteDetailMap")
            or {}
        )
        if not note_map:
            log.warning(f"noteDetailMap 不存在，顶层 keys={list(data.keys())[:10]}")
            return {}

        first = next(iter(note_map.values()), {}) or {}
        note = first.get("note") or first
        # DEBUG：把实际结构 dump 一份方便定位字段路径
        try:
            from pathlib import Path
            Path("debug_note.json").write_text(
                json.dumps(first, ensure_ascii=False, indent=2)[:8000],
                encoding="utf-8",
            )
            log.info(f"first keys = {list(first.keys())}")
            log.info(f"note  keys = {list(note.keys()) if isinstance(note, dict) else type(note)}")
        except Exception as e:
            log.warning(f"dump 失败: {e}")
        user = note.get("user") or {}
        interact = note.get("interactInfo") or {}
        images = note.get("imageList") or []

        return {
            "note_id": note.get("noteId") or note.get("id"),
            "title": note.get("title"),
            "desc": note.get("desc"),
            "type": note.get("type"),
            "user_id": user.get("userId"),
            "user": user.get("nickname"),
            "likes": interact.get("likedCount"),
            "collected": interact.get("collectedCount"),
            "comments": interact.get("commentCount"),
            "shares": interact.get("shareCount"),
            "images": [
                img.get("urlDefault") or img.get("url") for img in images
            ],
            "tags": [t.get("name") for t in (note.get("tagList") or [])],
        }

    @staticmethod
    def _dig(d: Dict, *keys):
        cur = d
        for k in keys:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(k)
        return cur
