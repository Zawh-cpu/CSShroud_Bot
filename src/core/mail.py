from dataclasses import dataclass
from enum import Enum


class MailType(Enum):
    Unknown = -1
    Default = 0
    RateExpiration = 1
    RateExpired = 2

    @classmethod
    def from_str(cls, name: str):
        return cls.__members__.get(name, MailType.Unknown)


@dataclass
class UserMail:
    id: str
    nickname: str
    telegram_id: int
    is_verified: bool

    def __init__(self, data):
        self.id = data['id']
        self.nickname = data['nickname']
        self.telegram_id = data['telegramId']
        self.is_verified = data['isVerified']


@dataclass
class Mail:
    id: str
    recipient: UserMail
    sender: UserMail
    type: MailType
    title: str
    content: str
    extra_data: dict[str, object]

    def __init__(self, data):
        self.id = data['id']
        self.recipient = UserMail(data['recipient'])
        self.sender = UserMail(data['sender'])
        self.type = MailType.from_str(data['type'])
        self.title = data['title']
        self.content = data['content']
        self.extra_data = data['extraData']
