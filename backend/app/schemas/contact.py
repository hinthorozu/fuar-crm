"""Pydantic schemas for contact endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContactBase(BaseModel):
    customer_id: int
    full_name: str
    normalized_full_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    note: Optional[str] = None
    is_primary: bool = False


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    customer_id: Optional[int] = None
    full_name: Optional[str] = None
    normalized_full_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    note: Optional[str] = None
    is_primary: Optional[bool] = None


class ContactOut(ContactBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
