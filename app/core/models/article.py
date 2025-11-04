from datetime import date
from sqlalchemy import Integer, String, Text, Date, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Article(Base):
    __tablename__ = 'article'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[str] = mapped_column(String(64))
    date_add: Mapped[date] = mapped_column(Date, server_default=func.now())
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)