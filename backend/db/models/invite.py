from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from db.base import Base


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    inviter_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(320), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="SENT")  # SENT / ACCEPTED / REVOKED
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
