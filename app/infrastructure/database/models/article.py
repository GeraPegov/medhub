from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.client import Client
    from app.infrastructure.database.models.comment import Comments

class Article(Base, AsyncAttrs):
    __tablename__ = 'articles'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('client.id'))
    created_at: Mapped[date] = mapped_column(DateTime, server_default=func.now())
    category: Mapped[str] = mapped_column(String(64))

    author: Mapped['Client'] = relationship('Client', back_populates='articles')
    comments: Mapped[list['Comments']] = relationship('Comments', back_populates='article')
