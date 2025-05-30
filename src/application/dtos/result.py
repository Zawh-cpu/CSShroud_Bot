from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

SUCCESS_CODES = {200, 201, 204}

@dataclass
class Result(Generic[T]):
    status_code: int
    value: Optional[T] = None

    def is_success(self):
        if self.status_code in SUCCESS_CODES:
            return True
        return False