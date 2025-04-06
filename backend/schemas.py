from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union
from datetime import date


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    password: str

class EventResponse(BaseModel):
    id: int
    title: str
    category_id: int
    image: str
    source: str
    destination: str
    start_date: datetime
    end_date: datetime
    price_per_adult: int
    price_per_child: int
    capacity: int
    status: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: int
    username: str
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    gender: int | None = None
    dob: datetime | None = None
    national_code: str | None = None
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: int
    credit_identifier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PassengerResponse(BaseModel):
    id: int
    user_id: int
    firstname: str
    lastname: str
    gender: int
    dob: Union[str, date]
    national_code: str

    class Config:
        from_attributes = True

class EventImageResponse(BaseModel):
    id: int
    event_id: int
    image_url: str

    class Config:
        from_attributes = True

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    num_of_adults: int
    num_of_children: int
    num_of_beds: int
    total_price: int
    status: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    category_id: int
    title: str
    image: str
    source: str
    destination: str
    start_date: datetime
    end_date: datetime
    price_per_adult: int
    price_per_child: int
    capacity: int
    status: bool

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    title: str

    class Config:
        from_attributes = True
