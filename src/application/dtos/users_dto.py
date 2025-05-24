from dataclasses import dataclass

@dataclass
class GetUserDto:
    id: str
    nickname: str
    telegram_id: int
    is_verified: bool

    def __init__(self, data):
        self.id = data["id"]
        self.nickname = data["nickname"]
        self.telegram_id = data["telegramId"]
        self.is_verified = data["isVerified"]

@dataclass
class GetUsersDto:
    users_count: int
    users: list[GetUserDto]