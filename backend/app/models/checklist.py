from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class ChecklistItem(Base):
    __tablename__ = "checklist"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    completed = Column(Boolean, default=False)

    # ✅ THIS IS THE FIX
    card_id = Column(Integer, ForeignKey("cards.id"))