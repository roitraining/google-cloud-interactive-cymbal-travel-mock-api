
import os
import random
import uuid
from datetime import datetime, timedelta
from google.cloud import firestore
from app.models import (
    Car, Hotel, HotelRoom, Flight, CartItemDetail
)
from app import config

# Lazy Firestore client — initialized on first use to reduce cold start time
db = None

def _get_db():
    """Initializes the Firestore client on first use and returns it."""
    global db
    if db is None:
        try:
            db = firestore.Client()
            print("Firestore client initialized for Cymbal Travel.")
        except Exception as e:
            print(f"Warning: Could not initialize Firestore client. {e}")
    return db

# --- Collection Names ---
COL_CARS = "travel-cars"
COL_HOTELS = "travel-hotels"
COL_CARTS = "travel-carts"
COL_ORDERS = "travel-orders"
COL_USERS = "travel-users"

# --- Initialization Data (Mock) ---

MOCK_CARS = [
    {"id": "economy", "type": "Economy", "brand": "Cymbal Rentals", "model": "Compact", "year": 2024, "image_url": f"{config.BASE_IMAGE_URL}/economy.jpg", "price_per_day": 45.0, "rating": 4.5, "description": "Fuel efficient and compact."},
    {"id": "sedan", "type": "Sedan", "brand": "Cymbal Rentals", "model": "Comfort", "year": 2024, "image_url": f"{config.BASE_IMAGE_URL}/sedan.jpg", "price_per_day": 55.0, "rating": 4.6, "description": "Comfortable sedan for your journey."},
    {"id": "suv", "type": "SUV", "brand": "Cymbal Rentals", "model": "Explorer", "year": 2024, "image_url": f"{config.BASE_IMAGE_URL}/suv.jpg", "price_per_day": 85.0, "rating": 4.7, "description": "Spacious for the whole family."},
    {"id": "sports", "type": "Sports", "brand": "Cymbal Rentals", "model": "Racer", "year": 2024, "image_url": f"{config.BASE_IMAGE_URL}/sports.jpg", "price_per_day": 120.0, "rating": 4.8, "description": "Experience the thrill of the road."},
    {"id": "luxury", "type": "Luxury", "brand": "Cymbal Rentals", "model": "S-Class", "year": 2024, "image_url": f"{config.BASE_IMAGE_URL}/luxury.jpg", "price_per_day": 150.0, "rating": 4.9, "description": "Travel in style and comfort."},
    {"id": "pickup", "type": "Pickup", "brand": "Cymbal Rentals", "model": "Hauler", "year": 2024, "image_url": f"{config.BASE_IMAGE_URL}/pickup.jpg", "price_per_day": 80.0, "rating": 4.5, "description": "Rugged and reliable for any terrain."}
]

# Keep basic mock hotels as fallback, but save_inventory uses full list
MOCK_HOTELS = [
    {
        "id": "hotel-dt-1", "property_name": "Cymbal Hotel - Downtown", "location": "San Francisco", "description": "Central location near all amenities.", "image_url": f"{config.BASE_IMAGE_URL}/hotel-downtown.jpg", "rating": 4.2, "amenities": ["Wifi", "Gym", "Restaurant"],
        "rooms": [
            {"id": "rm-dt-k", "hotel_id": "hotel-dt-1", "room_type": "King", "price_per_night": 250.0, "description": "Spacious King bed with city view.", "image_url": f"{config.BASE_IMAGE_URL}/room-king.jpg"},
            {"id": "rm-dt-q", "hotel_id": "hotel-dt-1", "room_type": "Queen", "price_per_night": 200.0, "description": "Cozy Queen bed.", "image_url": f"{config.BASE_IMAGE_URL}/room-queen.jpg"},
            {"id": "rm-dt-s", "hotel_id": "hotel-dt-1", "room_type": "Suite", "price_per_night": 450.0, "description": "Luxury suite with living area.", "image_url": f"{config.BASE_IMAGE_URL}/room-suite.jpg"},
            {"id": "rm-dt-std", "hotel_id": "hotel-dt-1", "room_type": "Standard", "price_per_night": 180.0, "description": "Standard room, great value.", "image_url": f"{config.BASE_IMAGE_URL}/room-standard.jpg"}
        ]
    }
]

