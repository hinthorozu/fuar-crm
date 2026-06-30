"""Customer email management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Contact, Customer, CustomerEmail
from app.schemas.customer_email import CustomerEmailCreate, CustomerEmailOut, CustomerEmailUpdate
from app.utils.normalization import normalize_email

router = APIRouter(prefix="/customer-emails", tags=["Customer Emails"])


def ensure_customer_exists(customer_id: int, db: Session):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")


def ensure_contact_exists(contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.is_deleted == False).first()  # noqa: E712
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")


def apply_email_normalization(data: dict) -> dict:
    if data.get("email") and not data.get("normalized_email"):
        data["normalized_email"] = normalize_email(data["email"])
    return data


@router.post("/", response_model=CustomerEmailOut, status_code=201)
def create_customer_email(email: CustomerEmailCreate, db: Session = Depends(get_db)):
    ensure_customer_exists(email.customer_id, db)
    if email.contact_id is not None:
        ensure_contact_exists(email.contact_id, db)
    new_email = CustomerEmail(**apply_email_normalization(email.model_dump()))
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    return new_email


@router.get("/", response_model=List[CustomerEmailOut])
def list_customer_emails(customer_id: Optional[int] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(CustomerEmail)
    if not include_deleted:
        query = query.filter(CustomerEmail.is_deleted == False)  # noqa: E712
    if customer_id:
        query = query.filter(CustomerEmail.customer_id == customer_id)
    return query.order_by(CustomerEmail.id.desc()).all()


@router.get("/{email_id}", response_model=CustomerEmailOut)
def get_customer_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(CustomerEmail).filter(CustomerEmail.id == email_id, CustomerEmail.is_deleted == False).first()  # noqa: E712
    if not email:
        raise HTTPException(status_code=404, detail="Customer email not found")
    return email


@router.put("/{email_id}", response_model=CustomerEmailOut)
def update_customer_email(email_id: int, email_update: CustomerEmailUpdate, db: Session = Depends(get_db)):
    email = db.query(CustomerEmail).filter(CustomerEmail.id == email_id, CustomerEmail.is_deleted == False).first()  # noqa: E712
    if not email:
        raise HTTPException(status_code=404, detail="Customer email not found")

    update_data = apply_email_normalization(email_update.model_dump(exclude_unset=True))
    if "customer_id" in update_data:
        ensure_customer_exists(update_data["customer_id"], db)
    if update_data.get("contact_id") is not None:
        ensure_contact_exists(update_data["contact_id"], db)

    for field, value in update_data.items():
        setattr(email, field, value)

    db.commit()
    db.refresh(email)
    return email


@router.delete("/{email_id}")
def delete_customer_email(email_id: int, db: Session = Depends(get_db)):
    email = db.query(CustomerEmail).filter(CustomerEmail.id == email_id, CustomerEmail.is_deleted == False).first()  # noqa: E712
    if not email:
        raise HTTPException(status_code=404, detail="Customer email not found")

    email.is_deleted = True
    email.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Customer email soft deleted successfully"}
