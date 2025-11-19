from dataclasses import dataclass


@dataclass
class UserEntity:
    id: int
    email: str
    username: str
    password_hash: str
    nickname: str
