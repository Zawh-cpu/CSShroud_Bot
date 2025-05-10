import json
import datetime as dt
from dataclasses import dataclass

from src.core import Rate


@dataclass
class UserRole:
    id: str
    name: str
    roleLevel: int
    permissions: int

@dataclass
class UserData:
    id: str
    nickname: str
    login: str
    telegramId: str
    role: UserRole
    rate: Rate
    payed_until: dt.datetime or None
    created_at: dt.datetime
    last_login: dt.datetime or None
    is_verified: bool

    def __init__(self, data: dict):
        self.id = data['id']
        self.nickname = data['nickname']
        self.login = data['login']
        self.telegramId = data['telegramId']
        self.role = UserRole(**data['role'])
        self.rate = Rate(**data['rate'])

        payed_until = data.get('payedUntil') or data.get('payed_until')
        self.payed_until = dt.datetime.fromisoformat(payed_until) if payed_until else None

        self.created_at = dt.datetime.fromisoformat(data.get('createdAt') or data.get('created_at'))

        last_login = data.get('lastLogin') or data.get('last_login')
        self.last_login = dt.datetime.fromisoformat(last_login) if last_login else None

        self.is_verified = data.get('isVerified') or data.get('is_verified')

    def dump(self):
        dump_data = self.__dict__.copy()
        dump_data["role"] = dump_data["role"].__dict__
        dump_data["rate"] = dump_data["rate"].__dict__
        dump_data["payed_until"] = str(dump_data["payed_until"]) if dump_data["payed_until"] else None
        dump_data["created_at"] = str(dump_data["created_at"]) if dump_data["created_at"] else None
        dump_data["last_login"] = str(dump_data["last_login"]) if dump_data["last_login"] else None
        return json.dumps(dump_data)


@dataclass
class UserSessionTokens:
    refresh_token: str
    action_token: str


@dataclass
class UserSession:
    user_id: str
    tokens: UserSessionTokens
    data: UserData
