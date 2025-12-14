from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleEntity:
    unique_username: str
    title: str
    content: str
    author_id: int
    nickname: str | None = None
    category: str | None = None
    created_at: datetime | None = None
    article_id: int | None = None


