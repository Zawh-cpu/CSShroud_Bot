from dataclasses import dataclass

SUCCESS_CODES = {200, 201, 204}

@dataclass
class Result:
    status_code: int
    value: object

    def is_success(self):
        if self.status_code in SUCCESS_CODES:
            return True
        return False