"""Pydantic schemas for customer phone endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerPhoneBase(BaseModel):
    customer_id: int
    contact_id: Optional[int] = None
    phone_number: str
    normalized_phone: Optional[str] = None
    phone_type: Optional[str] = None
    label: Optional[str] = None
    is_primary: bool = False
    source: str = "manual"


class CustomerPhoneCreate(CustomerPhoneBase):
    pass


class CustomerPhoneUpdate(BaseModel):
    customer_id: Optional[int] = None
    contact_id: Optional[int] = None
    phone_number: Optional[str] = None
    normalized_phone: Optional[str] = None
    phone_type: Optional[str] = None
    label: Optional[str] = None
    is_primary: Optional[bool] = None
    source: Optional[str] = None


class CustomerPhoneOut(CustomerPhoneBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
