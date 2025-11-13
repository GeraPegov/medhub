from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.article import Article
    from app.infrastructure.database.models.comment import Comment


class Client(Base, AsyncAttrs):
    __tablename__ = 'client'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(64))
    password_hash: Mapped[str] = mapped_column(String(255))

    articles: Mapped[list['Article']] = relationship('Article', back_populates='author')
    comments: Mapped[list['Comment']] = relationship('Comment', back_populates='author')
