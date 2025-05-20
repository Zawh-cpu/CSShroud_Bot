from dataclasses import dataclass

from src.core import VpnProtocol


@dataclass
class PatchKeyDto:
    name: str = None

    def dump(self):
        result = dict()
        if self.name:
            result["name"] = self.name

        return result