"""User-specific database access."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.models import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user persistence operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def _with_relations(self):
        return self.db.query(User).options(
            joinedload(User.role_ref),
            joinedload(User.organization),
        )

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    def find_by_email(self, email: str) -> User | None:
        normalized_email = self.normalize_email(email)
        return self._with_relations().filter(User.email == normalized_email).first()

    def find_by_id(self, user_id: int) -> User | None:
        return self._with_relations().filter(User.id == user_id).first()

    def update_last_login(self, user: User) -> User:
        user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.update(user)
