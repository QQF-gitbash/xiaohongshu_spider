import json, aiofiles
from pathlib import Path
from .base_store import BaseStore


class JsonStore(BaseStore):
    def __init__(self, file_path: str):
        self.path = Path(file_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def save(self, item) -> None:
        async with aiofiles.open(self.path, "a", encoding="utf-8") as f:
            await f.write(json.dumps(item, ensure_ascii=False) + "\n")
