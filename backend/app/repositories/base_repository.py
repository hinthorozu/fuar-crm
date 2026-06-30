"""Generic repository helpers for SQLAlchemy models."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Reusable CRUD helpers for a single SQLAlchemy model."""

    def __init__(self, db: Session, model: type[ModelType]) -> None:
        self.db = db
        self.model = model

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(self) -> list[ModelType]:
        return self.db.query(self.model).all()

    def create(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.db.delete(entity)
        self.db.commit()

    def exists(self, entity_id: int) -> bool:
        return (
            self.db.query(self.model.id).filter(self.model.id == entity_id).first()
            is not None
        )
