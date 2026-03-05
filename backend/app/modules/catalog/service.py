from sqlalchemy.orm import Session

from db.models.catalog_item import CatalogItem


DEFAULT_CATALOG = [
    {
        "title": "City Heritage Walk",
        "summary": "Guided walk through historic districts and local food spots.",
        "estimated_budget": 55,
        "duration_hours": 4.0,
        "tags_csv": "culture,walking,food",
    },
    {
        "title": "Beach & Sunset Day",
        "summary": "Relaxing beach day with optional water activities and sunset dinner.",
        "estimated_budget": 90,
        "duration_hours": 6.5,
        "tags_csv": "beach,relax,food",
    },
    {
        "title": "Mountain Adventure Trail",
        "summary": "Moderate hike with panoramic viewpoints and picnic stop.",
        "estimated_budget": 70,
        "duration_hours": 7.0,
        "tags_csv": "nature,hike,adventure",
    },
    {
        "title": "Museum + Cafe Circuit",
        "summary": "Two museums and local cafe hopping in the downtown core.",
        "estimated_budget": 45,
        "duration_hours": 5.0,
        "tags_csv": "culture,indoor,food",
    },
    {
        "title": "Local Markets & Street Food",
        "summary": "Explore local markets and top-rated street food corners.",
        "estimated_budget": 35,
        "duration_hours": 4.5,
        "tags_csv": "food,shopping,culture",
    },
]


def seed_catalog_if_empty(db: Session):
    exists = db.query(CatalogItem).first()
    if exists:
        return
    for item in DEFAULT_CATALOG:
        db.add(CatalogItem(**item))
    db.commit()


def list_catalog_items(db: Session):
    items = db.query(CatalogItem).order_by(CatalogItem.id.asc()).all()
    return [
        {
            "id": item.id,
            "title": item.title,
            "summary": item.summary,
            "estimated_budget": item.estimated_budget,
            "duration_hours": float(item.duration_hours),
            "tags": [tag.strip() for tag in (item.tags_csv or "").split(",") if tag.strip()],
        }
        for item in items
    ]
