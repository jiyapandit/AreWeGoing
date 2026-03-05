from sqlalchemy import Column, Integer, String, Float

from db.base import Base


class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    summary = Column(String(600), nullable=False)
    estimated_budget = Column(Integer, nullable=False)
    duration_hours = Column(Float, nullable=False)
    tags_csv = Column(String(300), nullable=False, default="")
