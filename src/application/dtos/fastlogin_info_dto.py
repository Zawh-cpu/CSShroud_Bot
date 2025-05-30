from dataclasses import dataclass


@dataclass
class FastLoginInfoDto:
    id: str
    variants: list[int]