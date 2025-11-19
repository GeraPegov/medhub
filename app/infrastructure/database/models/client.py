from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.article import Article
    from app.infrastructure.database.models.comment import Comments


class Client(Base, AsyncAttrs):
    __tablename__ = 'client'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True)
    nickname: Mapped[str] = mapped_column(String(64))
    unique_username: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    articles: Mapped[list['Article']] = relationship('Article', back_populates='author')
    comments: Mapped[list['Comments']] = relationship('Comments', back_populates='author')
