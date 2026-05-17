from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.ml.model_loader import load_models

# Import models so SQLAlchemy registers tables before create_all.
from app.models import (  # noqa: F401
    AdminProfile,
    AuditLog,
    ChatSession,
    ChatSessionMessage,
    Complaint,
    ComplaintMessage,
    Evidence,
    GuardianProfile,
    Notification,
    Resource,
    ResourceCategory,
    User,
)


settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # React dev server
        "http://localhost:5173",       # Vite dev server
        "http://localhost:5174",       # Vite alt port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    try:
        load_models()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("ML models not loaded: %s — chatbot will use stubs.", exc)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "TrustLine backend is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_prefix)
