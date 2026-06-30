"""Fair participation management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Customer, Fair, FairParticipation
from app.schemas.fair_participation import FairParticipationCreate, FairParticipationOut, FairParticipationUpdate

router = APIRouter(prefix="/fair-participations", tags=["Fair Participations"])


def ensure_customer_exists(customer_id: int, db: Session):
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_deleted == False).first()  # noqa: E712
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")


def ensure_fair_exists(fair_id: int, db: Session):
    fair = db.query(Fair).filter(Fair.id == fair_id, Fair.is_deleted == False).first()  # noqa: E712
    if not fair:
        raise HTTPException(status_code=404, detail="Fair not found")


def commit_or_duplicate_error(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This customer is already linked to this fair")


@router.post("/", response_model=FairParticipationOut, status_code=201)
def create_fair_participation(participation: FairParticipationCreate, db: Session = Depends(get_db)):
    ensure_customer_exists(participation.customer_id, db)
    ensure_fair_exists(participation.fair_id, db)
    new_participation = FairParticipation(**participation.model_dump())
    db.add(new_participation)
    commit_or_duplicate_error(db)
    db.refresh(new_participation)
    return new_participation


@router.get("/", response_model=List[FairParticipationOut])
def list_fair_participations(customer_id: Optional[int] = None, fair_id: Optional[int] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(FairParticipation)
    if not include_deleted:
        query = query.filter(FairParticipation.is_deleted == False)  # noqa: E712
    if customer_id:
        query = query.filter(FairParticipation.customer_id == customer_id)
    if fair_id:
        query = query.filter(FairParticipation.fair_id == fair_id)
    return query.order_by(FairParticipation.created_at.desc()).all()


@router.get("/{participation_id}", response_model=FairParticipationOut)
def get_fair_participation(participation_id: int, db: Session = Depends(get_db)):
    participation = db.query(FairParticipation).filter(FairParticipation.id == participation_id, FairParticipation.is_deleted == False).first()  # noqa: E712
    if not participation:
        raise HTTPException(status_code=404, detail="Fair participation not found")
    return participation


@router.put("/{participation_id}", response_model=FairParticipationOut)
def update_fair_participation(participation_id: int, participation_update: FairParticipationUpdate, db: Session = Depends(get_db)):
    participation = db.query(FairParticipation).filter(FairParticipation.id == participation_id, FairParticipation.is_deleted == False).first()  # noqa: E712
    if not participation:
        raise HTTPException(status_code=404, detail="Fair participation not found")

    update_data = participation_update.model_dump(exclude_unset=True)
    if "customer_id" in update_data:
        ensure_customer_exists(update_data["customer_id"], db)
    if "fair_id" in update_data:
        ensure_fair_exists(update_data["fair_id"], db)

    for field, value in update_data.items():
        setattr(participation, field, value)

    commit_or_duplicate_error(db)
    db.refresh(participation)
    return participation


@router.delete("/{participation_id}")
def delete_fair_participation(participation_id: int, db: Session = Depends(get_db)):
    participation = db.query(FairParticipation).filter(FairParticipation.id == participation_id, FairParticipation.is_deleted == False).first()  # noqa: E712
    if not participation:
        raise HTTPException(status_code=404, detail="Fair participation not found")

    participation.is_deleted = True
    participation.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Fair participation soft deleted successfully"}
