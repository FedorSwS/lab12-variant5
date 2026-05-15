from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import date
import enum
from app.database import Base

class RoomType(str, enum.Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PRESIDENTIAL = "presidential"

class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    passport_number = Column(String(50), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(Date, default=date.today)

    bookings = relationship("Booking", back_populates="customer")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(10), unique=True, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False)
    price_per_night = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    has_view = Column(Boolean, default=False)
    has_wifi = Column(Boolean, default=True)
    has_ac = Column(Boolean, default=True)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE)
    description = Column(Text, nullable=True)

    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(Date, default=date.today)
    special_requests = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
