from dataclasses import dataclass


@dataclass
class UserSessionTokens:
    refresh_token: str
    action_token: str

@dataclass
class UserRole:
    id: str
    name: str

@dataclass
class UserSession:
    user_id: str
    tokens: UserSessionTokens
