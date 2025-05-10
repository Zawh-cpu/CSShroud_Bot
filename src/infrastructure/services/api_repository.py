import aiohttp

from src import UserData
from src.core import UserSessionTokens
from src.application.dtos import KeysDto


class ApiRepository:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.base_url = config.BASE_URL
            cls._instance.headers = {"Authorization": f"Bearer {config.API_KEY}"}
            cls._instance.session = aiohttp.ClientSession(headers=cls._instance.headers)
        return cls._instance

    async def close(self):
        await self.session.close()

    async def signin_by_telegram_id_async(self, telegram_id: int) -> UserSessionTokens or None:
        async with self.session.post(f"{self.base_url}/api/v1/telegram/signin", json={"telegramId": telegram_id}) as response:
            if response.status != 200:
                return None

            tokens = await response.json()
            return UserSessionTokens(action_token=tokens.get("actionToken"), refresh_token=tokens.get("refreshToken"))

    async def signup_telegram_id_async(self, first_name: str, last_name: str, telegram_id: int) -> UserSessionTokens or None:
        async with self.session.post(f"{self.base_url}/api/v1/telegram/signup", json={"firstName": first_name, "lastName": last_name, "telegramId": telegram_id}) as response:
            if response.status != 200:
                return None

            tokens = await response.json()
            return UserSessionTokens(action_token=tokens.get("actionToken"), refresh_token=tokens.get("refreshToken"))

    async def refresh_action_by_refresh_token_async(self, refresh_token: str) -> str or None:
        async with self.session.get(f"{self.base_url}/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}) as response:
            if response.status != 200:
                return None
            return (await response.json()).get("actionToken")

    async def get_user_info_async(self, action_token: str) -> UserData or None:
        async with self.session.get(f"{self.base_url}/api/v1/user/me", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return None
            return UserData(await response.json())

    async def get_product_tags(self) -> list:
        async with self.session.get(f"{self.base_url}/api/v1/product/tags") as response:
            if response.status != 200:
                return list()
            return await response.json()

    async def get_rates(self) -> list:
        async with self.session.get(f"{self.base_url}/api/v1/rate/rates") as response:
            if response.status != 200:
                return list()
            return await response.json()

    async def get_my_keys(self, action_token: str, page=0, size=5) -> KeysDto or None:
        async with self.session.get(f"{self.base_url}/api/v1/key?size={size}&page={page}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return None

            return KeysDto(keys_count=response.headers.get("X-Total-Count"),
                           active_keys=response.headers.get("X-Enabled-Count"),
                           keys=await response.json())