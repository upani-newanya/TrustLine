from sqlalchemy.orm import Session

from app.models.user import User


def get_profile(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, role: str | None = None) -> list[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.created_at.desc()).all()
