"""Pydantic schemas for customer email endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CustomerEmailBase(BaseModel):
    customer_id: int
    contact_id: Optional[int] = None
    email: str
    normalized_email: Optional[str] = None
    email_type: Optional[str] = None
    label: Optional[str] = None
    is_primary: bool = False
    validation_status: str = "unknown"
    validation_message: Optional[str] = None
    source: str = "manual"


class CustomerEmailCreate(CustomerEmailBase):
    pass


class CustomerEmailUpdate(BaseModel):
    customer_id: Optional[int] = None
    contact_id: Optional[int] = None
    email: Optional[str] = None
    normalized_email: Optional[str] = None
    email_type: Optional[str] = None
    label: Optional[str] = None
    is_primary: Optional[bool] = None
    validation_status: Optional[str] = None
    validation_message: Optional[str] = None
    source: Optional[str] = None


class CustomerEmailOut(CustomerEmailBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
