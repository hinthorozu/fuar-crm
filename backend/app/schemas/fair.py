"""Pydantic schemas for fair endpoints."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FairBase(BaseModel):
    fair_name: str
    normalized_fair_name: Optional[str] = None
    organizer: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    website: Optional[str] = None
    is_active: bool = True


class FairCreate(FairBase):
    pass


class FairUpdate(BaseModel):
    fair_name: Optional[str] = None
    normalized_fair_name: Optional[str] = None
    organizer: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class FairOut(FairBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
