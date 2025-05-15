import datetime as dt

from dataclasses import dataclass


@dataclass
class Server:
    id: str
    location: str
    host: str
    port: int

    def __init__(self, data):
        self.id = data["id"]
        self.location = data["location"]
        self.host = data.get("host")
        self.port = int(data.get("port", 0))
