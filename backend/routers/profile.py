from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from ..database import get_db
from ..models import User, Reservation, Wallet, Passenger, Event
from ..schemas import UserProfileResponse, ReservationResponse, WalletResponse, PassengerResponse
from ..auth.auth_handler import get_current_user

def parse_flexible_date(date_string):
    """
    Parse date string in various formats and return a datetime.date object
    """
    if not date_string:
        return None
        
    # Try standard formats
    formats = [
        "%Y-%m-%d",       # 2023-04-21
        "%d-%m-%Y",       # 21-04-2023
        "%d/%m/%Y",       # 21/04/2023
        "%m/%d/%Y",       # 04/21/2023
        "%d.%m.%Y",       # 21.04.2023
        "%B %d, %Y",      # April 21, 2023
        "%d %B %Y",       # 21 April 2023
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
            
    # Try to extract numbers using regex
    import re
    if re.match(r"^\d{1,2}[/-\.]\d{1,2}[/-\.]\d{2,4}$", date_string):
        parts = re.split(r"[/-\.]", date_string)
        # Try different arrangements of the parts
        try:
            if len(parts[2]) == 2:  # Handle two-digit years
                parts[2] = "20" + parts[2] if int(parts[2]) < 50 else "19" + parts[2]
            return datetime(int(parts[2]), int(parts[1]), int(parts[0])).date()
        except ValueError:
            try:
                return datetime(int(parts[2]), int(parts[0]), int(parts[1])).date()
            except ValueError:
                pass
                
    raise ValueError(f"Could not parse date: {date_string}")

router = APIRouter()


@router.get("", response_model=UserProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return current_user


@router.put("")
def update_profile(update_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed_fields = ["firstname", "lastname", "email", "gender", "dob", "national_code"]

    for key, value in update_data.items():
        if key in allowed_fields:
            setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}


@router.get("/reservations/unpaid", response_model=list[ReservationResponse])
def get_unpaid_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Reservation).filter(Reservation.user_id == current_user.id, Reservation.status == False).all()


@router.get("/reservations/upcoming", response_model=list[ReservationResponse])
def get_upcoming_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_time = datetime.now(timezone.utc).date()
    return db.query(Reservation).join(Event).filter(
        Reservation.user_id == current_user.id,
        Reservation.status == True,
        Event.start_date > current_time
    ).all()


@router.get("/reservations/past", response_model=list[ReservationResponse])
def get_past_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_time = datetime.now(timezone.utc).date()
    return db.query(Reservation).join(Event).filter(
        Reservation.user_id == current_user.id,
        Reservation.status == True,
        Event.start_date <= current_time
    ).all()


@router.post("/reservations/cancel/{reservation_id}")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id,
                                               Reservation.user_id == current_user.id).first()

    if not reservation or not reservation.status:
        raise HTTPException(status_code=400, detail="Reservation not found or already cancelled")

    event = db.query(Event).filter(Event.id == reservation.event_id).first()
    current_time = datetime.now(timezone.utc).date()

    if event.start_date > current_time + timedelta(days=1):
        refund_amount = reservation.total_price
    elif event.start_date > current_time:
        refund_amount = int(reservation.total_price * 0.6)
    else:
        raise HTTPException(status_code=400, detail="This reservation can no longer be canceled")

    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if wallet:
        wallet.balance += refund_amount

    reservation.status = False
    db.commit()

    return {"message": "Reservation canceled", "refund_amount": refund_amount}


@router.get("/wallet", response_model=WalletResponse)
def get_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.post("/wallet/deposit")
def deposit_wallet(amount: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount is not valid")

    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if wallet:
        wallet.balance += amount
        db.commit()
        return {"message": "Inventory increased successfully", "new_balance": wallet.balance}

    raise HTTPException(status_code=404, detail="کیف پول یافت نشد")


@router.post("/wallet/withdraw")
def withdraw_wallet(amount: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount is not valid")

    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if wallet:
        wallet.balance -= amount
        db.commit()
        return {"message": "Inventory decreased successfully", "new_balance": wallet.balance}

    raise HTTPException(status_code=404, detail="کیف پول یافت نشد")


@router.post("/wallet/transfer")
def transfer_money(destination_wallet_id: str, amount: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    sender_wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    receiver_wallet = db.query(Wallet).filter(Wallet.credit_identifier == destination_wallet_id).first()

    if not sender_wallet or not receiver_wallet:
        raise HTTPException(status_code=404, detail="Destination wallet not found")

    if sender_wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Not enough inventory")

    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    db.commit()

    return {"message": "The transfer was successful"}


@router.get("/passengers", response_model=list[PassengerResponse])
def get_passengers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Passenger).filter(Passenger.user_id == current_user.id).all()


@router.post("/passengers", response_model=PassengerResponse)
def add_passenger(
        passenger_data: PassengerResponse,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        # If passenger_data.dob is a string, parse it; if it's already a date, use it as is
        dob = passenger_data.dob
        if isinstance(dob, str):
            dob = parse_flexible_date(dob)
            
        new_passenger = Passenger(
            user_id=current_user.id,
            firstname=passenger_data.firstname,
            lastname=passenger_data.lastname,
            gender=passenger_data.gender,
            dob=dob,  # Use the parsed date
            national_code=passenger_data.national_code
        )

        db.add(new_passenger)
        db.commit()
        db.refresh(new_passenger)
        return new_passenger
        
    except ValueError as e:
        # Handle invalid date error
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@router.delete("/passengers/{passenger_id}")
def delete_passenger(passenger_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    passenger = db.query(Passenger).filter(
        Passenger.id == passenger_id,
        Passenger.user_id == current_user.id
    ).first()

    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found or does not belong to this user")

    db.delete(passenger)
    db.commit()

    return {"message": "Passenger successfully deleted"}
