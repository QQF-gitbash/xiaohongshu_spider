"""AI Agent 父类"""
from abc import ABC, abstractmethod
from typing import Any
from openai import AsyncOpenAI
from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


class BaseAIAgent(ABC):
    def __init__(self, model: str = OPENAI_MODEL):
        self.model = model
        self.client = AsyncOpenAI(
            api_key = OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )

    @abstractmethod
    async def recognize(self, payload: Any) -> str: ...

    async def _chat(self, messages):
        resp = await self.client.chat.completions.create(
            model=self.model, messages=messages,
        )
        return resp.choices[0].message.content
