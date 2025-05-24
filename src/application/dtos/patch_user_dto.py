from dataclasses import dataclass


@dataclass
class PatchUserDto:
    nickname: str or None
    login: str or None
    password: str or None
    role_id: int or None
    rate_id: int or None
    rate_payed_until: str or None
    is_active: bool or None
    is_verified: bool or None

    def __init__(self, **kwargs):
        self.nickname = kwargs.get('nickname')
        self.login = kwargs.get('login')
        self.password = kwargs.get('password')
        self.role_id = kwargs.get('role_id')
        self.rate_id = kwargs.get('rate_id')
        self.rate_payed_until = kwargs.get('rate_payed_until')
        self.is_active = kwargs.get('is_active')
        self.is_verified = kwargs.get('is_verified')

    def dump(self):
        return {
            "nickname": self.nickname,
            "login": self.login,
            "password": self.password,
            "roleId": self.role_id,
            "rateId": self.rate_id,
            "ratePayedUntil": self.rate_payed_until,
            "isActive": self.is_active,
            "isVerified": self.is_verified,
        }