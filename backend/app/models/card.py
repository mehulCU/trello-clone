from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, default="")
    cover_image = Column(String, nullable=True)
    position = Column(Integer, default=0)
    list_id = Column(Integer, ForeignKey("lists.id"))
    archived = Column(Boolean, default=False)
    due_date = Column(String, nullable=True)

    labels = relationship("Label", cascade="all, delete")
    checklist = relationship("ChecklistItem", cascade="all, delete")
    members = relationship("CardMember", cascade="all, delete")
    attachments = relationship("Attachment", cascade="all, delete")
    comments = relationship("Comment", backref="card")
    activities = relationship("Activity", backref="card")

    # 🔥 CASCADE LINK
    list_id = Column(Integer, ForeignKey("lists.id", ondelete="CASCADE"))