from dataclasses import dataclass


@dataclass
class FastLoginInfoDto:
    id: str
    variants: list[int]

    def __init__(self, data):
        self.id = data.get("id")
        self.variants = data.get("variants")