from dataclasses import dataclass
from datetime import date


@dataclass
class ArticleEntity:
    author: str
    title: str
    content: str
    author_id: int
    date_add: date | None = None
    id: int | None = None


