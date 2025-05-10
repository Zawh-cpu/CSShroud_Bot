import json

import redis
import datetime as dt

from src import UserData
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

    def save_session(self, telegram_id: int, essession: UserSession, action_lifetime: int =120, refresh_lifetime: int =600, cache_data_lifetime: int =120, nx=False):
        pipeline = self._connection.pipeline()

        pipeline.set(f"tg:{telegram_id}:user_id", essession.user_id, ex=refresh_lifetime, nx=nx)
        pipeline.set(f"tg:{telegram_id}:action_token", essession.tokens.action_token, ex=action_lifetime, nx=nx)
        pipeline.set(f"tg:{telegram_id}:refresh_token", essession.tokens.refresh_token, ex=refresh_lifetime, nx=nx)
        pipeline.set(f"tg:{telegram_id}:cache_data", essession.data.dump(), ex=cache_data_lifetime, nx=nx)

        pipeline.execute()

    def get_session(self, telegram_id: int) -> UserSession or None:
        values = [var.decode("utf-8") if var is not None else None for var in self._connection.mget([f"tg:{telegram_id}:user_id", f"tg:{telegram_id}:refresh_token", f"tg:{telegram_id}:action_token", f"tg:{telegram_id}:cache_data"])]
        if values[0] is None or values[1] is None:
            return None

        return UserSession(user_id=values[0], tokens=UserSessionTokens(refresh_token=values[1], action_token=values[2]), data=None if values[3] is None else UserData(json.loads(values[3])))

    def update_user_token(self, telegram_id: int, token, token_type="action", lifetime: int =60):
        self._connection.set(f"tg:{telegram_id}:{token_type}_token", token, ex=lifetime)

    def update_cache_profile(self, telegram_id: int, value : UserData, lifetime: int =120):
        self._connection.set(f"tg:{telegram_id}:cache_data", value.dump(), ex=lifetime)
