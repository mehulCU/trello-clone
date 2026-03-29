from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class List(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    position = Column(Integer, default=0)

    board_id = Column(Integer, ForeignKey("boards.id"))

    # 🔥 ORM CASCADE
    cards = relationship("Card", cascade="all, delete")