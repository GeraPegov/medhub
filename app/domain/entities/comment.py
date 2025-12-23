from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommentEntity:
    author_id: int
    article_id: int
    content: str
    created_at: datetime
    unique_username: str
    nickname: str
    title_of_article: str
    id: int
