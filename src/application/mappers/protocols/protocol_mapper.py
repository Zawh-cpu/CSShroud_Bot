from src.application.dtos import KeyConnectionDto


class ProtocolMapper:

    @staticmethod
    def get_link(connection_info: KeyConnectionDto, name: str):
        ...