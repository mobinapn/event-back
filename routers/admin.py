from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Event, Category, User
from ..schemas import EventCreate, EventResponse, CategoryCreate, CategoryResponse
from ..auth.auth_handler import get_current_user

router = APIRouter()


@router.get("/admin/events", response_model=List[EventResponse])
def get_all_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return db.query(Event).all()


@router.post("/admin/events", response_model=EventResponse)
def create_event(event_data: EventCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    category = db.query(Category).filter(Category.id == event_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_event = Event(**event_data.dict())

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@router.put("/admin/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_data: EventCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for key, value in event_data.dict().items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)

    return event


@router.delete("/admin/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()

    return {"message": "Event deleted successfully"}


@router.get("/admin/categories", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return db.query(Category).all()


@router.post("/admin/categories", response_model=CategoryResponse)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    new_category = Category(**category_data.dict())

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.put("/admin/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category_data.dict().items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete("/admin/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}
