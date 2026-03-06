from pydantic import BaseModel
from typing import Optional, List, Union, Any
from datetime import date, datetime

class Car(BaseModel):
    id: str
    type: str  # e.g., "Economy", "SUV", "Luxury"
    brand: str # "Cymbal Rentals"
    model: str # e.g. "Model S", "Civic"
    year: int
    image_url: str
    price_per_day: float
    rating: float
    description: str

class HotelRoom(BaseModel):
    id: str
    hotel_id: str
    hotel_name: Optional[str] = None
    room_type: str # "King", "Queen", "Suite"
    price_per_night: float
    description: str
    image_url: str

class Hotel(BaseModel):
    id: str
    property_name: str # "Cymbal Hotel - Downtown"
    location: str
    description: str
    image_url: str
    rating: float
    amenities: List[str]
    rooms: List[HotelRoom] = []
    
class Flight(BaseModel):
    id: str
    airline: str # "Cymbal Air"
    flight_number: str
    departure_city: str
    arrival_city: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    seat_class: str # "Economy", "Business", "First"
    connections: int # 0 for Non-stop, 1, 2 etc.

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    date: date

class HotelSearchRequest(BaseModel):
    location: str
    date: date

class CarSearchRequest(BaseModel):
    location: str
    date: date

class CartItemDetail(BaseModel):
    id: str # UUID for the cart item itself
    type: str # "flight", "hotel", "car"
    item_details: Any # Snapshot of the item (using Any to support custom fields like hotel_name)
    quantity: int = 1 
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_price: float 

class CartAddRequest(BaseModel):
    user_id: str
    type: str # "flight", "hotel", "car"
    item_id: str # The ID of the flight, hotel room, or car type
    flight_details: Optional[Flight] = None 
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    quantity: int = 1

class CartRemoveRequest(BaseModel):
    user_id: str
    item_id: str # The UUID of the CartItem

class CheckoutRequest(BaseModel):
    user_id: str

class OrderStatusResponse(BaseModel):
    order_id: str
    status: str
    confirmation_code: str

class User(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class CartModel(BaseModel):
    user_id: str
    items: List[CartItemDetail]
    total_price: float

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None


class SessionCreateResponse(BaseModel):
    session_id: str
    user_id: str

