from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app import schemas, crud

router = APIRouter()

@router.post("/", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, booking.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    room = crud.get_room(db, booking.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if booking.check_in_date >= booking.check_out_date:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")
    
    available_rooms = crud.get_available_rooms(db, booking.check_in_date, booking.check_out_date)
    if room not in available_rooms:
        raise HTTPException(status_code=400, detail="Room not available for selected dates")
    
    return crud.create_booking(db, booking)

@router.get("/", response_model=List[schemas.Booking])
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return crud.get_bookings(db, skip=skip, limit=limit, customer_id=customer_id)

@router.get("/{booking_id}", response_model=schemas.BookingWithDetails)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}", response_model=schemas.Booking)
def update_booking(
    booking_id: int,
    booking_update: schemas.BookingUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_booking(db, booking_id, booking_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Booking not found")
    return updated

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_booking(db, booking_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Booking not found")
    return None

@router.get("/report/occupancy", response_model=List[schemas.RoomOccupancyReport])
def get_occupancy_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    return crud.get_room_occupancy_report(db, start_date, end_date)

@router.get("/report/popular-rooms", response_model=List[schemas.PopularRoomReport])
def get_popular_rooms(limit: int = 5, db: Session = Depends(get_db)):
    return crud.get_popular_rooms_report(db, limit)
