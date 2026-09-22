from sqlalchemy import Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.connection import Base


class Admin(Base):
    __tablename__ = "admins"
    __table_args__ = (Index("admins_one_row", text("(true)"), unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    login: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
