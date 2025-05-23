from dataclasses import dataclass

@dataclass
class GetUserDto:
    id: str

@dataclass
class GetUsersDto:
    users_count: int
    users: list[GetUserDto]

    def __init__(self, users_count, data):
        self.users_count = users_count