LOCATIONS = [
    "Bali, Indonesia", "Santorini, Greece", "Maui, Hawaii", "Bora Bora, French Polynesia", 
    "Maldives", "Phuket, Thailand", "Kyoto, Japan", "Machu Picchu, Peru", 
    "Amalfi Coast, Italy", "Costa Rica", "Seychelles", "Fiji", 
    "Banff, Canada", "Queenstown, New Zealand", "Marrakech, Morocco", "Dubai, UAE", 
    "Cape Town, South Africa", "Great Barrier Reef, Australia", "Petra, Jordan", "Galapagos Islands, Ecuador",
    "Barcelona, Spain", "Paris, France", "Rome, Italy", "Venice, Italy", 
    "New York City, USA", "Tokyo, Japan", "Istanbul, Turkey", "Rio de Janeiro, Brazil", 
    "Sydney, Australia", "London, UK", "Cairo, Egypt", "Reykjavik, Iceland", 
    "Dubrovnik, Croatia", "Cancun, Mexico", "Prague, Czech Republic", "Amsterdam, Netherlands",
    "Lisbon, Portugal", "Hanoi, Vietnam", "Buenos Aires, Argentina", "Budapest, Hungary",
    "Zanzibar, Tanzania", "Lofoten Islands, Norway", "Cinque Terre, Italy", "Siem Reap, Cambodia",
    "Serengeti, Tanzania", "Patagonia, Chile", "Antigua, Guatemala", "Cartagena, Colombia",
    "Ubud, Indonesia", "Cappadocia, Turkey"
]

def save_inventory():
    """Initializes the Car and Hotel inventory in Firestore using the full list."""
    _get_db()
    if not db:
        return False
    
    batch = db.batch()
    
    # Save Cars
    for car in MOCK_CARS:
        ref = db.collection(COL_CARS).document(car["id"])
        batch.set(ref, car)
        
    # Save Hotels - Generate 50 resorts
    # First, delete existing to prevent duplicates if IDs change or to clean up
    # Note: Deleting in transaction/batch is harder with large datasets, but for 50 it's ok to overwrite
    # if we use consistent IDs. But here we generate UUIDs. 
    # Let's delete all first.
    
    try:
        docs = db.collection(COL_HOTELS).list_documents()
        for doc in docs:
            doc.delete()
    except Exception as e:
        print(f"Error clearing hotels: {e}")

    # Create new resorts
    count = 0
    # Batch limit is 500. We have 50 items + 6 cars = 56 ops. Safe.
    
    for i, location in enumerate(LOCATIONS):
        hotel_id = str(uuid.uuid4())
        city = location.split(",")[0].strip()
        property_name = f"Cymbal Resort {city}"
        slug_location = location.lower().replace(",", "").replace(" ", "-")
        hotel_image_url = f"{config.BASE_IMAGE_URL}/resort-{slug_location}.jpg"
        
        description = f"Experience luxury at {property_name} in {location}. Enjoy world-class amenities, breathtaking views, and unparalleled service."
        
        resort_data = {
            "id": hotel_id,
            "property_name": property_name,
            "location": location,
            "description": description,
            "image_url": hotel_image_url,
            "rating": round(random.uniform(4.0, 5.0), 1),
            "amenities": ["Pool", "Spa", "Fine Dining", "Concierge", "Beach/Mountain View", "Wifi"],
            "rooms": []
        }
        
        room_types = [
            {"type": "Standard Room", "desc": "A comfortable room with a view.", "slug": "standard", "base_price": random.randint(200, 400)},
            {"type": "Suite", "desc": "Spacious suite with multiple rooms and a full kitchen.", "slug": "suite", "base_price": random.randint(500, 900)},
            {"type": "Cabin", "desc": "Private separate building with 2 bedrooms, living area, and kitchen.", "slug": "cabin", "base_price": random.randint(1000, 2000)}
        ]
        
        for rt in room_types:
            room_id = str(uuid.uuid4())
            room_image_url = f"{config.BASE_IMAGE_URL}/resort-{slug_location}-{rt['slug']}.jpg"
            room_data = {
                "id": room_id,
                "hotel_id": hotel_id,
                "room_type": rt["type"],
                "price_per_night": float(rt["base_price"]),
                "description": rt["desc"],
                "image_url": room_image_url
            }
            resort_data["rooms"].append(room_data)
        
        ref = db.collection(COL_HOTELS).document(hotel_id)
        batch.set(ref, resort_data)
        count += 1
        
    batch.commit()
    print(f"Travel inventory initialized. Created {count} resorts and {len(MOCK_CARS)} cars.")
    return True

# --- Retrieval Functions ---

def search_cars(location: str = None, date: str = None):
    _get_db()
    if not db:
        return MOCK_CARS # Fallback for local testing without creds
        
    # Return all cars, ignoring location/date as requested
    cars_ref = db.collection(COL_CARS)
    docs = cars_ref.stream()
    results = [doc.to_dict() for doc in docs]
    return results

def search_hotels(location: str = None, date: str = None):
    _get_db()
    if not db:
        all_hotels = MOCK_HOTELS
    else:
        # Filter by location name match
        hotels_ref = db.collection(COL_HOTELS)
        docs = hotels_ref.stream()
        all_hotels = [doc.to_dict() for doc in docs]

    if not location:
        return all_hotels
        
    filtered = [h for h in all_hotels if location.lower() in h.get("location", "").lower() or location.lower() in h.get("property_name", "").lower()]
    return filtered if filtered else all_hotels # Return all if no match found (for demo)

