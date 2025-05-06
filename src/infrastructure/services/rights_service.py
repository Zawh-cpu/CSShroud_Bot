import pathlib
import json
import functools


class Rights:
    AdminAccess = 0

class RightsService:

    @staticmethod
    def has_access(access_path: int, bit_position: int) -> bool:
        return (access_path & (1 << bit_position)) != 0