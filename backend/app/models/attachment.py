from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    file_path = Column(String)
    card_id = Column(Integer, ForeignKey("cards.id"))