def get_top_resorts(limit: int = 3):
    _get_db()
    if not db:
        return MOCK_HOTELS[:limit]
        
    hotels_ref = db.collection(COL_HOTELS)
    docs = hotels_ref.stream()
    all_hotels = [doc.to_dict() for doc in docs]
    
    if not all_hotels:
        # Fallback to MOCK if DB is empty but connected? varying behavior
        return MOCK_HOTELS[:limit]
        
    if len(all_hotels) <= limit:
        return all_hotels
        
    return random.sample(all_hotels, limit)



COL_FLIGHTS = "flights"

def search_flights(origin: str, destination: str, date: str):
    """Generates mock flights."""
    _get_db()
    # Deterministic random based on input so it feels consistent
    random.seed(f"{origin}{destination}{date}")
    
    results = []
    # Mock airlines for variety
    airlines = ["Cymbal Air", "Cymbal Air Express", "SkyBlue", "FlyGlobal"]
    times = [
        "06:00", "07:15", "08:30", "09:45", "11:00", 
        "13:15", "14:45", "16:20", "17:50", "19:10", "21:30"
    ]
    
    # Generate 5-8 options
    num_flights = random.randint(5, 8)
    
    for _ in range(num_flights):
        flight_num = f"{random.choice(['CA', 'SB', 'FG'])}-{random.randint(100, 999)}"
        dept_str = f"{date} {random.choice(times)}"
        try:
            dept_dt = datetime.strptime(dept_str, "%Y-%m-%d %H:%M")
        except:
            dept_dt = datetime.now() # Fallback
            
        base_duration = random.randint(2, 14) # Hours
        connections = 0
        
        # 30% chance of a connection which adds time
        if random.random() < 0.3:
            connections = 1
            base_duration += random.randint(2, 5)
            
        arr_dt = dept_dt + timedelta(hours=base_duration)
        
        # Dynamic pricing
        base_price = 150 + (base_duration * 20)
        if connections > 0:
            base_price *= 0.8 # Cheaper with connections usually? Or more expensive? Let's say cheaper.
            
        price = round(base_price + random.randint(-50, 50))
        
        flight_id = str(uuid.uuid4())
        flight = {
            "id": flight_id,
            "airline": random.choice(airlines),
            "flight_number": flight_num,
            "departure_city": origin,
            "arrival_city": destination,
            "departure_time": dept_dt.isoformat(),
            "arrival_time": arr_dt.isoformat(),
            "price": float(price),
            "seat_class": random.choice(["Economy", "Business"]),
            "connections": connections,
            "created_at": datetime.now().isoformat()
        }
        results.append(flight)

    if db:
        # Cleanup old flights first (older than 24 hours)
        try:
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            flights_ref = db.collection(COL_FLIGHTS)
            old_flights = flights_ref.where("created_at", "<", cutoff).stream()
            
            # Batch delete
            batch = db.batch()
            count = 0
            for doc in old_flights:
                batch.delete(doc.reference)
                count += 1
                if count >= 400: # Firestore batch limit is 500
                    batch.commit()
                    batch = db.batch()
                    count = 0
            if count > 0:
                batch.commit()
                print("Cleaned up old flights.")

            # Save new flights
            batch = db.batch()
            for f in results:
                 ref = flights_ref.document(f["id"])
                 batch.set(ref, f)
            batch.commit()
            print(f"Saved {len(results)} generated flights to Firestore.")

        except Exception as e:
            print(f"Error managing flight persistence: {e}")
        
    return results

# --- Cart Logic ---

def get_cart(user_id: str):
    _get_db()
    if not db:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
        
    cart_ref = db.collection(COL_CARTS).document(user_id)
    doc = cart_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        return data
    else:
        return {"user_id": user_id, "items": [], "total_price": 0.0}

def clear_cart(user_id: str):
    _get_db()
    if not db:
        return True
    
    cart_ref = db.collection(COL_CARTS).document(user_id)
    cart_ref.delete()
    return True

