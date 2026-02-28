import os
import httpx
from typing import Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

async def generate_marketing_copy(prompt: str, language: str = "English", tone: str = "Professional") -> Optional[str]:
    """
    Calls OpenAI API to generate marketing copy in a specific language and tone.
    """
    if not OPENAI_API_KEY:
        # Mock response for development
        return f"[MOCK AI RESPONSE]\nGenerated a {tone} marketing copy in {language} about: {prompt}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = f"You are an expert digital marketing copywriter for Indian SMBs. Write highly converting marketing text. Language: {language}. Tone: {tone}."
    
    payload = {
        "model": "gpt-4o",  # or gpt-3.5-turbo
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a WhatsApp/Email marketing message for the following: {prompt}. Include emojis where appropriate but keep it professional."}
        ],
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None

async def agentic_chat_response(customer_message: str, business_context: str) -> Optional[str]:
    """
    Generates a smart, autonomous reply based on the customer's message and the business's context (e.g., booking availability).
    """
    if not OPENAI_API_KEY:
        return "[MOCK AI AGENT] This would be an intelligent contextual response."
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = f"You are a helpful AI customer service agent for an Indian business. The business details are: {business_context}. Answer the user's question accurately in a friendly tone. If you are asked to book something, assume it is possible if requested. Keep it concise for WhatsApp."
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": customer_message}
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error acting as AI Agent: {e}")
            return None
