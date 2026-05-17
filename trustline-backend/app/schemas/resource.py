from datetime import datetime

from pydantic import BaseModel


class ResourceCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None

    model_config = {"from_attributes": True}


class ResourceResponse(BaseModel):
    id: int
    category_id: int
    title: str
    slug: str
    summary: str | None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
