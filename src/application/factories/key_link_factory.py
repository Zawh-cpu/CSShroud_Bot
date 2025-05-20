from src import VpnProtocol
from src.application.dtos import KeyConnectionDto
from src.application.mappers import ProtocolMapper, VlessMapper


class KeyLinkFactory:
    _mappers: dict[VpnProtocol, ProtocolMapper] = {
        VpnProtocol.Vless: VlessMapper
    }

    @staticmethod
    def get_link(key_connection: KeyConnectionDto, name: str):
        mapper = KeyLinkFactory._mappers.get(key_connection.protocol)
        if mapper is None:
            raise Exception("error-unsupported-protocol")

        return mapper.get_link(key_connection, name)