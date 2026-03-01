from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Contact details
    name = Column(String, index=True)
    phone = Column(String, index=True)
    email = Column(String, nullable=True)
    
    # Organization / categorization
    tags = Column(String, default="")  # comma-separated tags like "vip,diwali-2024,new-lead"
    notes = Column(Text, default="")
    source = Column(String, default="manual")  # manual, csv_import, justdial, referral
    
    # Engagement tracking
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    total_messages_sent = Column(Integer, default=0)
    total_messages_opened = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    owner = relationship("User", back_populates="contacts")
