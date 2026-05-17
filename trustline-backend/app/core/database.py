from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    pass


_connect_args = {}
if settings.database_url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

# Enable foreign keys for SQLite
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
