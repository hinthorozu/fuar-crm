"""Composite schemas for customer profile views."""

from typing import List

from pydantic import BaseModel

from app.schemas.contact import ContactOut
from app.schemas.customer import CustomerOut
from app.schemas.customer_email import CustomerEmailOut
from app.schemas.customer_phone import CustomerPhoneOut
from app.schemas.fair_participation import FairParticipationOut
from app.schemas.note import NoteOut


class CustomerProfileOut(BaseModel):
    customer: CustomerOut
    contacts: List[ContactOut]
    phones: List[CustomerPhoneOut]
    emails: List[CustomerEmailOut]
    fair_participations: List[FairParticipationOut]
    notes: List[NoteOut]
