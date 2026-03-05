from sqlalchemy import Column, Integer, String, ForeignKey, Float

from db.base import Base


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_day_id = Column(Integer, ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    summary = Column(String(600), nullable=False)
    estimated_cost = Column(Integer, nullable=False)
    duration_hours = Column(Float, nullable=False)
    rationale = Column(String(500), nullable=False)
