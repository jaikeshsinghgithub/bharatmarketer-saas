from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from models.user import User
from api.deps import get_current_active_user
from services.whatsapp import send_whatsapp_message
from services.email import send_email

router = APIRouter()

class BulkMessageRequest(BaseModel):
    numbers: List[str]
    message: str

class EmailCampaignRequest(BaseModel):
    emails: List[str]
    subject: str
    html_content: str

@router.post("/whatsapp/send-bulk")
async def send_bulk_whatsapp(
    req: BulkMessageRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Send a bulk WhatsApp message to a list of numbers. 
    Requires user to have an active subscription (mock validation included).
    """
    if current_user.subscription_status != "active":
        raise HTTPException(status_code=403, detail="Active subscription required for bulk sending.")
        
    results = []
    for number in req.numbers:
        res = await send_whatsapp_message(number, req.message)
        results.append(res)
        
    return {"status": "success", "results": results}

@router.post("/email/send-campaign")
async def send_email_campaign(
    req: EmailCampaignRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Send an email campaign.
    """
    if current_user.subscription_status != "active":
        raise HTTPException(status_code=403, detail="Active subscription required.")
        
    results = []
    for email in req.emails:
        res = await send_email(email, req.subject, req.html_content)
        results.append(res)
        
    return {"status": "success", "results": results}
