from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.constants import RoleEnum
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_user_optional(token: str | None = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> User | None:
    """Return the current user if a valid token is provided, otherwise None (guest)."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return None
    return db.query(User).filter(User.email == payload["sub"]).first()


def require_role(user: User, allowed_roles: list[RoleEnum]) -> None:
    if user.role not in [role.value for role in allowed_roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    require_role(user, [RoleEnum.ADMIN])
    return user
