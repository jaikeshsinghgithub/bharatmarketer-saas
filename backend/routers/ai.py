from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from models.user import User
from api.deps import get_current_active_user
from services.ai import generate_marketing_copy, agentic_chat_response

router = APIRouter()

class CopyGenerationRequest(BaseModel):
    prompt: str
    language: str = "Hindi"
    tone: str = "Persuasive"

class AgentChatRequest(BaseModel):
    message: str
    business_context: str

@router.post("/generate-copy")
async def generate_copy(
    req: CopyGenerationRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Generates AI marketing copy based on user requirements.
    In real app, we'd deduct 'AI Credits' from the user's account here.
    """
    if current_user.subscription_status != "active":
        # Usually, basic plans might have a limit, pro plans unlimited
        pass

    generated_text = await generate_marketing_copy(req.prompt, req.language, req.tone)
    if not generated_text:
        raise HTTPException(status_code=500, detail="Failed to generate AI copy.")
        
    return {"status": "success", "content": generated_text}

@router.post("/agent-reply")
async def get_agent_reply(
    req: AgentChatRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Simulates the AI hitting a webhook from WhatsApp, processing the message against business context, and generating a reply.
    """
    if current_user.subscription_tier not in ["growth", "paid_stripe", "paid_razorpay"]:
        raise HTTPException(status_code=403, detail="Agentic AI requires Growth plan or higher.")
        
    reply = await agentic_chat_response(req.message, req.business_context)
    if not reply:
        raise HTTPException(status_code=500, detail="AI Agent failed to respond.")
        
    return {"status": "success", "agent_reply": reply}
