from sqlalchemy import JSON, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from db.base import Base

class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)

    destination_type = Column(String(50), nullable=True)

    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)

    days = Column(Integer, nullable=True)

    activities = Column(JSON, nullable=False, default=list)          # list[str]
    transport_mode = Column(String(40), nullable=True)

    dietary_preferences = Column(JSON, nullable=False, default=list) # list[str]
    travel_pace = Column(String(30), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
    group = relationship("Group")
