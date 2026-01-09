from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.comment import Comments
    from app.infrastructure.database.models.user import User
    from app.infrastructure.database.models.reaction import Reaction


class Article(Base, AsyncAttrs):
    __tablename__ = 'articles'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', ondelete='SET NULL'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    category: Mapped[str] = mapped_column(String(64))
    like: Mapped[int] = mapped_column(Integer, default=0)
    dislike: Mapped[int] = mapped_column(Integer, default=0)

    reaction: Mapped[list['Reaction']] = relationship('Reaction', back_populates='article')
    user: Mapped['User'] = relationship('User', back_populates='articles')
    comments: Mapped[list['Comments']] = relationship('Comments', back_populates='article')
