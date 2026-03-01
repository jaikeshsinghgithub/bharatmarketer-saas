import os
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from database import get_db
from models.user import User
from services.ai import agentic_chat_response
from services.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter()

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "bharatmarketer_verify_token_2026")

@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> Any:
    """
    Meta WhatsApp Webhook Verification (GET request).
    When you register your webhook URL in the Meta Developer Dashboard, 
    Meta sends a GET request with a challenge token. We must echo it back.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully!")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/whatsapp")
async def receive_whatsapp_message(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Inbound WhatsApp Message Handler (POST request).
    
    This is the AUTONOMOUS AI AGENT (USP #2).
    
    Flow:
    1. Customer sends a WhatsApp message to the business's number.
    2. Meta forwards this message to our webhook URL.
    3. We extract the sender's number and message text.
    4. We look up which business owns this WhatsApp number.
    5. We read the business's context (e.g., "Dental clinic, open 9-5").
    6. We call GPT-4o with the customer message + business context.
    7. We send the AI-generated reply back to the customer via WhatsApp API.
    
    All of this happens instantly while the business owner sleeps.
    """
    body = await request.json()
    
    try:
        # Extract the incoming message from Meta's webhook payload
        entry = body.get("entry", [])
        if not entry:
            return {"status": "ok"}
        
        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ok"}
        
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            # This might be a status update (delivered, read), not an actual message
            return {"status": "ok"}
        
        # Get the incoming message details
        message = messages[0]
        sender_phone = message.get("from", "")
        message_type = message.get("type", "")
        
        # We only handle text messages for now
        if message_type != "text":
            logger.info(f"Received non-text message type: {message_type} from {sender_phone}")
            return {"status": "ok", "note": "Only text messages are supported by the AI agent currently."}
        
        message_text = message.get("text", {}).get("body", "")
        
        if not message_text:
            return {"status": "ok"}
        
        logger.info(f"Incoming WhatsApp from {sender_phone}: {message_text}")
        
        # Find the business owner who owns the WhatsApp number that received this message
        # The phone_number_id from the webhook tells us which business number was messaged
        metadata = value.get("metadata", {})
        display_phone = metadata.get("display_phone_number", "")
        
        # Look up the business owner by their registered phone number or by their WhatsApp number
        result = await db.execute(
            select(User).where(User.phone_number == display_phone)
        )
        business_owner = result.scalars().first()
        
        if not business_owner:
            # Fallback: use the first active user (for MVP/demo purposes)
            result = await db.execute(
                select(User).where(User.is_active == True).limit(1)
            )
            business_owner = result.scalars().first()
        
        if not business_owner:
            logger.warning("No business owner found for this WhatsApp number")
            return {"status": "ok"}
        
        # Check if the business owner has AI Agent enabled (Growth plan or higher)
        if business_owner.subscription_tier in ["free", "starter"]:
            logger.info(f"Business {business_owner.email} is on {business_owner.subscription_tier} plan - AI Agent not available")
            return {"status": "ok", "note": "AI Agent requires Growth plan or higher"}
        
        # Check AI credits
        if business_owner.ai_credits_remaining <= 0:
            logger.info(f"Business {business_owner.email} has no AI credits remaining")
            return {"status": "ok", "note": "No AI credits remaining"}
        
        # Get the business context for smart replies
        business_context = business_owner.business_context or f"Business: {business_owner.company_name or 'Unknown'}. Please assist the customer."
        
        # Generate the autonomous AI reply
        ai_reply = await agentic_chat_response(message_text, business_context)
        
        if not ai_reply:
            logger.error("AI Agent failed to generate a response")
            return {"status": "error", "note": "AI generation failed"}
        
        # Send the AI reply back to the customer via WhatsApp
        send_result = await send_whatsapp_message(sender_phone, ai_reply)
        
        # Deduct 1 AI credit
        business_owner.ai_credits_remaining -= 1
        await db.commit()
        
        logger.info(f"AI Agent replied to {sender_phone}: {ai_reply[:50]}...")
        
        return {
            "status": "success",
            "customer_phone": sender_phone,
            "customer_message": message_text,
            "ai_reply": ai_reply,
            "credits_remaining": business_owner.ai_credits_remaining
        }
        
    except Exception as e:
        logger.error(f"Error processing inbound WhatsApp message: {str(e)}")
        return {"status": "error", "detail": str(e)}
