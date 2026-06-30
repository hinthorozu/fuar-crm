"""Note management API endpoints."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Contact, Customer, Fair, FairParticipation, Note, User
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["Notes"])


def ensure_exists(model, item_id: int, label: str, db: Session):
    item = db.query(model).filter(model.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"{label} not found")


@router.post("/", response_model=NoteOut, status_code=201)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    ensure_exists(Customer, note.customer_id, "Customer", db)
    if note.contact_id is not None:
        ensure_exists(Contact, note.contact_id, "Contact", db)
    if note.fair_id is not None:
        ensure_exists(Fair, note.fair_id, "Fair", db)
    if note.fair_participation_id is not None:
        ensure_exists(FairParticipation, note.fair_participation_id, "Fair participation", db)
    if note.created_by_user_id is not None:
        ensure_exists(User, note.created_by_user_id, "User", db)
    new_note = Note(**note.model_dump())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/", response_model=List[NoteOut])
def list_notes(customer_id: Optional[int] = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    query = db.query(Note)
    if not include_deleted:
        query = query.filter(Note.is_deleted == False)  # noqa: E712
    if customer_id:
        query = query.filter(Note.customer_id == customer_id)
    return query.order_by(Note.note_date.desc()).all()


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.is_deleted == False).first()  # noqa: E712
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.is_deleted == False).first()  # noqa: E712
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    update_data = note_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.is_deleted == False).first()  # noqa: E712
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.is_deleted = True
    note.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Note soft deleted successfully"}
