from sqlalchemy import Column, Integer, String
from app.database import Base

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    background = Column(String, nullable=True)