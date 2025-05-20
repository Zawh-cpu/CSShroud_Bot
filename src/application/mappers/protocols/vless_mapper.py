from .protocol_mapper import ProtocolMapper
from src.application.dtos import KeyConnectionDto
from src.application.dtos.connection import VlessConnection


class VlessMapper(ProtocolMapper):

    @staticmethod
    def get_link(connection_info: KeyConnectionDto, name: str):
        creds = VlessConnection(connection_info.credentials)

        return rf"vless://{creds.uuid}@{creds.host}:{creds.port}/?fp=random&pbk={creds.public_key}&sid={creds.public_key}&sni={creds.server_name}&spx=%2F&flow={creds.flow}&type=tcp&security=reality#{name}"
