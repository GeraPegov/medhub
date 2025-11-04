from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    username: str
    password_hash: str