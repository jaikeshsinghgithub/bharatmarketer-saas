from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import stripe
import razorpay
import hmac
import hashlib
import json

from core.config import settings
from database import get_db
from models.user import User
from api.deps import get_current_active_user

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize Razorpay Client
razorpay_client = None
if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Pricing Plans (Hardcoded for beta MVP)
PLANS = {
    "starter_inr": {"razorpay_plan_id": "plan_starter", "stripe_price_id": "price_starter_inr", "name": "starter"},
    "growth_inr": {"razorpay_plan_id": "plan_growth", "stripe_price_id": "price_growth_inr", "name": "growth"},
    "pro_inr": {"razorpay_plan_id": "plan_pro", "stripe_price_id": "price_pro_inr", "name": "pro"},
}

@router.post("/create-stripe-checkout")
async def create_stripe_checkout(
    plan_key: str, 
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a Stripe checkout session for global users.
    """
    if plan_key not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
        
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': PLANS[plan_key]["stripe_price_id"],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url="https://bharatmarketer.in/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://bharatmarketer.in/pricing",
            client_reference_id=str(current_user.id)
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-razorpay-subscription")
async def create_razorpay_subscription(
    plan_key: str, 
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a Razorpay subscription link for Indian users.
    """
    if plan_key not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
        
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Razorpay not configured")
        
    try:
        subscription_data = {
            "plan_id": PLANS[plan_key]["razorpay_plan_id"],
            "total_count": 12, # 1 year
            "customer_notify": 1,
            "notes": {
                "user_id": str(current_user.id)
            }
        }
        subscription = razorpay_client.subscription.create(data=subscription_data)
        return {"subscription_id": subscription['id'], "short_url": subscription.get('short_url')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Stripe Webhook handler
    """
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')
        customer_id = session.get('customer')
        
        if client_reference_id:
            user_id = int(client_reference_id)
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if user:
                user.stripe_customer_id = customer_id
                user.subscription_status = "active"
                # TODO: Retrieve actual plan name from Stripe subscription
                user.subscription_tier = "paid_stripe"
                await db.commit()

    return {"status": "success"}

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    X_Razorpay_Signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Razorpay Webhook handler
    """
    payload = await request.body()
    
    # Verify Signature
    expected_signature = hmac.new(
        bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if expected_signature != X_Razorpay_Signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    data = json.loads(payload)
    event_type = data.get('event')
    
    if event_type == 'subscription.authenticated' or event_type == 'subscription.charged':
        sub_entity = data['payload']['subscription']['entity']
        notes = sub_entity.get('notes', {})
        user_id_str = notes.get('user_id')
        
        if user_id_str:
            user_id = int(user_id_str)
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if user:
                user.razorpay_customer_id = sub_entity.get('customer_id')
                user.subscription_status = "active"
                user.subscription_tier = "paid_razorpay"
                await db.commit()
                
    return {"status": "success"}
