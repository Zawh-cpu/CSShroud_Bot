import time

from src.core import UserSession, UserSessionTokens
from src.infrastructure.services import ApiRepository, RedisRepository

from src.infrastructure.utility import TokenParser, JwtToken


class UserRepository:
    def __init__(self, api_repository: ApiRepository, redis_repository: RedisRepository):
        self.api_repository = api_repository
        self.redis_repository = redis_repository

    def parse_and_save_session(self, telegram_id, tokens: UserSessionTokens):
        action_token: JwtToken = TokenParser.parse_jwt(tokens.action_token)
        refresh_token: JwtToken = TokenParser.parse_jwt(tokens.refresh_token)

        session = UserSession(user_id=refresh_token.sub, tokens=tokens)

        current_time = time.time()
        self.redis_repository.save_session(telegram_id, session, action_lifetime=int(action_token.exp - current_time),
                                           refresh_lifetime=int(refresh_token.exp - current_time))

        return session

    async def get_session_by_telegram_id_async(self, telegram_id):
        session: UserSession = self.redis_repository.get_session(telegram_id)
        if session:
            if not session.tokens.action_token:
                token = await self.api_repository.refresh_action_by_refresh_token_async(session.tokens.refresh_token)
                if not token:
                    return None

                session.tokens.action_token = token

                action_token: JwtToken = TokenParser.parse_jwt(token)
                current_time = time.time()
                self.redis_repository.update_user_token(telegram_id, token, token_type="action", lifetime=int(action_token.exp - current_time))

            return session


        tokens: UserSessionTokens = await self.api_repository.signin_by_telegram_id_async(telegram_id)
        if not tokens:
            return None

        return self.parse_and_save_session(telegram_id, tokens)

    async def signup_user_async(self, telegram_id, first_name, last_name):
        tokens: UserSessionTokens = await self.api_repository.signup_telegram_id_async(first_name, last_name, telegram_id)
        if not tokens:
            return None

        return self.parse_and_save_session(telegram_id, tokens)