from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Event, Category
from ..schemas import EventResponse, CategoryResponse

router = APIRouter()


@router.get("/slider", response_model=list[EventResponse])
def get_upcoming_events(db: Session = Depends(get_db)):
    return db.query(Event).filter(Event.status == True).order_by(Event.start_date).limit(5).all()


@router.get("/events")
def get_all_events(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    total_count = db.query(Event).filter(Event.status == True).count()
    events = db.query(Event).filter(Event.status == True).offset((page - 1) * per_page).limit(per_page).all()
    return {"events": events, "total_count": total_count}


@router.get("/search")
def search_events(destination: str = None, start_date: str = None, capacity: int = None, page: int = 1,
                  per_page: int = 10, db: Session = Depends(get_db)):
    query = db.query(Event).filter(Event.status == True)

    if destination:
        query = query.filter(Event.destination.ilike(f"%{destination}%"))
    if start_date:
        query = query.filter(Event.start_date >= start_date)
    if capacity:
        query = query.filter(Event.capacity >= capacity)

    total_count = query.count()
    events = query.offset((page - 1) * per_page).limit(per_page).all()

    return {"events": events, "total_count": total_count}


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.get("/category/{category_id}")
def get_events_by_category(category_id: int, page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    query = db.query(Event).filter(Event.status == True, Event.category_id == category_id)

    total_count = query.count()
    events = query.offset((page - 1) * per_page).limit(per_page).all()

    return {"events": events, "total_count": total_count}
