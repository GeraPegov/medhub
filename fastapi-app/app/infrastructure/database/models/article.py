from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.connection import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.comment import Comment
    from app.infrastructure.database.models.reaction import Reaction
    from app.infrastructure.database.models.user import User


class Article(Base, AsyncAttrs):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    like: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    dislike: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    views_counter: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    reactions: Mapped[list["Reaction"]] = relationship(
        "Reaction", back_populates="articles"
    )
    users: Mapped["User"] = relationship("User", back_populates="articles")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="articles"
    )
