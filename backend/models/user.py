from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile info
    full_name = Column(String, index=True)
    company_name = Column(String)
    phone_number = Column(String)
    
    # Subscriptions
    subscription_tier = Column(String, default="free") # free, starter, growth, pro
    subscription_status = Column(String, default="active") # inactive, active, past_due, canceled
    
    # Payment Gateway specific IDs (for mapping webhooks)
    stripe_customer_id = Column(String, unique=True, index=True, nullable=True)
    razorpay_customer_id = Column(String, unique=True, index=True, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
