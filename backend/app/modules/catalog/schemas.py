from pydantic import BaseModel


class CatalogItemResponse(BaseModel):
    id: int
    title: str
    summary: str
    estimated_budget: int
    duration_hours: float
    tags: list[str]
