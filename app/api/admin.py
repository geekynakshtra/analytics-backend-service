from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.generator import generate_all_data
from app.services.ingestion import ingest_all
from app.services.analytics_service import refresh_analytics

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/generate")
def generate_data(seed: int = 42, db: Session = Depends(get_db)):
    generate_all_data(db=db, seed=seed)

    return {
        "message": "Data generated successfully",
        "seed": seed,
        "customers": 100_000,
        "orders": 1_000_000,
        "refunds": 200_000,
    }


@router.post("/ingest")
def ingest_data(page_size: int = 5000, db: Session = Depends(get_db)):
    result = ingest_all(db=db, page_size=page_size)

    return {
        "message": "Ingestion completed successfully",
        "page_size": page_size,
        "ingested": result,
    }


@router.post("/refresh-analytics")
def refresh_analytics_data(db: Session = Depends(get_db)):
    result = refresh_analytics(db=db)

    return result