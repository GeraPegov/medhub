from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList

from app.infrastructure.database.connection import Base
from app.infrastructure.database.models.user import article_likes

if TYPE_CHECKING:
    from app.infrastructure.database.models.comment import Comments
    from app.infrastructure.database.models.user import User

class Article(Base, AsyncAttrs):
    __tablename__ = 'articles'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    category: Mapped[str] = mapped_column(String(64))
    like: Mapped[int] = mapped_column(Integer, default=0)
    dislike: Mapped[int] = mapped_column(Integer, default=0)

    like_by_users: Mapped[list['User']] = relationship('User', secondary=article_likes, back_populates='liked_articles')
    user: Mapped['User'] = relationship('User', back_populates='articles')
    comments: Mapped[list['Comments']] = relationship('Comments', back_populates='article')
