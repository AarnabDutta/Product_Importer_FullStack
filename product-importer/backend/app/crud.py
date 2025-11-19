# Database operations (CRUD logic)
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models import Product, Webhook
from app.schemas import ProductCreate, ProductUpdate, WebhookCreate, WebhookUpdate
from typing import Optional, List


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    return db.query(Product).filter(func.lower(Product.sku) == sku.lower()).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sku: Optional[str] = None,
    name: Optional[str] = None,
    active: Optional[bool] = None,
    description: Optional[str] = None
) -> tuple[List[Product], int]:
    query = db.query(Product)
    
    if sku:
        query = query.filter(Product.sku.ilike(f"%{sku}%"))
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if active is not None:
        query = query.filter(Product.active == active)
    if description:
        query = query.filter(Product.description.ilike(f"%{description}%"))
    
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return products, total


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate) -> Optional[Product]:
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True


def delete_all_products(db: Session) -> int:
    count = db.query(Product).delete()
    db.commit()
    return count


def get_webhook(db: Session, webhook_id: int) -> Optional[Webhook]:
    return db.query(Webhook).filter(Webhook.id == webhook_id).first()


def get_webhooks(db: Session, skip: int = 0, limit: int = 100) -> List[Webhook]:
    return db.query(Webhook).offset(skip).limit(limit).all()


def create_webhook(db: Session, webhook: WebhookCreate) -> Webhook:
    db_webhook = Webhook(**webhook.model_dump())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


def update_webhook(db: Session, webhook_id: int, webhook: WebhookUpdate) -> Optional[Webhook]:
    db_webhook = get_webhook(db, webhook_id)
    if not db_webhook:
        return None
    
    update_data = webhook.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_webhook, field, value)
    
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


def delete_webhook(db: Session, webhook_id: int) -> bool:
    db_webhook = get_webhook(db, webhook_id)
    if not db_webhook:
        return False
    
    db.delete(db_webhook)
    db.commit()
    return True
