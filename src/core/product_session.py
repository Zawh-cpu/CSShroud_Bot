from dataclasses import dataclass


@dataclass
class ProductSession:
    temp_id: int
    attributes: dict
    files: dict