from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app import schemas, crud

router = APIRouter()

@router.post("/", response_model=schemas.Room, status_code=status.HTTP_201_CREATED)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    existing = crud.get_room_by_number(db, room.room_number)
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")
    return crud.create_room(db, room)

@router.get("/", response_model=List[schemas.Room])
def read_rooms(
    skip: int = 0,
    limit: int = 100,
    room_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_rooms(db, skip=skip, limit=limit, room_type=room_type)

@router.get("/available", response_model=List[schemas.Room])
def get_available_rooms(
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    db: Session = Depends(get_db)
):
    if check_in >= check_out:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")
    return crud.get_available_rooms(db, check_in, check_out)

@router.get("/{room_id}", response_model=schemas.Room)
def read_room(room_id: int, db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=schemas.Room)
def update_room(room_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)):
    updated = crud.update_room(db, room_id, room)
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_room(db, room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    return None
