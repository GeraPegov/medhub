from dataclasses import dataclass
from datetime import date


@dataclass
class ArticleEntity:
    unique_username: str
    title: str
    content: str
    author_id: int
    nickname: str | None = None
    category: str | None = None
    created_at: date | None = None
    id: int | None = None


