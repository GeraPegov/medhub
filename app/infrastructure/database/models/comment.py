from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.article import Article
    from app.infrastructure.database.models.client import Client

class Comment(Base, AsyncAttrs):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('client.id'))
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey('article.id'))

    article: Mapped['Article'] = relationship('Article', back_populates='comments')
    author: Mapped['Client'] = relationship('Client', back_populates='comments')
