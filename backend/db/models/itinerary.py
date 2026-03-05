from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from db.base import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    state = Column(String(20), nullable=False, default="DRAFT")  # DRAFT / REVIEW / LOCKED
    confidence_score = Column(Integer, nullable=False, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
