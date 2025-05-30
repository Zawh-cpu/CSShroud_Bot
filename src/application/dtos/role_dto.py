from dataclasses import dataclass


class RoleDto:
    id: int
    name: str

    def __init__(self, data: dict):
        self.id = data['id']
        self.name = data['name']