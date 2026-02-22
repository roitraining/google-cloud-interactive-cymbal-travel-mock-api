import os
import random
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, APIRouter, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    Car, Hotel, HotelRoom, Flight, 
    FlightSearchRequest, HotelSearchRequest, CarSearchRequest,
    CartItemDetail, User, LoginRequest, 
    CartAddRequest, CartRemoveRequest, CheckoutRequest, OrderStatusResponse,
    CartModel
)
from app import database
from app import config

app = FastAPI(
    title="Cymbal Travel Mock API",
    description="Mock API for Cymbal Travel agency (Flights, Hotels, Cars) for CX Agent Studio training.",
    version="1.0.0",
    servers=[{"url": config.SERVICE_URL, "description": "Cloud Run Service URL"}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for the frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["UI"])
async def root():
    return FileResponse('app/static/index.html')

# Create a router for the API endpoints
api_router = APIRouter()

@api_router.get("/", tags=["General"])
async def api_root():
    return {"message": "Welcome to the Cymbal Travel Mock API"}

@api_router.get("/save_inventory", tags=["Admin"], summary="Initialize Inventory")
async def save_inventory():
    """
    Initialize the database with mock Cars and Hotels.
    """
    success = database.save_inventory()
    if success:
        return {"message": "Travel inventory saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save inventory")

# --- FLIGHTS ---
@api_router.get("/flights/search", tags=["Flights"], response_model=List[Flight])
async def search_flights(
    origin: str, 
    destination: str, 
    date: str
):
    """
    Search for flights. 
    Notes: Generates deterministic mock data based on inputs.
    """
    return database.search_flights(origin, destination, date)

# --- HOTELS ---
@api_router.get("/hotels/search", tags=["Hotels"], response_model=List[Hotel])
async def search_hotels(
    location: Optional[str] = None, 
    date: Optional[str] = None
):
    """
    Search for hotels by location.
    """
    return database.search_hotels(location, date)

@api_router.get("/hotels/top", tags=["Hotels"], response_model=List[Hotel])
async def get_top_resorts():
    """
    Get 3 random top resorts.
    """
    return database.get_top_resorts(limit=3)

# --- CARS ---
@api_router.get("/cars/search", tags=["Cars"], response_model=List[Car])
async def search_cars(
    location: Optional[str] = None, 
    date: Optional[str] = None
):
    """
    Search for rental cars by location.
    """
    return database.search_cars(location, date)

# --- CART / BOOKING ---

@api_router.post("/cart/add", tags=["Cart"])
async def add_item_to_cart(request: CartAddRequest):
    """
    Add a Flight, Hotel, or Car to the cart/itinerary.
    """
    success = database.add_to_cart(request)
    if success:
        return {"message": "Item added to cart", "cart": database.get_cart(request.user_id)}
    raise HTTPException(status_code=400, detail="Failed to add item")

@api_router.post("/cart/remove", tags=["Cart"])
async def remove_item_from_cart(request: CartRemoveRequest):
    """
    Remove an item from the cart.
    """
    success = database.remove_from_cart(request)
    if success:
        return {"message": "Item removed from cart", "cart": database.get_cart(request.user_id)}
    raise HTTPException(status_code=400, detail="Failed to remove item")

@api_router.get("/cart/{user_id}", tags=["Cart"], response_model=CartModel)
async def get_cart(user_id: str):
    """
    Get the current user's cart/itinerary.
    """
    cart_data = database.get_cart(user_id)
    # The DB now returns structure matching CartModel more closely
    return CartModel(
        user_id=cart_data["user_id"],
        items=cart_data["items"], 
        total_price=cart_data["total_price"]
    )

@api_router.post("/cart/checkout", tags=["Cart"])
async def checkout(request: CheckoutRequest):
    """
    Book all items in the cart.
    """
    cart = database.get_cart(request.user_id)
    if not cart or not cart.get('items'):
       raise HTTPException(status_code=400, detail="Cart is empty")

    order_id = str(uuid.uuid4())
    # In a real app, we'd save the order to 'travel-orders' here.
    # For now, just clear the cart.
    # We can add a create_order function in database if needed later.
    
    # Actually, let's just clear for the mock checkout
    success = database.clear_cart(request.user_id)
    
    if success:
        return {
            "message": "Booking successful! Your dream trip awaits.", 
            "order_id": order_id,
            "confirmation_code": f"CYMBAL-{order_id[:8].upper()}"
        }
    raise HTTPException(status_code=500, detail="Failed to process booking")

# --- USERS ---

@api_router.post("/users", tags=["Users"])
async def create_account(user: User):
    database.create_user(user.username, user.password)
    return {"message": "User created successfully", "username": user.username}

@api_router.post("/login", tags=["Users"])
async def login(request: LoginRequest):
    if database.verify_user(request.username, request.password):
        return {"message": "Login successful", "token": "mock-token-123"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Include the router with the /api prefix
app.include_router(api_router, prefix="/api")
