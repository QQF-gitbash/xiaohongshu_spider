"""图片验证码识别"""
import base64
from .base_agent import BaseAIAgent


class CaptchaAgent(BaseAIAgent):
    async def recognize(self, image_bytes: bytes) -> str:
        b64 = base64.b64encode(image_bytes).decode()
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "请识别这张验证码图片中的字符，仅返回字符本身。"},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }]
        return (await self._chat(messages)).strip()