def add_to_cart(cart_add_request):
    """
    Adds a fully formed item to the cart.
    """
    _get_db()
    if not db:
        return False

    user_id = cart_add_request.user_id
    cart_ref = db.collection(COL_CARTS).document(user_id)
    doc = cart_ref.get()
    
    current_data = doc.to_dict() if doc.exists else {"user_id": user_id, "items": [], "total_price": 0.0}
    current_items = current_data.get("items", [])
    
    item_type = cart_add_request.type
    detail_obj = None
    price = 0.0
    
    if item_type == "flight":
        # Check if full details provided (Frontend behavior)
        if cart_add_request.flight_details:
            detail_obj = cart_add_request.flight_details.dict()
            price = detail_obj.get("price", 0.0)
        # Otherwise try to fetch from Firestore (Agent behavior)
        elif db and cart_add_request.item_id:
             try:
                 flight_doc = db.collection(COL_FLIGHTS).document(cart_add_request.item_id).get()
                 if flight_doc.exists:
                     detail_obj = flight_doc.to_dict()
                     # Clean internal fields if needed
                     detail_obj.pop('created_at', None)
                     price = detail_obj.get("price", 0.0)
             except Exception as e:
                 print(f"Error fetching flight {cart_add_request.item_id}: {e}")

    elif item_type == "car":
        try:
            car_doc = db.collection(COL_CARS).document(cart_add_request.item_id).get()
            if car_doc.exists:
                car_data = car_doc.to_dict()
                detail_obj = car_data
                
                start_d = cart_add_request.start_date
                end_d = cart_add_request.end_date
                days = 1
                if start_d and end_d:
                     if isinstance(start_d, str): start_d = datetime.strptime(start_d, "%Y-%m-%d").date()
                     if isinstance(end_d, str): end_d = datetime.strptime(end_d, "%Y-%m-%d").date()
                     # Handle datetime vs date
                     if isinstance(start_d, datetime): start_d = start_d.date()
                     if isinstance(end_d, datetime): end_d = end_d.date()
                     
                     delta = end_d - start_d
                     days = max(1, delta.days)
                     
                price = float(car_data.get("price_per_day", 0.0)) * days
        except Exception as e:
            print(f"Error fetching car: {e}")
            
    elif item_type == "hotel":
        # Find room in all hotels
        found_room = None
        found_hotel_name = ""
        
        try:
            hotels = db.collection(COL_HOTELS).stream()
            target_id = cart_add_request.item_id 
            
            for h_doc in hotels:
                h_data = h_doc.to_dict()
                
                # Check rooms first (more specific)
                for room in h_data.get("rooms", []):
                    if room.get("id") == target_id:
                        found_room = room
                        found_hotel_name = h_data.get("property_name")
                        break
                
                if found_room: break

                # Fallback: check if item_id matches hotel ID (default to first room)
                if h_data.get("id") == target_id:
                     if h_data.get("rooms"):
                         found_room = h_data["rooms"][0]
                         found_hotel_name = h_data.get("property_name")
                         break
            
            if found_room:
                detail_obj = found_room
                detail_obj["hotel_name"] = found_hotel_name
                
                start_d = cart_add_request.start_date
                end_d = cart_add_request.end_date
                days = 1
                if start_d and end_d:
                     if isinstance(start_d, str): start_d = datetime.strptime(start_d, "%Y-%m-%d").date()
                     if isinstance(end_d, str): end_d = datetime.strptime(end_d, "%Y-%m-%d").date()
                     # Handle datetime vs date
                     if isinstance(start_d, datetime): start_d = start_d.date()
                     if isinstance(end_d, datetime): end_d = end_d.date()

                     delta = end_d - start_d
                     days = max(1, delta.days)
                     
                price = float(found_room.get("price_per_night", 0.0)) * days
        except Exception as e:
            print(f"Error searching hotels: {e}")
            
    if not detail_obj:
        print("Error: Could not resolve item details.")
        return False

    # Create new item structure
    new_item = {
        "id": str(uuid.uuid4()),
        "type": item_type,
        "item_details": detail_obj,
        "quantity": cart_add_request.quantity,
        "start_date": cart_add_request.start_date.isoformat() if cart_add_request.start_date else None,
        "end_date": cart_add_request.end_date.isoformat() if cart_add_request.end_date else None,
        "total_price": float(price)
    }
    
    current_items.append(new_item)
    
    # Recalculate total
    new_total = sum([item["total_price"] for item in current_items])
    
    cart_ref.set({
        "user_id": user_id,
        "items": current_items,
        "total_price": new_total
    })
    return True

def remove_from_cart(cart_remove_request):
    _get_db()
    if not db:
        return False
        
    user_id = cart_remove_request.user_id
    cart_ref = db.collection(COL_CARTS).document(user_id)
    doc = cart_ref.get()
    
    if not doc.exists:
        return False

    current_data = doc.to_dict()
    items = current_data.get("items", [])
    
    # Filter out the item with the matching Cart Item ID (not product ID)
    new_items = [i for i in items if i["id"] != cart_remove_request.item_id]
    
    if len(new_items) == len(items):
        return False # Item not found
        
    new_total = sum([item["total_price"] for item in new_items])
    
    cart_ref.set({
        "user_id": user_id,
        "items": new_items,
        "total_price": new_total
    })
    return True

# --- User Management ---

def create_user(username, password):
    # Mock behavior: Always return True, don't save to DB
    return True

def verify_user(username, password):
    # Mock behavior: Always allow login for any password
    return True


