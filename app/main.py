from fastapi import FastAPI

from app.core.config import settings
from app.db.database import Base, engine
from app.models import tables
from app.api import admin, mock_api, analytics

app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(admin.router)
app.include_router(mock_api.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "message": "Analytics Backend Service is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }