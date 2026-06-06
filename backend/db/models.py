from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP
from .database import Base

class ScamMessage(Base):
    __tablename__ = "scam_messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    verdict = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=True)
    category = Column(String(50), nullable=True)
    source_type = Column(String(20), nullable=True)
    sender_info = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
