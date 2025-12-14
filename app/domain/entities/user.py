from dataclasses import dataclass


@dataclass
class UserEntity:
    user_id: int
    email: str
    unique_username: str
    nickname: str
    subscriptions: list[str]
    password_hash: str | None = None
