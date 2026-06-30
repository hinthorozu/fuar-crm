"""Dashboard API endpoints for the usable CRM layer."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Contact,
    Customer,
    CustomerEmail,
    CustomerPhone,
    Fair,
    FairParticipation,
    ImportBatch,
    ImportRow,
    Note,
)
from app.schemas.dashboard import DashboardCounts, DashboardSummary, RecentCustomer, RecentFair

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def count_active(db: Session, model):
    return db.query(model).filter(model.is_deleted == False).count()  # noqa: E712


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    counts = DashboardCounts(
        customers=count_active(db, Customer),
        contacts=count_active(db, Contact),
        phones=count_active(db, CustomerPhone),
        emails=count_active(db, CustomerEmail),
        fairs=count_active(db, Fair),
        fair_participations=count_active(db, FairParticipation),
        notes=count_active(db, Note),
        import_batches=db.query(ImportBatch).count(),
        import_rows_pending_decision=db.query(ImportRow)
        .filter(ImportRow.decision_status == "pending")
        .count(),
    )

    recent_customers = [
        RecentCustomer(
            id=item.id,
            company_name=item.company_name,
            country=item.country,
            city=item.city,
            source=item.source,
            created_at=item.created_at,
        )
        for item in db.query(Customer)
        .filter(Customer.is_deleted == False)  # noqa: E712
        .order_by(Customer.created_at.desc())
        .limit(5)
        .all()
    ]

    recent_fairs = [
        RecentFair(
            id=item.id,
            fair_name=item.fair_name,
            city=item.city,
            country=item.country,
            start_date=item.start_date,
            created_at=item.created_at,
        )
        for item in db.query(Fair)
        .filter(Fair.is_deleted == False)  # noqa: E712
        .order_by(Fair.created_at.desc())
        .limit(5)
        .all()
    ]

    return DashboardSummary(
        counts=counts,
        recent_customers=recent_customers,
        recent_fairs=recent_fairs,
    )
