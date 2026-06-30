"""Customer phone management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Contact, Customer, CustomerPhone
from app.schemas.customer_phone import CustomerPhoneCreate, CustomerPhoneOut, CustomerPhoneUpdate
from app.utils.normalization import normalize_phone

router = APIRouter(prefix="/customer-phones", tags=["Customer Phones"])


def ensure_customer_exists(customer_id: int, db: Session):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")


def ensure_contact_exists(contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.is_deleted == False).first()  # noqa: E712
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")


def apply_phone_normalization(data: dict) -> dict:
    if data.get("phone_number") and not data.get("normalized_phone"):
        data["normalized_phone"] = normalize_phone(data["phone_number"])
    return data


@router.post("/", response_model=CustomerPhoneOut, status_code=201)
def create_customer_phone(phone: CustomerPhoneCreate, db: Session = Depends(get_db)):
    ensure_customer_exists(phone.customer_id, db)
    if phone.contact_id is not None:
        ensure_contact_exists(phone.contact_id, db)
    new_phone = CustomerPhone(**apply_phone_normalization(phone.model_dump()))
    db.add(new_phone)
    db.commit()
    db.refresh(new_phone)
    return new_phone


@router.get("/", response_model=List[CustomerPhoneOut])
def list_customer_phones(customer_id: Optional[int] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(CustomerPhone)
    if not include_deleted:
        query = query.filter(CustomerPhone.is_deleted == False)  # noqa: E712
    if customer_id:
        query = query.filter(CustomerPhone.customer_id == customer_id)
    return query.order_by(CustomerPhone.id.desc()).all()


@router.get("/{phone_id}", response_model=CustomerPhoneOut)
def get_customer_phone(phone_id: int, db: Session = Depends(get_db)):
    phone = db.query(CustomerPhone).filter(CustomerPhone.id == phone_id, CustomerPhone.is_deleted == False).first()  # noqa: E712
    if not phone:
        raise HTTPException(status_code=404, detail="Customer phone not found")
    return phone


@router.put("/{phone_id}", response_model=CustomerPhoneOut)
def update_customer_phone(phone_id: int, phone_update: CustomerPhoneUpdate, db: Session = Depends(get_db)):
    phone = db.query(CustomerPhone).filter(CustomerPhone.id == phone_id, CustomerPhone.is_deleted == False).first()  # noqa: E712
    if not phone:
        raise HTTPException(status_code=404, detail="Customer phone not found")

    update_data = apply_phone_normalization(phone_update.model_dump(exclude_unset=True))
    if "customer_id" in update_data:
        ensure_customer_exists(update_data["customer_id"], db)
    if update_data.get("contact_id") is not None:
        ensure_contact_exists(update_data["contact_id"], db)

    for field, value in update_data.items():
        setattr(phone, field, value)

    db.commit()
    db.refresh(phone)
    return phone


@router.delete("/{phone_id}")
def delete_customer_phone(phone_id: int, db: Session = Depends(get_db)):
    phone = db.query(CustomerPhone).filter(CustomerPhone.id == phone_id, CustomerPhone.is_deleted == False).first()  # noqa: E712
    if not phone:
        raise HTTPException(status_code=404, detail="Customer phone not found")

    phone.is_deleted = True
    phone.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Customer phone soft deleted successfully"}
