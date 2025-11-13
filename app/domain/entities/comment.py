from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommentEntity:
    id: int
    author_id: int
    article_id: int
    content: str
    datetime: datetime
    author: str | None = None
