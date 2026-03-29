from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    card_id = Column(Integer, ForeignKey("cards.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())