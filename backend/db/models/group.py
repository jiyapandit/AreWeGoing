from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from db.base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    is_public = Column(Boolean, default=False)
    join_code = Column(String(12), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
