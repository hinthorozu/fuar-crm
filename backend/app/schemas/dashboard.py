"""Pydantic schemas for dashboard endpoints."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class DashboardCounts(BaseModel):
    customers: int
    contacts: int
    phones: int
    emails: int
    fairs: int
    fair_participations: int
    notes: int
    import_batches: int
    import_rows_pending_decision: int


class RecentCustomer(BaseModel):
    id: int
    company_name: str
    country: Optional[str] = None
    city: Optional[str] = None
    source: str
    created_at: datetime


class RecentFair(BaseModel):
    id: int
    fair_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[date] = None
    created_at: datetime


class DashboardSummary(BaseModel):
    counts: DashboardCounts
    recent_customers: list[RecentCustomer]
    recent_fairs: list[RecentFair]
