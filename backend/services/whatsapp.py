import os
import httpx
import logging

logger = logging.getLogger(__name__)

# Basic settings for Meta WhatsApp API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_VERSION = "v18.0"

async def send_whatsapp_message(to_number: str, message_text: str):
    """
    Sends a simple text message via WhatsApp Cloud API.
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        from fastapi import HTTPException
        logger.error("WhatsApp API Keys missing.")
        raise HTTPException(status_code=500, detail="WhatsApp API Keys missing. Please configure WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID in your environment variables.")

    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"WhatsApp API Error: {e.response.text}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=f"Failed to send WhatsApp message. Meta API responded with error.")
        except Exception as e:
            logger.error(f"Unknown WhatsApp Error: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Failed to connect to Meta API.")

async def send_whatsapp_template(to_number: str, template_name: str, language_code: str = "en_US"):
    """
    Sends a pre-approved WhatsApp template.
    """
    # Implementation similar to text format
    pass
