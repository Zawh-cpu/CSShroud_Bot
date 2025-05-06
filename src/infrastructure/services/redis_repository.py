import json

import redis
import datetime as dt

from src.core import UserSession, UserSessionTokens


class RedisRepository:
    _instance = None
    _connection_pool = None

    def __new__(cls, config=None):
        if cls._instance is None:
            config.save_config()
            cls._connection_pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
            cls._instance = super().__new__(cls)
            cls._connection = redis.StrictRedis(connection_pool=cls._connection_pool)
        return cls._instance

    def get(self, key):
        return self._connection.get(key)

    def set(self, key, value):
        self._connection.set(key, value)

    def save_session(self, telegram_id: int, session: UserSession, action_lifetime: int =60, refresh_lifetime: int =600, cache_data_lifetime: int =60):
        pipeline = self._connection.pipeline()

        pipeline.set(f"tg:{telegram_id}:user_id", session.user_id, ex=refresh_lifetime)
        pipeline.set(f"tg:{telegram_id}:action_token", session.tokens.action_token, ex=action_lifetime)
        pipeline.set(f"tg:{telegram_id}:refresh_token", session.tokens.refresh_token, ex=refresh_lifetime)
        pipeline.set(f"tg:{telegram_id}:cache_data", "....", ex=cache_data_lifetime)

        pipeline.execute()

    def get_session(self, telegram_id: int) -> UserSession or None:
        values = [var.decode("utf-8") if var is not None else None for var in self._connection.mget([f"tg:{telegram_id}:user_id", f"tg:{telegram_id}:refresh_token", f"tg:{telegram_id}:action_token"])]
        if values[0] is None or values[1] is None:
            return None

        return UserSession(user_id=values[0], tokens=UserSessionTokens(refresh_token=values[1], action_token=values[2]))

    def update_user_token(self, telegram_id: int, token, token_type="action", lifetime: int =60):
        self._connection.set(f"tg:{telegram_id}:{token_type}_token", token, ex=lifetime)

    def update_cache_profile(self, telegram_id: int, value, lifetime: int =60):
        self._connection.set(f"tg:{telegram_id}:cache_data", value, ex=lifetime)
