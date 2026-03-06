from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from db.base import Base


class GroupMetricSnapshot(Base):
    __tablename__ = "group_metric_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    captured_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    group_size = Column(Integer, nullable=False, default=0)
    preference_completion_percent = Column(Integer, nullable=False, default=0)
    budget_alignment_score = Column(Integer, nullable=False, default=0)
    activity_match_score = Column(Integer, nullable=False, default=0)
    conflict_count = Column(Integer, nullable=False, default=0)
    itinerary_confidence_score = Column(Integer, nullable=False, default=0)
    approval_status = Column(String(60), nullable=False, default="NOT_STARTED")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
