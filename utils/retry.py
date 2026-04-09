import asyncio, functools
from .logger import get_logger

log = get_logger("retry")

def async_retry(times: int = 3, delay: float = 1.0, exceptions=(Exception,)):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            last = None
            for i in range(times):
                try:
                    return await fn(*args, **kwargs)
                except exceptions as e:
                    last = e
                    log.warning(f"{fn.__name__} 第{i+1}次失败: {e}")
                    await asyncio.sleep(delay * (i + 1))
            raise last
        return wrapper
    return deco
