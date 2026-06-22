import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.tables import Customer, Order, Refund


BASE_URL = "http://127.0.0.1:8000"


def upsert_records(db: Session, model, records: list[dict]):
    if not records:
        return 0

    stmt = insert(model).values(records)

    update_columns = {
        column.name: getattr(stmt.excluded, column.name)
        for column in model.__table__.columns
        if column.name != "id"
    }

    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_=update_columns,
    )

    db.execute(stmt)
    db.commit()

    return len(records)


def ingest_endpoint(
    db: Session,
    endpoint: str,
    model,
    page_size: int = 5000,
):
    page = 1
    total_ingested = 0

    with httpx.Client(timeout=60.0) as client:
        while True:
            response = client.get(
                f"{BASE_URL}/mock/{endpoint}",
                params={
                    "page": page,
                    "page_size": page_size,
                },
            )
            response.raise_for_status()

            payload = response.json()
            records = payload["data"]

            if not records:
                break

            inserted = upsert_records(db, model, records)
            total_ingested += inserted

            print(f"Ingested {endpoint}: page={page}, records={inserted}")

            if page >= payload["total_pages"]:
                break

            page += 1

    return total_ingested


def ingest_all(db: Session, page_size: int = 5000):
    customers = ingest_endpoint(
        db=db,
        endpoint="customers",
        model=Customer,
        page_size=page_size,
    )

    orders = ingest_endpoint(
        db=db,
        endpoint="orders",
        model=Order,
        page_size=page_size,
    )

    refunds = ingest_endpoint(
        db=db,
        endpoint="refunds",
        model=Refund,
        page_size=page_size,
    )

    return {
        "customers": customers,
        "orders": orders,
        "refunds": refunds,
    }