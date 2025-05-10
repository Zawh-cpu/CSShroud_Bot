from dataclasses import dataclass


@dataclass
class KeysDto:
    keys: list
    keys_count: int
    active_keys: int