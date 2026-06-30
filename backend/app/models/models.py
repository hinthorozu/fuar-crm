"""
SQLAlchemy ORM models.

Naming rule:
- Python classes/attributes: English
- Database tables/columns: English
- Frontend labels: Turkish, handled outside this backend structure
"""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
import json
from sqlalchemy.sql import func

from app.database import Base


class JSONEncodedText(TypeDecorator):
    """Stores JSON-compatible Python values as TEXT for MySQL/MariaDB compatibility."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="admin")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    normalized_company_name = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    normalized_website = Column(String(255), nullable=True)
    main_phone = Column(String(50), nullable=True)
    normalized_main_phone = Column(String(50), nullable=True)
    tax_number = Column(String(50), nullable=True)
    tax_office = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(30), nullable=False, default="manual")
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    phones = relationship("CustomerPhone", back_populates="customer", cascade="all, delete-orphan")
    emails = relationship("CustomerEmail", back_populates="customer", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="customer", cascade="all, delete-orphan")
    fair_participations = relationship("FairParticipation", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_customers_company_name", "company_name", mysql_length=191),
        Index("idx_customers_normalized_company_name", "normalized_company_name", mysql_length=191),
        Index("idx_customers_website", "website", mysql_length=191),
        Index("idx_customers_normalized_website", "normalized_website", mysql_length=191),
        Index("idx_customers_main_phone", "main_phone"),
        Index("idx_customers_normalized_main_phone", "normalized_main_phone"),
        Index("idx_customers_tax_number", "tax_number"),
    )


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(150), nullable=False)
    normalized_full_name = Column(String(150), nullable=True)
    title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    note = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="contacts")

    __table_args__ = (
        Index("idx_contacts_customer_id", "customer_id"),
        Index("idx_contacts_full_name", "full_name"),
        Index("idx_contacts_normalized_full_name", "normalized_full_name"),
    )


class CustomerPhone(Base):
    __tablename__ = "customer_phones"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    phone_number = Column(String(50), nullable=False)
    normalized_phone = Column(String(50), nullable=True)
    phone_type = Column(String(50), nullable=True)
    label = Column(String(50), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    source = Column(String(30), nullable=False, default="manual")
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="phones")
    contact = relationship("Contact")

    __table_args__ = (
        Index("idx_customer_phones_customer_id", "customer_id"),
        Index("idx_customer_phones_contact_id", "contact_id"),
        Index("idx_customer_phones_normalized_phone", "normalized_phone"),
    )


class CustomerEmail(Base):
    __tablename__ = "customer_emails"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    email = Column(String(150), nullable=False)
    normalized_email = Column(String(150), nullable=True)
    email_type = Column(String(50), nullable=True)
    label = Column(String(50), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    validation_status = Column(String(30), nullable=False, default="unknown")
    validation_message = Column(String(255), nullable=True)
    source = Column(String(30), nullable=False, default="manual")
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="emails")
    contact = relationship("Contact")

    __table_args__ = (
        Index("idx_customer_emails_customer_id", "customer_id"),
        Index("idx_customer_emails_contact_id", "contact_id"),
        Index("idx_customer_emails_normalized_email", "normalized_email"),
        Index("idx_customer_emails_validation_status", "validation_status"),
    )


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    fair_id = Column(Integer, ForeignKey("fairs.id", ondelete="SET NULL"), nullable=True)
    fair_participation_id = Column(Integer, ForeignKey("fair_participations.id", ondelete="SET NULL"), nullable=True)
    note_date = Column(DateTime, server_default=func.now(), nullable=False)
    detail = Column(Text, nullable=False)
    note_type = Column(String(50), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="notes")
    contact = relationship("Contact")
    fair = relationship("Fair")
    fair_participation = relationship("FairParticipation")
    created_by_user = relationship("User")


class Fair(Base):
    __tablename__ = "fairs"

    id = Column(Integer, primary_key=True, index=True)
    fair_name = Column(String(255), nullable=False)
    normalized_fair_name = Column(String(255), nullable=True)
    organizer = Column(String(255), nullable=True)
    venue = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    participants = relationship("FairParticipation", back_populates="fair", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_fairs_fair_name", "fair_name", mysql_length=191),
        Index("idx_fairs_normalized_fair_name", "normalized_fair_name", mysql_length=191),
        Index("idx_fairs_dates", "start_date", "end_date"),
    )


class FairParticipation(Base):
    __tablename__ = "fair_participations"
    __table_args__ = (
        UniqueConstraint("customer_id", "fair_id", name="unique_customer_fair"),
        Index("idx_participations_customer_id", "customer_id"),
        Index("idx_participations_fair_id", "fair_id"),
        Index("idx_participations_external_id", "external_exhibitor_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    fair_id = Column(Integer, ForeignKey("fairs.id", ondelete="CASCADE"), nullable=False)
    hall = Column(String(100), nullable=True)
    stand_number = Column(String(100), nullable=True)
    exhibitor_profile_url = Column(String(500), nullable=True)
    external_exhibitor_id = Column(String(100), nullable=True)
    participation_status = Column(String(50), nullable=False, default="active")
    source = Column(String(30), nullable=False, default="manual")
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="fair_participations")
    fair = relationship("Fair", back_populates="participants")


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    fair_id = Column(Integer, ForeignKey("fairs.id", ondelete="SET NULL"), nullable=True)
    source_type = Column(String(50), nullable=False)  # excel, scraper
    source_name = Column(String(255), nullable=True)
    original_file_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="uploaded")
    total_rows = Column(Integer, nullable=False, default=0)
    successful_rows = Column(Integer, nullable=False, default=0)
    warning_rows = Column(Integer, nullable=False, default=0)
    error_rows = Column(Integer, nullable=False, default=0)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    fair = relationship("Fair")
    created_by_user = relationship("User")
    rows = relationship("ImportRow", back_populates="import_batch", cascade="all, delete-orphan")


class ImportRow(Base):
    __tablename__ = "import_rows"

    id = Column(Integer, primary_key=True, index=True)
    import_batch_id = Column(Integer, ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False)
    row_number = Column(Integer, nullable=False)
    raw_data_json = Column(JSONEncodedText, nullable=True)
    normalized_data_json = Column(JSONEncodedText, nullable=True)
    detected_customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    detected_fair_participation_id = Column(Integer, ForeignKey("fair_participations.id", ondelete="SET NULL"), nullable=True)
    match_score = Column(DECIMAL(5, 2), nullable=True)
    detection_status = Column(String(50), nullable=False, default="new")
    decision_status = Column(String(50), nullable=False, default="pending")
    decision_payload_json = Column(JSONEncodedText, nullable=True)
    warning_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    import_batch = relationship("ImportBatch", back_populates="rows")
    detected_customer = relationship("Customer")
    detected_fair_participation = relationship("FairParticipation")


class ScraperSource(Base):
    __tablename__ = "scraper_sources"

    id = Column(Integer, primary_key=True, index=True)
    fair_id = Column(Integer, ForeignKey("fairs.id", ondelete="SET NULL"), nullable=True)
    source_name = Column(String(255), nullable=False)
    base_url = Column(String(500), nullable=False)
    adapter_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    fair = relationship("Fair")


class ScraperRun(Base):
    __tablename__ = "scraper_runs"

    id = Column(Integer, primary_key=True, index=True)
    scraper_source_id = Column(Integer, ForeignKey("scraper_sources.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="running")
    total_found = Column(Integer, nullable=False, default=0)
    output_file_name = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, server_default=func.now(), nullable=False)
    finished_at = Column(DateTime, nullable=True)

    scraper_source = relationship("ScraperSource")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_data_json = Column(JSONEncodedText, nullable=True)
    new_data_json = Column(JSONEncodedText, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User")
