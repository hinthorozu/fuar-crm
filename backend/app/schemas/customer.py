"""Pydantic schemas for customer endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    company_name: str
    normalized_company_name: Optional[str] = None
    website: Optional[str] = None
    normalized_website: Optional[str] = None
    main_phone: Optional[str] = None
    normalized_main_phone: Optional[str] = None
    tax_number: Optional[str] = None
    tax_office: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    source: str = "manual"
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    normalized_company_name: Optional[str] = None
    website: Optional[str] = None
    normalized_website: Optional[str] = None
    main_phone: Optional[str] = None
    normalized_main_phone: Optional[str] = None
    tax_number: Optional[str] = None
    tax_office: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerOut(CustomerBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
