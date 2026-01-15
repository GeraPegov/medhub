from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.article import Article
    from app.infrastructure.database.models.comment import Comments
    from app.infrastructure.database.models.reaction import Reaction


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
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')

    reaction: Mapped[list['Reaction']] = relationship('Reaction', back_populates='user')
    articles: Mapped[list['Article']] = relationship('Article', back_populates='user')
    comments: Mapped[list['Comments']] = relationship('Comments', back_populates='user')
