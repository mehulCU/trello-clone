from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class CardMember(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # ✅ REQUIRED
    card_id = Column(Integer, ForeignKey("cards.id"))