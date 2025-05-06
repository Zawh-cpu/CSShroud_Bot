import aiohttp
import json

from src.core import UserSessionTokens
from src.infrastructure.config import Config

class AiRepository:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.base_url = config.AI.BASE_URL
            cls._instance.headers = {"Authorization": f"Bearer {config.AI.TOKEN}"}
            cls._instance.base_model = config.AI.BASE_MODEL
            cls._instance.token_limit = config.AI.TOKEN_LIMIT
            cls._instance.max_retries = config.AI.MAX_RETRIES
            cls._instance.session = aiohttp.ClientSession(headers=cls._instance.headers)
        return cls._instance

    async def close(self):
        await self.session.close()

    async def parse_response(self, description: str) -> dict or None:
        tags = {
            "size": 'для размеров одежды (например, "M", "XL", "56"), обуви ("42", "45"), предметов с фиксированными размерами ("A4", "10x15cm").',
            "volume": 'для объёма в литрах, кубометрах (например, "1.5л", "0.3м³").',
            "capacity": 'для ёмкости электроники в мАч (например, "5000mAh").'
        }

        tag_text = ['- `"{0}"` — {1}'.format(x, tags[x]) for x in tags]
        prompt = r'Опиши "%s" и выбери теги [%s], если применимо. Определяй единицы измерения: %s.  Формат JSON: {"title": "<название товара>", "cost": "<int, цена в рублях или null, если не предоставлено>", "desc": "<среднее описание>", "tags": {"<тег>": "<значение>", ...} // Или {}}' % (description, ", ".join(tags.keys()), " ".join(tag_text))

        data = {
            "model": self.base_model,
            "messages": [{
                "role": "system",
                "content": prompt,
                "max_tokens": self.token_limit,
                "response_format": {"type": "json_object"}
            }]
        }

        for i in range(self.max_retries):
            try:
                async with self.session.post(f"{self.base_url}/openai/v1/chat/completions", json=data) as response:
                    if response.status != 200:
                        return None

                    answer = await response.json()
                    return json.loads(answer.get("choices")[0].get("message", dict()).get("content", dict()))
            except Exception as e:
                print("GENERATION FAILED. RETRYING...")
        return None
