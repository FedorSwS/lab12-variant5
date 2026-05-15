import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_customer():
    response = client.post("/api/customers/", json={
        "full_name": "Test Customer",
        "email": "test@example.com",
        "phone": "+79991234567",
        "passport_number": "TEST123456",
        "address": "Test Address"
    })
    return response.json()

@pytest.fixture
def test_room():
    response = client.post("/api/rooms/", json={
        "room_number": "101",
        "room_type": "standard",
        "price_per_night": 100.0,
        "capacity": 2,
        "floor": 1,
        "has_view": False,
        "has_wifi": True,
        "has_ac": True
    })
    return response.json()

def test_create_booking(test_customer, test_room):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    response = client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat(),
        "special_requests": "Extra pillow"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == test_customer["id"]
    assert data["room_id"] == test_room["id"]
    assert data["total_price"] == 200.0

def test_create_booking_invalid_dates(test_customer, test_room):
    check_in = date.today() + timedelta(days=3)
    check_out = date.today() + timedelta(days=1)
    
    response = client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    assert response.status_code == 400

def test_create_booking_customer_not_found(test_room):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    response = client.post("/api/bookings/", json={
        "customer_id": 99999,
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    assert response.status_code == 404

def test_create_booking_room_not_found(test_customer):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    response = client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": 99999,
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    assert response.status_code == 404

def test_read_booking(test_customer, test_room):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    create_resp = client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    booking_id = create_resp.json()["id"]
    
    response = client.get(f"/api/bookings/{booking_id}")
    assert response.status_code == 200
    assert response.json()["id"] == booking_id

def test_read_booking_not_found():
    response = client.get("/api/bookings/99999")
    assert response.status_code == 404

def test_update_booking(test_customer, test_room):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    create_resp = client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    booking_id = create_resp.json()["id"]
    
    new_check_out = date.today() + timedelta(days=5)
    response = client.put(f"/api/bookings/{booking_id}", json={
        "check_out_date": new_check_out.isoformat(),
        "special_requests": "Late check-in"
    })
    assert response.status_code == 200
    assert response.json()["total_price"] == 400.0

def test_delete_booking(test_customer, test_room):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    create_resp = client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    booking_id = create_resp.json()["id"]
    
    response = client.delete(f"/api/bookings/{booking_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/api/bookings/{booking_id}")
    assert get_response.status_code == 404

def test_get_occupancy_report(test_customer, test_room):
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=3)
    
    client.post("/api/bookings/", json={
        "customer_id": test_customer["id"],
        "room_id": test_room["id"],
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat()
    })
    
    start_date = date.today()
    end_date = date.today() + timedelta(days=30)
    
    response = client.get(f"/api/bookings/report/occupancy?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}")
    assert response.status_code == 200
    assert len(response.json()) >= 1
