from dataclasses import dataclass


@dataclass
class QuickAuthInfoDto:
    id: str
    variants: list[int]

    def __init__(self, data):
        self.id = data.get("id")
        self.variants = data.get("variants")