from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, NotNullable, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.article import Article
    from app.infrastructure.database.models.comment import Comments


class User(Base, AsyncAttrs):
    __tablename__ = 'user'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    nickname: Mapped[str] = mapped_column(String(64))
    unique_username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    subscriptions: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSONB), default=list)
    publication_limit: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    first_publication_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    articles: Mapped[list['Article']] = relationship('Article', back_populates='author')
    comments: Mapped[list['Comments']] = relationship('Comments', back_populates='author')
