"""解析器父类"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    """统一原始数据 → 标准化 dict。"""

    @abstractmethod
    def parse(self, raw: Any) -> Dict[str, Any]: ...

    def parse_many(self, raws):
        return [self.parse(r) for r in raws]
