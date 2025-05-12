from enum import Enum


class VpnProtocol(Enum):
    Unknown = -1
    Vless = 0

    @classmethod
    def from_str(cls, name: str):
        return cls.__members__.get(name, VpnProtocol.Unknown)
