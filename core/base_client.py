"""HTTP 客户端父类"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseHttpClient(ABC):
    """所有 HTTP 客户端的抽象父类。

    职责：统一 get/post 接口、cookie 注入、请求签名钩子。
    """

    def __init__(self, headers: Optional[Dict[str, str]] = None,
                 cookies: Optional[Dict[str, str]] = None,
                 timeout: int = 15):
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.timeout = timeout

    def update_cookies(self, cookies: Dict[str, str]) -> None:
        self.cookies.update(cookies)

    def _sign(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """签名钩子，子类按需实现 x-s / x-t 等头注入。"""
        return kwargs

    @abstractmethod
    async def get(self, url: str, **kwargs) -> Any: ...

    @abstractmethod
    async def post(self, url: str, **kwargs) -> Any: ...

    @abstractmethod
    async def close(self) -> None: ...
