from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from db.base import Base


class InviteDeliveryAttempt(Base):
    __tablename__ = "invite_delivery_attempts"

    id = Column(Integer, primary_key=True, index=True)
    invite_id = Column(Integer, ForeignKey("invites.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    provider = Column(String(40), nullable=False)
    status = Column(String(20), nullable=False)  # DELIVERED / FAILED / BOUNCED
    provider_message_id = Column(String(128), nullable=True)
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
