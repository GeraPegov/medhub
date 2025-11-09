from dataclasses import dataclass
from datetime import date


@dataclass
class ArticleEntity:
    author: str
    title: str
    article: str
    date_add: date | None = None


