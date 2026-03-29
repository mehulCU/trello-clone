from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)

    # ✅ REQUIRED
    card_id = Column(Integer, ForeignKey("cards.id"))