# Product CRUD endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import crud, schemas
import math

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=schemas.PaginatedProductResponse)
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sku: Optional[str] = None,
    name: Optional[str] = None,
    active: Optional[bool] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    products, total = crud.get_products(
        db, skip=skip, limit=size, 
        sku=sku, name=name, active=active, description=description
    )
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=schemas.ProductResponse, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    existing = crud.get_product_by_sku(db, product.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")


@router.delete("", status_code=200)
def delete_all_products(db: Session = Depends(get_db)):
    count = crud.delete_all_products(db)
    return {"message": f"Deleted {count} products", "count": count}
