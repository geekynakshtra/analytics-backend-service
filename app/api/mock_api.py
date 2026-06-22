from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tables import Customer, Order, Refund

router = APIRouter(prefix="/mock", tags=["Mock APIs"])


def paginate_query(query, page: int, page_size: int):
    total = query.count()

    items = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "data": items,
    }


@router.get("/customers")
def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(Customer).order_by(Customer.id)
    return paginate_query(query, page, page_size)


@router.get("/orders")
def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(Order).order_by(Order.id)
    return paginate_query(query, page, page_size)


@router.get("/refunds")
def get_refunds(
    page: int = Query(1, ge=1),
    page_size: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(Refund).order_by(Refund.id)
    return paginate_query(query, page, page_size)