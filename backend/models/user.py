import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

def generate_referral_code():
    return uuid.uuid4().hex[:8].upper()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Profile info
    full_name = Column(String, index=True)
    company_name = Column(String)
    phone_number = Column(String)
    
    # Business context for AI Agent (e.g. "We are a dental clinic open 9 AM to 5 PM")
    business_context = Column(Text, default="")
    
    # Subscriptions
    subscription_tier = Column(String, default="free") # free, starter, growth, pro
    subscription_status = Column(String, default="active") # inactive, active, past_due, canceled
    
    # Payment Gateway specific IDs (for mapping webhooks)
    stripe_customer_id = Column(String, unique=True, index=True, nullable=True)
    razorpay_customer_id = Column(String, unique=True, index=True, nullable=True)
    
    # Referral Engine (USP #4)
    referral_code = Column(String, unique=True, index=True, default=generate_referral_code)
    referred_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    referral_credits = Column(Integer, default=0)  # Credits earned from referrals (₹199 packs)
    total_referrals = Column(Integer, default=0)    # Count of successful referrals
    
    # AI Usage Tracking
    ai_credits_remaining = Column(Integer, default=50)  # Free tier gets 50 AI generations
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
    referred_by = relationship("User", remote_side=[id], backref="referrals")
