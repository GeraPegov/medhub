from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleEntity:
    unique_username: str
    title: str
    content: str
    user_id: int
    nickname: str
    category: str
    created_at: datetime
    article_id: int
    likes: int
    dislikes: int
    reaction: str | None = None


