from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    is_public = Column(Boolean, default=False)
    join_code = Column(String(12), unique=True, nullable=False, index=True)