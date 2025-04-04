from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Wallet, Event, EventImage, EventDetail, Reservation
from ..schemas import EventResponse, EventImageResponse, ReservationResponse
from ..auth.auth_handler import get_current_user

router = APIRouter()


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, Event.status == True).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/images", response_model=list[EventImageResponse])
def get_event_images(event_id: int, db: Session = Depends(get_db)):
    return db.query(EventImage).filter(EventImage.event_id == event_id).all()


@router.get("/{event_id}/details")
def get_grouped_event_details(event_id: int, db: Session = Depends(get_db)):

    details = db.query(EventDetail).filter(EventDetail.event_id == event_id).all()

    grouped_details = {
        "services": [],
        "required_equipment": [],
        "terms_and_conditions": []
    }

    for detail in details:
        if detail.type == 1:
            grouped_details["services"].append(detail)
        elif detail.type == 2:
            grouped_details["required_equipment"].append(detail)
        elif detail.type == 3:
            grouped_details["terms_and_conditions"].append(detail)

    return grouped_details


@router.post("/{event_id}/reserve", response_model=ReservationResponse)
def reserve_or_watchlist(
        event_id: int,
        num_of_adults: int,
        num_of_children: int,
        num_of_beds: int,
        is_paid: bool,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    event = db.query(Event).filter(Event.id == event_id, Event.status == True).first()
    if not event:
        raise HTTPException(status_code=404, detail="تور یافت نشد")

    total_price = (num_of_adults * event.price_per_adult) + (num_of_children * event.price_per_child)

    if is_paid:
        wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
        if not wallet or wallet.balance < total_price:
            raise HTTPException(status_code=400, detail="موجودی کیف پول کافی نیست")
        wallet.balance -= total_price

    new_reservation = Reservation(
        user_id=current_user.id,
        event_id=event_id,
        num_of_adults=num_of_adults,
        num_of_children=num_of_children,
        num_of_beds=num_of_beds,
        total_price=total_price,
        status=is_paid
    )

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    return new_reservation
