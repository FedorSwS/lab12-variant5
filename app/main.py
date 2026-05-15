from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.database import engine, get_db, Base
from app import schemas
from app.routes import bookings, rooms, customers

app = FastAPI(
    title="Hotel Booking System API",
    description="API for managing hotel room bookings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Hotel Booking System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
