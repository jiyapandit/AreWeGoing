from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime, func

from db.base import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("itinerary_id", "user_id", name="uq_vote_itinerary_user"),)

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(String(20), nullable=False)  # APPROVE / CHANGES
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
