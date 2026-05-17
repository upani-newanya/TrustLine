from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resource import Resource, ResourceCategory


def list_categories(db: Session) -> list[ResourceCategory]:
    return db.query(ResourceCategory).order_by(ResourceCategory.name.asc()).all()


def get_resource_by_slug(db: Session, slug: str) -> Resource:
    resource = db.query(Resource).filter(Resource.slug == slug).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource
