"""Pydantic schemas for note endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    customer_id: int
    contact_id: Optional[int] = None
    fair_id: Optional[int] = None
    fair_participation_id: Optional[int] = None
    detail: str
    note_type: Optional[str] = None
    created_by_user_id: Optional[int] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    customer_id: Optional[int] = None
    contact_id: Optional[int] = None
    fair_id: Optional[int] = None
    fair_participation_id: Optional[int] = None
    detail: Optional[str] = None
    note_type: Optional[str] = None
    created_by_user_id: Optional[int] = None


class NoteOut(NoteBase):
    id: int
    note_date: datetime
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
