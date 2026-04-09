"""基于 httpx 的异步客户端"""
import httpx
from typing import Any
from core.base_client import BaseHttpClient
from utils.retry import async_retry
from config.settings import USER_AGENT, DEFAULT_TIMEOUT


class AsyncHttpClient(BaseHttpClient):
    DEFAULT_HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "origin": "https://www.xiaohongshu.com",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": '"Chromium";v="126", "Not-A.Brand";v="24", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": USER_AGENT,
    }

    def __init__(self, headers=None, cookies=None, timeout=DEFAULT_TIMEOUT):
        headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        super().__init__(headers, cookies, timeout)
        self._client = httpx.AsyncClient(
            headers=self.headers,
            cookies=self.cookies,
            timeout=timeout,
            follow_redirects=True,
        )

    def update_cookies(self, cookies):
        super().update_cookies(cookies)
        for k, v in cookies.items():
            self._client.cookies.set(k, v)

    @async_retry(times=3, delay=5.0)
    async def get(self, url: str, **kwargs) -> Any:
        kwargs = self._sign("GET", url, **kwargs)
        r = await self._client.get(url, **kwargs)
        r.raise_for_status()
        return r

    @async_retry(times=3, delay=5.0)
    async def post(self, url: str, **kwargs) -> Any:
        kwargs = self._sign("POST", url, **kwargs)
        r = await self._client.post(url, **kwargs)
        r.raise_for_status()
        return r

    async def close(self):
        await self._client.aclose()
