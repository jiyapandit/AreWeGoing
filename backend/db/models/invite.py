from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from db.base import Base


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    inviter_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(320), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="SENT")  # SENT / ACCEPTED / REVOKED
    delivery_status = Column(String(20), nullable=False, default="PENDING")  # PENDING / DELIVERED / FAILED / BOUNCED
    delivery_provider = Column(String(40), nullable=True)
    delivery_provider_id = Column(String(128), nullable=True)
    delivery_attempts = Column(Integer, nullable=False, default=0)
    delivery_last_error = Column(String(500), nullable=True)
    delivery_last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
