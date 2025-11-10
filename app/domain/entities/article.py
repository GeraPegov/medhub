from dataclasses import dataclass
from datetime import date


@dataclass
class ArticleEntity:
    author: str
    title: str
    article: str
    author_id: int
    date_add: date | None = None


