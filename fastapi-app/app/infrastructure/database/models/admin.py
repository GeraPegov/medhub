from app.infrastructure.database.connection import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)