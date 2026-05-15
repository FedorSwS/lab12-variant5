from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date
from typing import Optional
from enum import Enum

class RoomTypeEnum(str, Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    PRESIDENTIAL = "presidential"

class RoomStatusEnum(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"

class BookingStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    passport_number: str = Field(..., min_length=5, max_length=50)
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: date

    class Config:
        from_attributes = True

class RoomBase(BaseModel):
    room_number: str = Field(..., pattern=r'^[0-9]{1,4}[A-Z]?$')
    room_type: RoomTypeEnum
    price_per_night: float = Field(..., ge=0)
    capacity: int = Field(..., ge=1, le=10)
    floor: int = Field(..., ge=0, le=50)
    has_view: bool = False
    has_wifi: bool = True
    has_ac: bool = True
    status: RoomStatusEnum = RoomStatusEnum.AVAILABLE
    description: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    customer_id: int
    room_id: int
    check_in_date: date
    check_out_date: date
    special_requests: Optional[str] = None

    @field_validator('check_out_date')
    def validate_dates(cls, v, info):
        if 'check_in_date' in info.data and v <= info.data['check_in_date']:
            raise ValueError('check_out_date must be after check_in_date')
        return v

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    total_price: float
    status: BookingStatusEnum
    created_at: date

    class Config:
        from_attributes = True

class BookingWithDetails(Booking):
    customer: Customer
    room: Room

class BookingUpdate(BaseModel):
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    status: Optional[BookingStatusEnum] = None
    special_requests: Optional[str] = None

    @field_validator('check_out_date')
    def validate_dates(cls, v, info):
        check_in = info.data.get('check_in_date')
        if check_in and v and v <= check_in:
            raise ValueError('check_out_date must be after check_in_date')
        return v

class RoomOccupancyReport(BaseModel):
    room_id: int
    room_number: str
    occupancy_rate: float
    total_revenue: float

class PopularRoomReport(BaseModel):
    room_type: RoomTypeEnum
    booking_count: int
    total_revenue: float
