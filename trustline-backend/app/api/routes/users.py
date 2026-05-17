from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.constants import RoleEnum
from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserProfileResponse
from app.services.user_service import list_users

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserProfileResponse])
def get_users(
    role: RoleEnum | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return list_users(db, role.value if role else None)
