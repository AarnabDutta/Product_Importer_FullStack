# Webhook execution logic
import httpx
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Webhook
import time


async def trigger_webhooks(db: Session, event_type: str, payload: Dict[str, Any]):
    webhooks = db.query(Webhook).filter(
        Webhook.event_type == event_type,
        Webhook.enabled == True
    ).all()
    
    if not webhooks:
        return
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for webhook in webhooks:
            tasks.append(send_webhook(client, webhook.url, payload))
        
        await asyncio.gather(*tasks, return_exceptions=True)


async def send_webhook(client: httpx.AsyncClient, url: str, payload: Dict[str, Any]):
    try:
        response = await client.post(url, json=payload)
        return response.status_code
    except Exception as e:
        print(f"Webhook error for {url}: {str(e)}")
        return None


async def test_webhook(url: str) -> Dict[str, Any]:
    try:
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={"test": True, "message": "Webhook test from Product Importer"}
            )
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "status_code": response.status_code,
            "response_time": round(response_time, 3),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": str(e)
        }
