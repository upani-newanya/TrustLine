from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import RoleEnum
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.audit_service import log_action


def register_user(db: Session, payload: RegisterRequest) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        password_hash=get_password_hash(payload.password),
        role=RoleEnum.USER.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=user.email, extra={"role": user.role, "user_id": user.id})
    log_action(db, action="register", actor_user_id=user.id, entity_type="user", entity_id=str(user.id))
    return TokenResponse(access_token=access_token)


def login_user_by_credentials(db: Session, email: str, password: str) -> TokenResponse:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(subject=user.email, extra={"role": user.role, "user_id": user.id})
    log_action(db, action="login", actor_user_id=user.id, entity_type="user", entity_id=str(user.id))
    return TokenResponse(access_token=access_token)
