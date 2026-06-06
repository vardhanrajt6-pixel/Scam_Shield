from .models import ScamMessage
from .database import SessionLocal

def insert_scam_message(message, verdict, confidence, category=None, source_type=None, sender_info=None):
    db = SessionLocal()
    scam = ScamMessage(
        message=message,
        verdict=verdict,
        confidence=confidence,
        category=category,
        source_type=source_type,
        sender_info=sender_info
    )
    db.add(scam)
    db.commit()
    db.refresh(scam)
    db.close()
    return scam

def get_all_scam_messages():
    db = SessionLocal()
    scams = db.query(ScamMessage).filter(ScamMessage.verdict == "scam").all()
    db.close()
    return scams
