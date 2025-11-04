from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Article(Base):
    __tablename__ = 'register'
    __table_args__ = None

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(64))
