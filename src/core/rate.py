from dataclasses import dataclass


@dataclass
class Rate:
    id: int
    name: str
    cost: int
    vpnLevel: int
    maxKeys: int
    trafficSpeedLimit: int
    maxConnections: int
    isPrivate: bool