# Webhook management endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.utils.webhook_trigger import test_webhook

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.get("", response_model=list[schemas.WebhookResponse])
def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_webhooks(db, skip=skip, limit=limit)


@router.get("/{webhook_id}", response_model=schemas.WebhookResponse)
def get_webhook(webhook_id: int, db: Session = Depends(get_db)):
    webhook = crud.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.post("", response_model=schemas.WebhookResponse, status_code=201)
def create_webhook(webhook: schemas.WebhookCreate, db: Session = Depends(get_db)):
    return crud.create_webhook(db, webhook)


@router.put("/{webhook_id}", response_model=schemas.WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook: schemas.WebhookUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_webhook(db, webhook_id, webhook)
    if not updated:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return updated


@router.delete("/{webhook_id}", status_code=204)
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    success = crud.delete_webhook(db, webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")


@router.post("/{webhook_id}/test", response_model=schemas.WebhookTestResponse)
async def test_webhook_endpoint(webhook_id: int, db: Session = Depends(get_db)):
    webhook = crud.get_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    result = await test_webhook(webhook.url)
    return result
