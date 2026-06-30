"""Contact management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Contact, Customer
from app.schemas.contact import ContactCreate, ContactOut, ContactUpdate
from app.utils.normalization import normalize_text

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def ensure_customer_exists(customer_id: int, db: Session):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")


def apply_contact_normalization(data: dict) -> dict:
    if data.get("full_name") and not data.get("normalized_full_name"):
        data["normalized_full_name"] = normalize_text(data["full_name"])
    return data


@router.post("/", response_model=ContactOut, status_code=201)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    ensure_customer_exists(contact.customer_id, db)
    new_contact = Contact(**apply_contact_normalization(contact.model_dump()))
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.get("/", response_model=List[ContactOut])
def list_contacts(customer_id: Optional[int] = None, search: Optional[str] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(Contact)
    if not include_deleted:
        query = query.filter(Contact.is_deleted == False)  # noqa: E712
    if customer_id:
        query = query.filter(Contact.customer_id == customer_id)
    if search:
        query = query.filter(
            or_(
                Contact.full_name.ilike(f"%{search}%"),
                Contact.normalized_full_name.ilike(f"%{search}%"),
                Contact.title.ilike(f"%{search}%"),
                Contact.department.ilike(f"%{search}%"),
                Contact.phone.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
            )
        )
    return query.order_by(Contact.full_name.asc()).all()


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.is_deleted == False).first()  # noqa: E712
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.is_deleted == False).first()  # noqa: E712
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = apply_contact_normalization(contact_update.model_dump(exclude_unset=True))
    if "customer_id" in update_data:
        ensure_customer_exists(update_data["customer_id"], db)

    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.is_deleted == False).first()  # noqa: E712
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_deleted = True
    contact.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Contact soft deleted successfully"}
