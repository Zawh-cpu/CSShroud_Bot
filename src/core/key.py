from dataclasses import dataclass


@dataclass
class Key:
    id: str
    location_id: str
    protocol_id: str
    name: str
    is_active: bool
