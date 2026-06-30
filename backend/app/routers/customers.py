"""Customer management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Customer
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdate
from app.schemas.customer_profile import CustomerProfileOut
from app.utils.normalization import normalize_company_name, normalize_phone, normalize_website

router = APIRouter(prefix="/customers", tags=["Customers"])


def apply_customer_normalization(data: dict) -> dict:
    if data.get("company_name") and not data.get("normalized_company_name"):
        data["normalized_company_name"] = normalize_company_name(data["company_name"])
    if data.get("website") and not data.get("normalized_website"):
        data["normalized_website"] = normalize_website(data["website"])
    if data.get("main_phone") and not data.get("normalized_main_phone"):
        data["normalized_main_phone"] = normalize_phone(data["main_phone"])
    return data


@router.post("/", response_model=CustomerOut, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    data = apply_customer_normalization(customer.model_dump())
    new_customer = Customer(**data)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/", response_model=List[CustomerOut])
def list_customers(search: Optional[str] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(Customer)
    if not include_deleted:
        query = query.filter(Customer.is_deleted == False)  # noqa: E712
    if search:
        query = query.filter(
            or_(
                Customer.company_name.ilike(f"%{search}%"),
                Customer.normalized_company_name.ilike(f"%{search}%"),
                Customer.country.ilike(f"%{search}%"),
                Customer.city.ilike(f"%{search}%"),
                Customer.address.ilike(f"%{search}%"),
                Customer.website.ilike(f"%{search}%"),
                Customer.main_phone.ilike(f"%{search}%"),
            )
        )
    return query.order_by(Customer.company_name.asc()).all()


@router.get("/{customer_id}/profile", response_model=CustomerProfileOut)
def get_customer_profile(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer": customer,
        "contacts": [item for item in customer.contacts if not item.is_deleted],
        "phones": [item for item in customer.phones if not item.is_deleted],
        "emails": [item for item in customer.emails if not item.is_deleted],
        "fair_participations": [item for item in customer.fair_participations if not item.is_deleted],
        "notes": [item for item in customer.notes if not item.is_deleted],
    }


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = apply_customer_normalization(customer_update.model_dump(exclude_unset=True))
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.is_deleted = True
    customer.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Customer soft deleted successfully"}
