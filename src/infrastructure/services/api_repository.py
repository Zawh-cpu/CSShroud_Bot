import aiohttp

from src import UserData, VpnProtocol
from src.application.dtos.key_connection_dto import KeyConnectionDto
from src.core import UserSessionTokens
from src.core import Key
from src.application.dtos import KeysDto, AddKeyDto, Result, PatchKeyDto, GetUsersDto, GetUserDto, PatchUserDto, RoleDto, QuickAuthInfoDto


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

    async def signin_by_telegram_id_async(self, telegram_id: int) -> Result[UserSessionTokens]:
        async with self.session.post(f"{self.base_url}/api/v1/telegram/signin", json={"telegramId": telegram_id}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            tokens = await response.json()
            return Result(status_code=response.status, value=UserSessionTokens(action_token=tokens.get("actionToken"), refresh_token=tokens.get("refreshToken")))

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

    async def get_protocols(self) -> list:
        async with self.session.get(f"{self.base_url}/api/v1/protocol/available") as response:
            if response.status != 200:
                return list()
            return [VpnProtocol.from_str(data) for data in await response.json()]

    async def get_my_keys(self, action_token: str, page=0, size=5) -> KeysDto or None:
        async with self.session.get(f"{self.base_url}/api/v1/key?size={size}&page={page}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return None

            return KeysDto(keys_count=int(response.headers.get("X-Total-Count", "0")),
                           active_keys=int(response.headers.get("X-Enabled-Count", "0")),
                           keys=[Key(key) for key in await response.json()])

    async def add_key(self, data: AddKeyDto, action_token: str) -> Result:
        async with self.session.post(f"{self.base_url}/api/v1/key", json=data.dump(), headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=(await response.json()).get("id"))

    async def get_key(self, key_id: str, action_token: str) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/key/{key_id}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=Key(await response.json()))

    async def key_turn_on(self, key_id: str, action_token: str) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/key/{key_id}/switch/enable", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=None)

    async def key_turn_off(self, key_id: str, action_token: str) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/key/{key_id}/switch/disable", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=None)

    async def key_patch(self, key_id: str, patch_data: PatchKeyDto, action_token: str) -> Result:
        async with self.session.patch(f"{self.base_url}/api/v1/key/{key_id}", json=patch_data.dump(), headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=None)

    async def key_delete(self, key_id: str, action_token: str) -> Result:
        async with self.session.delete(f"{self.base_url}/api/v1/key/{key_id}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            return Result(status_code=response.status, value=None)

    async def key_get_connect_data(self, key_id: str, action_token: str) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/key/{key_id}/connect", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=KeyConnectionDto(await response.json()))

    async def get_users(self, action_token: str, page=0, size=10) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/user/users?size={size}&page={page}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=GetUsersDto(users_count=int(response.headers.get("X-Total-Count", "0")), users=[GetUserDto(x) for x in await response.json()]))

    async def get_user_by_id_info_async(self, user_id: str, action_token: str) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/user/{user_id}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=UserData(await response.json()))

    async def user_delete_async(self, user_id: str, action_token: str) -> Result:
        async with self.session.delete(f"{self.base_url}/api/v1/user/{user_id}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            return Result(status_code=response.status, value=None)

    async def user_patch_async(self, user_id: str, dto: PatchUserDto, action_token: str) -> Result:
        async with self.session.patch(f"{self.base_url}/api/v1/user/{user_id}", json=dto.dump(), headers={"Authorization": f"Bearer {action_token}"}) as response:
            return Result(status_code=response.status, value=None)

    async def get_roles_async(self) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/role/roles") as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=[RoleDto(x) for x in await response.json()])

    async def get_quickauth_data_async(self, fl_id: str) -> Result:
        async with self.session.get(f"{self.base_url}/api/v1/auth/quick-auth/{fl_id}/info") as response:
            if response.status != 200:
                return Result(status_code=response.status, value=None)

            return Result(status_code=response.status, value=QuickAuthInfoDto(await response.json()))

    async def quickauth_try_claim_async(self, fl_id: str, variant: int, action_token: str) -> Result:
        async with self.session.post(f"{self.base_url}/api/v1/auth/quick-auth/{fl_id}/confirm?variant={variant}", headers={"Authorization": f"Bearer {action_token}"}) as response:
            print(response.status)
            print(await response.text())
            return Result(status_code=response.status)
