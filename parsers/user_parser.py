from typing import Any, Dict
from core.base_parser import BaseParser


class UserParser(BaseParser):
    def parse(self, raw: Any) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {}
        info = raw.get("basicInfo", {})
        return {
            "user_id": raw.get("userId"),
            "nickname": info.get("nickname"),
            "desc": info.get("desc"),
            "fans": (raw.get("interactions") or [{}])[0].get("count"),
        }
