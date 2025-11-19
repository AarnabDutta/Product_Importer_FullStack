# Pydantic models for request/response
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    sku: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    sku: Optional[str] = None
    name: Optional[str] = None
    active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebhookBase(BaseModel):
    url: str = Field(..., max_length=500)
    event_type: str = Field(..., max_length=50)
    enabled: bool = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    event_type: Optional[str] = None
    enabled: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebhookTestResponse(BaseModel):
    success: bool
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    task_id: str
    message: str


class ProgressResponse(BaseModel):
    state: str
    current: int
    total: int
    percent: float
    status: str


class PaginatedProductResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int
