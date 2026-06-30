"""Pydantic schemas for fair participation endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FairParticipationBase(BaseModel):
    customer_id: int
    fair_id: int
    hall: Optional[str] = None
    stand_number: Optional[str] = None
    exhibitor_profile_url: Optional[str] = None
    external_exhibitor_id: Optional[str] = None
    participation_status: str = "active"
    source: str = "manual"


class FairParticipationCreate(FairParticipationBase):
    pass


class FairParticipationUpdate(BaseModel):
    customer_id: Optional[int] = None
    fair_id: Optional[int] = None
    hall: Optional[str] = None
    stand_number: Optional[str] = None
    exhibitor_profile_url: Optional[str] = None
    external_exhibitor_id: Optional[str] = None
    participation_status: Optional[str] = None
    source: Optional[str] = None


class FairParticipationOut(FairParticipationBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
