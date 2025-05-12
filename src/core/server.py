import datetime as dt

from dataclasses import dataclass


@dataclass
class Server:
    id: str
    location: str

    def __init__(self, data):
        self.id = data["id"]
        self.location = data["location"]
