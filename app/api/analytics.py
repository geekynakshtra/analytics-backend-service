from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tables import AnalyticsSummary, RevenueTrend, TopCustomer

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def decimal_to_float(value):
    if value is None:
        return 0
    return float(value)


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    summary = db.query(AnalyticsSummary).filter(AnalyticsSummary.id == 1).first()

    if not summary:
        return {
            "message": "Analytics not refreshed yet. Run POST /admin/refresh-analytics first."
        }

    return {
        "total_orders": summary.total_orders,
        "total_revenue": decimal_to_float(summary.total_revenue),
        "total_refunds": decimal_to_float(summary.total_refunds),
        "net_revenue": decimal_to_float(summary.net_revenue),
        "average_order_value": decimal_to_float(summary.average_order_value),
        "repeat_customer_revenue": decimal_to_float(summary.repeat_customer_revenue),
        "updated_at": summary.updated_at,
    }


@router.get("/revenue-trends")
def get_revenue_trends(
    limit: int = Query(365, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RevenueTrend)
        .order_by(RevenueTrend.date.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "date": row.date,
            "revenue": decimal_to_float(row.revenue),
            "refunds": decimal_to_float(row.refunds),
            "net_revenue": decimal_to_float(row.net_revenue),
        }
        for row in rows
    ]


@router.get("/top-customers")
def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(TopCustomer)
        .order_by(TopCustomer.total_spend.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "email": row.email,
            "total_spend": decimal_to_float(row.total_spend),
            "order_count": row.order_count,
        }
        for row in rows
    ]