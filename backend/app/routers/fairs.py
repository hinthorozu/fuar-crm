"""Fair management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Fair
from app.schemas.fair import FairCreate, FairOut, FairUpdate
from app.utils.normalization import normalize_text

router = APIRouter(prefix="/fairs", tags=["Fairs"])


def apply_fair_normalization(data: dict) -> dict:
    if data.get("fair_name") and not data.get("normalized_fair_name"):
        data["normalized_fair_name"] = normalize_text(data["fair_name"])
    return data


@router.post("/", response_model=FairOut, status_code=201)
def create_fair(fair: FairCreate, db: Session = Depends(get_db)):
    new_fair = Fair(**apply_fair_normalization(fair.model_dump()))
    db.add(new_fair)
    db.commit()
    db.refresh(new_fair)
    return new_fair


@router.get("/", response_model=List[FairOut])
def list_fairs(search: Optional[str] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(Fair)
    if not include_deleted:
        query = query.filter(Fair.is_deleted == False)  # noqa: E712
    if search:
        query = query.filter(
            or_(
                Fair.fair_name.ilike(f"%{search}%"),
                Fair.normalized_fair_name.ilike(f"%{search}%"),
                Fair.venue.ilike(f"%{search}%"),
                Fair.city.ilike(f"%{search}%"),
                Fair.country.ilike(f"%{search}%"),
            )
        )
    return query.order_by(Fair.start_date.desc()).all()


@router.get("/{fair_id}", response_model=FairOut)
def get_fair(fair_id: int, db: Session = Depends(get_db)):
    fair = db.query(Fair).filter(Fair.id == fair_id, Fair.is_deleted == False).first()  # noqa: E712
    if not fair:
        raise HTTPException(status_code=404, detail="Fair not found")
    return fair


@router.put("/{fair_id}", response_model=FairOut)
def update_fair(fair_id: int, fair_update: FairUpdate, db: Session = Depends(get_db)):
    fair = db.query(Fair).filter(Fair.id == fair_id, Fair.is_deleted == False).first()  # noqa: E712
    if not fair:
        raise HTTPException(status_code=404, detail="Fair not found")

    update_data = apply_fair_normalization(fair_update.model_dump(exclude_unset=True))
    for field, value in update_data.items():
        setattr(fair, field, value)

    db.commit()
    db.refresh(fair)
    return fair


@router.delete("/{fair_id}")
def delete_fair(fair_id: int, db: Session = Depends(get_db)):
    fair = db.query(Fair).filter(Fair.id == fair_id, Fair.is_deleted == False).first()  # noqa: E712
    if not fair:
        raise HTTPException(status_code=404, detail="Fair not found")

    fair.is_deleted = True
    fair.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Fair soft deleted successfully"}
