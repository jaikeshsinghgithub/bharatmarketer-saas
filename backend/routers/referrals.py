from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.user import User
from database import get_db
from api.deps import get_current_active_user

router = APIRouter()

# --- Schemas ---
class ApplyReferralRequest(BaseModel):
    referral_code: str

class ReferralDashboardResponse(BaseModel):
    your_referral_code: str
    total_referrals: int
    referral_credits: int
    referral_link: str

# --- Constants ---
REFERRAL_CREDIT_REWARD = 1  # Each successful referral = 1 AI Credit Pack (₹199 worth)
REFERRED_USER_BONUS_CREDITS = 10  # New user who used a code gets 10 bonus AI credits

# --- Endpoints ---

@router.get("/dashboard", response_model=ReferralDashboardResponse)
async def get_referral_dashboard(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get the current user's referral dashboard showing their unique code,
    how many people they've referred, and credits earned.
    """
    return {
        "your_referral_code": current_user.referral_code,
        "total_referrals": current_user.total_referrals,
        "referral_credits": current_user.referral_credits,
        "referral_link": f"https://bharatmarketer.in/signup?ref={current_user.referral_code}"
    }

@router.post("/apply")
async def apply_referral_code(
    req: ApplyReferralRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Apply a referral code. Both the referrer and the new user get rewarded.
    This should be called once after a new user registers (or on first payment).
    """
    # Prevent self-referral
    if req.referral_code == current_user.referral_code:
        raise HTTPException(status_code=400, detail="You cannot refer yourself.")
    
    # Check if user already used a referral
    if current_user.referred_by_id is not None:
        raise HTTPException(status_code=400, detail="You have already used a referral code.")
    
    # Find the referrer
    result = await db.execute(select(User).where(User.referral_code == req.referral_code))
    referrer = result.scalars().first()
    
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code.")
    
    if referrer.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot refer yourself.")
    
    # --- Dual-Sided Reward ---
    
    # Reward the REFERRER
    referrer.referral_credits += REFERRAL_CREDIT_REWARD
    referrer.total_referrals += 1
    referrer.ai_credits_remaining += 20  # Bonus AI credits for bringing a new user
    
    # Reward the NEW USER
    current_user.referred_by_id = referrer.id
    current_user.ai_credits_remaining += REFERRED_USER_BONUS_CREDITS
    
    await db.commit()
    
    return {
        "status": "success",
        "message": f"Referral applied! You received {REFERRED_USER_BONUS_CREDITS} bonus AI credits. {referrer.full_name or referrer.email} earned a reward too!",
        "your_bonus_credits": REFERRED_USER_BONUS_CREDITS,
        "referrer_rewarded": True
    }

@router.get("/leaderboard")
async def referral_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Show top 10 referrers on the platform (gamification to encourage more referrals).
    """
    result = await db.execute(
        select(User.full_name, User.company_name, User.total_referrals)
        .where(User.total_referrals > 0)
        .order_by(User.total_referrals.desc())
        .limit(10)
    )
    leaders = result.all()
    return [
        {
            "rank": i + 1,
            "name": leader.full_name or leader.company_name or "Anonymous",
            "referrals": leader.total_referrals
        }
        for i, leader in enumerate(leaders)
    ]
