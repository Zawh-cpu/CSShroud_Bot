import datetime as dt

from dataclasses import dataclass
from enum import Enum
from src.core import VpnProtocol, Server


class KeyStatus(Enum):
    Disabled = 0
    Enabled = 1
    Revoked = 2

@dataclass
class Key:
    id: str
    name: str
    protocol: VpnProtocol
    server: Server
    user_id: str
    createdAt: dt.datetime
    status: KeyStatus

    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.protocol = VpnProtocol.from_str(data["protocol"])
        self.server = Server(data["server"])
        self.user_id = data["userId"]
        self.createdAt = data["createdAt"]
        self.status = KeyStatus(data["status"])
