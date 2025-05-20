from dataclasses import dataclass


@dataclass
class VlessConnection:
    host: str
    port: int
    uuid: str
    flow: str
    server_name: str
    insecure: bool
    public_key: str
    short_id: str

    def __init__(self, data):
        self.host = data['host']
        self.port = data['port']
        self.uuid = data['uuid']
        self.flow = data['flow']
        self.server_name = data['serverName']
        self.insecure = data['insecure']
        self.public_key = data['publicKey']
        self.short_id = data['shortId']