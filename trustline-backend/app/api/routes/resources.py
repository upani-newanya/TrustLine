from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.resource import ResourceCategoryResponse, ResourceResponse
from app.services.resource_service import get_resource_by_slug, list_categories

router = APIRouter()


@router.get("/categories", response_model=list[ResourceCategoryResponse])
def categories(db: Session = Depends(get_db)):
    return list_categories(db)


@router.get("/{slug}", response_model=ResourceResponse)
def resource_detail(slug: str, db: Session = Depends(get_db)):
    return get_resource_by_slug(db, slug)
