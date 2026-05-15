from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import date, timedelta
from typing import List, Optional

from app import models, schemas

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: int, customer_update: schemas.CustomerCreate):
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    for key, value in customer_update.model_dump().items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False
    db.delete(db_customer)
    db.commit()
    return True

def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

def get_room_by_number(db: Session, room_number: str):
    return db.query(models.Room).filter(models.Room.room_number == room_number).first()

def get_rooms(db: Session, skip: int = 0, limit: int = 100, room_type: Optional[str] = None):
    query = db.query(models.Room)
    if room_type:
        query = query.filter(models.Room.room_type == room_type)
    return query.offset(skip).limit(limit).all()

def get_available_rooms(db: Session, check_in: date, check_out: date):
    booked_rooms = db.query(models.Booking.room_id).filter(
        and_(
            models.Booking.status.in_([models.BookingStatus.CONFIRMED, models.BookingStatus.CHECKED_IN]),
            models.Booking.check_in_date < check_out,
            models.Booking.check_out_date > check_in
        )
    ).subquery()
    
    return db.query(models.Room).filter(
        and_(
            models.Room.status == models.RoomStatus.AVAILABLE,
            models.Room.id.notin_(booked_rooms)
        )
    ).all()

def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def update_room(db: Session, room_id: int, room_update: schemas.RoomCreate):
    db_room = get_room(db, room_id)
    if not db_room:
        return None
    for key, value in room_update.model_dump().items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room

def delete_room(db: Session, room_id: int):
    db_room = get_room(db, room_id)
    if not db_room:
        return False
    db.delete(db_room)
    db.commit()
    return True

def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

def get_bookings(db: Session, skip: int = 0, limit: int = 100, customer_id: Optional[int] = None):
    query = db.query(models.Booking)
    if customer_id:
        query = query.filter(models.Booking.customer_id == customer_id)
    return query.offset(skip).limit(limit).all()

def calculate_total_price(room_id: int, check_in: date, check_out: date, db: Session) -> float:
    room = get_room(db, room_id)
    if not room:
        return 0
    nights = (check_out - check_in).days
    return room.price_per_night * nights

def create_booking(db: Session, booking: schemas.BookingCreate):
    total_price = calculate_total_price(booking.room_id, booking.check_in_date, booking.check_out_date, db)
    
    db_booking = models.Booking(
        **booking.model_dump(),
        total_price=total_price,
        status=models.BookingStatus.PENDING
    )
    db.add(db_booking)
    
    room = get_room(db, booking.room_id)
    if room:
        room.status = models.RoomStatus.BOOKED
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

def update_booking(db: Session, booking_id: int, booking_update: schemas.BookingUpdate):
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return None
    
    update_data = booking_update.model_dump(exclude_unset=True)
    
    if 'check_in_date' in update_data or 'check_out_date' in update_data:
        check_in = update_data.get('check_in_date', db_booking.check_in_date)
        check_out = update_data.get('check_out_date', db_booking.check_out_date)
        update_data['total_price'] = calculate_total_price(db_booking.room_id, check_in, check_out, db)
    
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    
    if booking_update.status == models.BookingStatus.CANCELLED:
        room = get_room(db, db_booking.room_id)
        if room:
            room.status = models.RoomStatus.AVAILABLE
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

def delete_booking(db: Session, booking_id: int):
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return False
    
    room = get_room(db, db_booking.room_id)
    if room and db_booking.status != models.BookingStatus.CANCELLED:
        room.status = models.RoomStatus.AVAILABLE
    
    db.delete(db_booking)
    db.commit()
    return True

def get_bookings_by_date_range(db: Session, start_date: date, end_date: date):
    return db.query(models.Booking).filter(
        and_(
            models.Booking.check_in_date >= start_date,
            models.Booking.check_out_date <= end_date
        )
    ).all()

def get_room_occupancy_report(db: Session, start_date: date, end_date: date) -> List[dict]:
    total_days = (end_date - start_date).days
    if total_days <= 0:
        total_days = 1
    
    rooms = db.query(models.Room).all()
    report = []
    
    for room in rooms:
        booked_days = db.query(func.sum(func.julianday(models.Booking.check_out_date) - func.julianday(models.Booking.check_in_date))).filter(
            and_(
                models.Booking.room_id == room.id,
                models.Booking.status.in_([models.BookingStatus.CONFIRMED, models.BookingStatus.CHECKED_IN]),
                models.Booking.check_in_date < end_date,
                models.Booking.check_out_date > start_date
            )
        ).scalar() or 0
        
        occupancy_rate = (booked_days / total_days) * 100
        revenue = db.query(func.sum(models.Booking.total_price)).filter(
            and_(
                models.Booking.room_id == room.id,
                models.Booking.check_in_date >= start_date,
                models.Booking.check_out_date <= end_date,
                models.Booking.status == models.BookingStatus.CHECKED_OUT
            )
        ).scalar() or 0
        
        report.append({
            "room_id": room.id,
            "room_number": room.room_number,
            "occupancy_rate": round(occupancy_rate, 2),
            "total_revenue": revenue
        })
    
    return sorted(report, key=lambda x: x["occupancy_rate"], reverse=True)

def get_popular_rooms_report(db: Session, limit: int = 5) -> List[dict]:
    results = db.query(
        models.Room.room_type,
        func.count(models.Booking.id).label('booking_count'),
        func.sum(models.Booking.total_price).label('total_revenue')
    ).join(
        models.Booking, models.Room.id == models.Booking.room_id
    ).filter(
        models.Booking.status == models.BookingStatus.CHECKED_OUT
    ).group_by(
        models.Room.room_type
    ).order_by(
        desc('booking_count')
    ).limit(limit).all()
    
    return [
        {
            "room_type": r.room_type.value if hasattr(r.room_type, 'value') else r.room_type,
            "booking_count": r.booking_count,
            "total_revenue": r.total_revenue
        }
        for r in results
    ]
