from dataclasses import dataclass

from src.core import VpnProtocol


@dataclass
class AddKeyDto:
    protocol: VpnProtocol
    location = "frankfurt"
    name = None

    def dump(self):
        return {
            "protocol": self.protocol.name,
            "location": self.location,
            "name": self.name,
        }