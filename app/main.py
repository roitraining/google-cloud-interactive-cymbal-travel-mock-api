import os
import random
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, APIRouter, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    Car, Hotel, Flight,
    CartItemDetail, User, LoginRequest,
    CartAddRequest, CartRemoveRequest, CheckoutRequest,
    CartModel, ChatRequest
)
from app import database
from app import chat
from app import config


app = FastAPI(
    title="Cymbal Travel Mock API",
    description="Mock API for Cymbal Travel Resorts (Flights, Resorts (Hotels), Cars) for CX Agent Studio training.",
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

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse('app/static/favicon.svg')

@app.get("/", tags=["UI"])
async def root():
    return FileResponse('app/static/index.html')

# Create a router for the API endpoints
api_router = APIRouter()

@api_router.get("/", tags=["General"], operation_id="api_root")
async def api_root():
    return {"message": "Welcome to the Cymbal Travel Mock API"}

@api_router.get("/save_inventory", tags=["Admin"], summary="Initialize Inventory", operation_id="save_inventory")
async def save_inventory():
    """
    Initialize the database with mock Cars and Hotels.
    """
    success = database.save_inventory()
    if success:
        return {"message": "Travel inventory saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save inventory")

@api_router.post("/chat", tags=["Chat"], operation_id="chat_endpoint")
async def chat_endpoint(request: ChatRequest):
    """
    Interact with the Vertex AI Agent.
    """
    try:
        response = await chat.process_message(request.user_id, request.message)
        
        # If response is empty or None, return a friendly message
        if not response:
             return {"response": "I didn't receive a response from the agent. Please try again."}
             
        return {"response": response}
    except Exception as e:
        # Log the error on the server side
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- FLIGHTS ---
@api_router.get("/flights/search", tags=["Flights"], response_model=List[Flight], operation_id="search_flights")
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
@api_router.get("/hotels/search", tags=["Hotels"], response_model=List[Hotel], operation_id="search_hotels")
async def search_hotels(
    location: Optional[str] = Query(None, description="The location to search for (e.g. 'Paris', 'London')."),
    date: Optional[str] = Query(None, description="Check-in date (optional). If not provided, returns availability for next week.")
):
    """
    Search for hotels, resorts, and accommodations by location.
    """
    return database.search_hotels(location, date)

@api_router.get("/hotels/top", tags=["Hotels"], response_model=List[Hotel], operation_id="get_top_resorts")
async def get_top_resorts():
    """
    Get 3 random top resorts.
    """
    return database.get_top_resorts(limit=3)

# --- CARS ---
@api_router.get("/cars/search", tags=["Cars"], response_model=List[Car], operation_id="search_cars")
async def search_cars(
    location: Optional[str] = None, 
    date: Optional[str] = None
):
    """
    Search for rental cars by location.
    """
    return database.search_cars(location, date)

# --- CART / BOOKING ---

@api_router.post("/cart/add", tags=["Cart"], operation_id="add_item_to_cart")
async def add_item_to_cart(request: CartAddRequest):
    """
    Add a Flight, Hotel, or Car to the cart/itinerary.
    """
    success = database.add_to_cart(request)
    if success:
        return {"message": "Item added to cart", "cart": database.get_cart(request.user_id)}
    raise HTTPException(status_code=400, detail="Failed to add item")

@api_router.post("/cart/remove", tags=["Cart"], operation_id="remove_item_from_cart")
async def remove_item_from_cart(request: CartRemoveRequest):
    """
    Remove an item from the cart.
    """
    success = database.remove_from_cart(request)
    if success:
        return {"message": "Item removed from cart", "cart": database.get_cart(request.user_id)}
    raise HTTPException(status_code=400, detail="Failed to remove item")

@api_router.get("/cart/{user_id}", tags=["Cart"], response_model=CartModel, operation_id="get_cart")
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

@api_router.post("/cart/checkout", tags=["Cart"], operation_id="checkout")
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

@api_router.post("/users", tags=["Users"], operation_id="create_account")
async def create_account(user: User):
    database.create_user(user.username, user.password)
    return {"message": "User created successfully", "username": user.username}

@api_router.post("/login", tags=["Users"], operation_id="login")
async def login(request: LoginRequest):
    if database.verify_user(request.username, request.password):
        return {"message": "Login successful", "token": "mock-token-123"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Include the router with the /api prefix
app.include_router(api_router, prefix="/api")
