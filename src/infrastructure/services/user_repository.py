import time

from src import UserData, UserRole
from src.core import UserSession, UserSessionTokens
from src.infrastructure.services import ApiRepository, RedisRepository

from src.infrastructure.utility import TokenParser, JwtToken


class UserRepository:
    def __init__(self, api_repository: ApiRepository, redis_repository: RedisRepository):
        self.api_repository = api_repository
        self.redis_repository = redis_repository

    def save_session(self, telegram_id, session: UserSession, nx=False):
        action_token: JwtToken = TokenParser.parse_jwt(session.tokens.action_token)
        refresh_token: JwtToken = TokenParser.parse_jwt(session.tokens.refresh_token)

        current_time = time.time()
        self.redis_repository.save_session(telegram_id, session, action_lifetime=int(action_token.exp - current_time),
                                           refresh_lifetime=int(refresh_token.exp - current_time), nx=nx)

    async def get_session_by_telegram_id_async(self, telegram_id):
        session: UserSession = self.redis_repository.get_session(telegram_id)
        needs_save = -1

        if not session:
            tokens: UserSessionTokens = await self.api_repository.signin_by_telegram_id_async(telegram_id)
            if not tokens.action_token:
                return None

            data: UserData = await self.api_repository.get_user_info_async(tokens.action_token)
            if not data:
                return None

            session = UserSession(user_id=data.id, tokens=tokens, data=data)
            self.save_session(telegram_id, session)
            return session

        if not session.tokens.action_token:
            token = await self.api_repository.refresh_action_by_refresh_token_async(session.tokens.refresh_token)
            if not token:
                return None

            session.tokens.action_token = token
            needs_save = True

        if not session.data:
            data: UserData = await self.api_repository.get_user_info_async(session.tokens.action_token)
            if not data:
                return None

            session.data = data
            needs_save = True

        if needs_save > 0:
            self.save_session(telegram_id, session, nx=True)

        return session

    async def signup_user_async(self, telegram_id, first_name, last_name):
        tokens: UserSessionTokens = await self.api_repository.signup_telegram_id_async(first_name, last_name, telegram_id)
        data: UserData = await self.api_repository.get_user_info_async(tokens.action_token)
        if not tokens or not data:
            return None

        session = UserSession(user_id=data.id, tokens=tokens, data=data)
        self.save_session(telegram_id, session)
        return session