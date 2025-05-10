# src/container.py
from dependency_injector import containers, providers

from src.infrastructure.services import ApiRepository, RedisRepository, UserRepository, AiRepository
from src.infrastructure.services.server_service import ServerService
from src.infrastructure.services.translator import Translator
from src.infrastructure.config import Config


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    translator = providers.Singleton(Translator, config=config)

    api_repository = providers.Singleton(ApiRepository, config=config)
    redis_repository = providers.Factory(RedisRepository, config=config)
    ai_repository = providers.Factory(AiRepository, config=config)

    user_repository = providers.Factory(UserRepository, api_repository=api_repository, redis_repository=redis_repository)

    server_service = providers.Singleton(ServerService, api_repository=api_repository, redis_repository=redis_repository)
