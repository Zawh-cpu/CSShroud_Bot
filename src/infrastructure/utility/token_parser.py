import jwt

from dataclasses import dataclass


@dataclass
class JwtToken:
    data: str
    jti: str
    exp: int
    sub: str


class TokenParser:

    @staticmethod
    def parse_jwt(token: str) -> JwtToken:
        data: dict = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
        return JwtToken(token, data.get("jti"), data.get("exp"), data.get("sub"))