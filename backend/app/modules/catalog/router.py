from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.modules.catalog.schemas import CatalogItemResponse
from app.modules.catalog.service import list_catalog_items, seed_catalog_if_empty

router = APIRouter(prefix="/api/v1/catalog", tags=["Catalog"])


@router.get("", response_model=list[CatalogItemResponse])
def get_catalog(db: Session = Depends(get_db)):
    seed_catalog_if_empty(db)
    return [CatalogItemResponse(**item) for item in list_catalog_items(db)]
