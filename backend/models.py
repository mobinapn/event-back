from sqlalchemy import Column, Integer, Float, String, Text, Date, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(10), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    firstname = Column(String(50), nullable=True)
    lastname = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    gender = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    national_code = Column(String(10), unique=True, index=True, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=func.now())

    wallet = relationship("Wallet", back_populates="user", uselist=False)
    passengers = relationship("Passenger", back_populates="user", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True , nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    gender = Column(Integer, nullable=False)
    dob = Column(Date, nullable=True)
    national_code = Column(String(10), index=True, nullable=False)

    user = relationship("User", back_populates="passengers")

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=0)
    credit_identifier = Column(String(32), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=func.now())

    user = relationship("User", back_populates="wallet")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String(100), nullable=False)
    image = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    price_per_adult = Column(Integer, nullable=False)
    price_per_child = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=func.now())

    category = relationship("Category", back_populates="events")
    images = relationship("EventImage", back_populates="event", cascade="all, delete-orphan")
    details = relationship("EventDetail", back_populates="event", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="event", cascade="all, delete-orphan")


class EventImage(Base):
    __tablename__ = "event_images"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    image_url = Column(String(255), nullable=False)

    event = relationship("Event", back_populates="images")

class EventDetail(Base):
    __tablename__ = "event_details"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    type = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    event = relationship("Event", back_populates="details")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, nullable=False)

    events = relationship("Event", back_populates="category", cascade="all, delete-orphan")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    num_of_adults = Column(Integer, nullable=False)
    num_of_children = Column(Integer, nullable=False)
    num_of_beds = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=func.now())

    user = relationship("User", back_populates="reservations")
    event = relationship("Event", back_populates="reservations")
