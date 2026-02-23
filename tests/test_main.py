from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from datetime import date

client = TestClient(app)

def test_read_root():
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Cymbal Travel Mock API"}

@patch('app.database.save_inventory')
def test_save_inventory(mock_save):
    mock_save.return_value = True
    response = client.get("/api/save_inventory")
    assert response.status_code == 200
    assert response.json() == {"message": "Travel inventory saved successfully"}

@patch('app.database.search_flights')
def test_search_flights(mock_search_flights):
    mock_search_flights.return_value = [
        {
            "id": "fl-123", 
            "airline": "Cymbal Air", 
            "flight_number": "CA101",
            "departure_city": "San Francisco",
            "arrival_city": "London",
            "origin": "SFO", 
            "destination": "LHR", 
            "departure_time": "2025-12-25T10:00:00", 
            "arrival_time": "2025-12-25T20:00:00", 
            "price": 500.0,
            "seat_class": "Economy",
            "connections": 0
        }
    ]
    response = client.get("/api/flights/search", params={"origin": "SFO", "destination": "LHR", "date": "2025-12-25"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "fl-123"
    assert data[0]["flight_number"] == "CA101"

@patch('app.database.search_hotels')
def test_search_hotels(mock_search_hotels):
    mock_search_hotels.return_value = [
        {
            "id": "ht-123", 
            "property_name": "Cymbal Resort", 
            "location": "Bali", 
            "description": "Nice place", 
            "image_url": "url", 
            "rating": 5.0, 
            "amenities": [], 
            "rooms": []
        }
    ]
    response = client.get("/api/hotels/search", params={"location": "Bali"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["property_name"] == "Cymbal Resort"

@patch('app.database.search_cars')
def test_search_cars(mock_search_cars):
    mock_search_cars.return_value = [
        {
            "id": "car-123", 
            "type": "Sedan",
            "brand": "Cymbal Rentals",
            "model": "Model S",
            "year": 2024,
            "title": "Luxury Sedan", 
            "description": "Fast", 
            "image_url": "url", 
            "price_per_day": 100.0,
            "rating": 4.5
        }
    ]
    response = client.get("/api/cars/search", params={"location": "SFO"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["model"] == "Model S"

@patch('app.database.add_to_cart')
@patch('app.database.get_cart')
def test_add_to_cart(mock_get_cart, mock_add):
    mock_add.return_value = True
    # Return structure matching CartModel
    mock_get_cart.return_value = {
        "user_id": "user1", 
        "items": [
            {
                "id": "cart-item-1",
                "type": "flight",
                "item_details": {"id": "fl-123", "price": 500.0},
                "quantity": 1,
                "total_price": 500.0
            }
        ], 
        "total_price": 500.0
    }
    
    payload = {
        "user_id": "user1",
        "type": "flight",
        "item_id": "fl-123"
    }
    response = client.post("/api/cart/add", json=payload)
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Item added to cart"

@patch('app.database.remove_from_cart')
@patch('app.database.get_cart')
def test_remove_from_cart(mock_get_cart, mock_remove):
    mock_remove.return_value = True
    mock_get_cart.return_value = {"user_id": "user1", "items": [], "total_price": 0.0}
    
    payload = {
        "user_id": "user1",
        "item_id": "cart-item-1"
    }
    response = client.post("/api/cart/remove", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Item removed from cart"

@patch('app.database.get_cart')
def test_get_cart(mock_get_cart):
    mock_get_cart.return_value = {
        "user_id": "user1", 
        "items": [
            {
                "id": "cart-item-1",
                "type": "flight",
                "item_details": {"id": "fl-123", "airline": "Test Air"},
                "quantity": 1,
                "total_price": 500.0
            }
        ], 
        "total_price": 500.0
    }
    response = client.get("/api/cart/user1")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    assert len(data["items"]) == 1
    assert data["items"][0]["item_details"]["airline"] == "Test Air"

@patch('app.database.clear_cart')
@patch('app.database.get_cart')
def test_checkout(mock_get_cart, mock_clear):
    mock_get_cart.return_value = {
        "user_id": "user1", 
        "items": [{"id": "cart-item-1", "type": "flight", "item_details": {}, "total_price": 500.0, "quantity": 1}], 
        "total_price": 500.0
    }
    mock_clear.return_value = True
    
    payload = {"user_id": "user1"}
    response = client.post("/api/cart/checkout", json=payload)
    assert response.status_code == 200
    assert "confirmation_code" in response.json()

@patch('app.database.verify_user')
def test_login(mock_verify):
    mock_verify.return_value = True
    payload = {"username": "testuser", "password": "password"}
    response = client.post("/api/login", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()

@patch('app.database.create_user')
def test_create_user(mock_create):
    mock_create.return_value = True
    payload = {"username": "newuser", "password": "password"}
    response = client.post("/api/users", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
