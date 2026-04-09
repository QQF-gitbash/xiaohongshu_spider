from abc import ABC, abstractmethod
from typing import Any, Iterable


class BaseStore(ABC):
    @abstractmethod
    async def save(self, item: Any) -> None: ...

    async def save_many(self, items: Iterable[Any]) -> None:
        for it in items:
            await self.save(it)

    async def close(self) -> None:
        pass
