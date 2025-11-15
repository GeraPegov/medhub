from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommentEntity:
    author_id: int
    article_id: int
    content: str
    created_at: datetime
    author: str | None = None
    id: int | None = None
