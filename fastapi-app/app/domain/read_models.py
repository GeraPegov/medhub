from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleReadModel:
    article_id: int
    user_id: int
    title: str
    content: str
    category: str
    created_at: datetime
    likes: int
    dislikes: int
    author_username: str
    author_nickname: str


@dataclass
class CommentReadModel:
    id: int
    user_id: int
    article_id: int
    content: str
    created_at: datetime
    author_username: str
    author_nickname: str
