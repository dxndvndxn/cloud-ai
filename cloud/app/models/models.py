# models.py
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func
from app.models.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="создано описание", nullable=False)
    allure = Column(Text, default=None, nullable=True)
    code = Column(Text, default=None, nullable=True)
    apply = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())