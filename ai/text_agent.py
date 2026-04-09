"""乱序/混淆文本还原"""
from .base_agent import BaseAIAgent


class TextAgent(BaseAIAgent):
    async def recognize(self, scrambled: str) -> str:
        messages = [
            {"role": "system", "content": "你是中文文本还原助手，将乱序/混淆文本还原为通顺原文，只输出结果。"},
            {"role": "user", "content": scrambled},
        ]
        return (await self._chat(messages)).strip()
