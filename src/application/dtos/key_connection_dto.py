from dataclasses import dataclass

from src.core import VpnProtocol


@dataclass
class KeyConnectionDto:
    id: str
    protocol: VpnProtocol
    credentials: dict[str, object]

    def __init__(self, data):
        self.id = data['id']
        self.protocol = VpnProtocol.from_str(data['protocol'])
        self.credentials = data['credentials']