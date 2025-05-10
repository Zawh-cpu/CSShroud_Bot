import aiohttp

from src.infrastructure.services import UserData, ApiRepository, RedisRepository
from src.core import UserSessionTokens, Rate
from src.infrastructure.config import Config

class ServerService:
    _instance = None
    _api_repository = None
    _redis_repository = None

    def __new__(cls, api_repository: ApiRepository, redis_repository: RedisRepository):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api_repository = api_repository
            cls._instance.redis_repository = redis_repository
        return cls._instance

    async def get_rates(self):
        return [Rate(**data) for data in await self._api_repository.get_rates()]