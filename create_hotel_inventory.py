import sys
import os
import random
import uuid

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from app import database

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

def create_resort_inventory():
    if not database.db:
        print("Database not initialized.")
        return

    print("Deleting existing hotel inventory...")
    # Delete Hotels
    hotels_ref = database.db.collection(database.COL_HOTELS)
    docs = hotels_ref.stream()
    for doc in docs:
        doc.reference.delete()
    print("Deleted all hotels.")

    print("Creating 50 exotic resorts...")
    batch = database.db.batch()
    count = 0
    
    # We will process in batches of 500 writes (Firestore limit), but since we have 50 hotels, 1 batch is fine.
    
    for i, location in enumerate(LOCATIONS):
        hotel_id = str(uuid.uuid4())
        city = location.split(",")[0].strip()
        
        property_name = f"Cymbal Resort {city}"
        
        # Consistent image naming convention for future generation
        # e.g., "cymbal-resort-bali-indonesia.jpg"
        slug_location = location.lower().replace(",", "").replace(" ", "-")
        hotel_image_url = f"https://storage.googleapis.com/cymbal-travel-images-dar/resort-{slug_location}.jpg"
        
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
        
        # Create Rooms for each resort
        room_types = [
            {
                "type": "Standard Room",
                "desc": "A comfortable room with a view.",
                "slug": "standard",
                "base_price": random.randint(200, 400)
            },
            {
                "type": "Suite",
                "desc": "Spacious suite with multiple rooms and a full kitchen.",
                "slug": "suite",
                "base_price": random.randint(500, 900)
            },
            {
                "type": "Cabin",
                "desc": "Private separate building with 2 bedrooms, living area, and kitchen.",
                "slug": "cabin",
                "base_price": random.randint(1000, 2000)
            }
        ]
        
        for rt in room_types:
            room_id = str(uuid.uuid4())
            # Consistent image naming: "resort-bali-indonesia-suite.jpg"
            room_image_url = f"https://storage.googleapis.com/cymbal-travel-images-dar/resort-{slug_location}-{rt['slug']}.jpg"
            
            room_data = {
                "id": room_id,
                "hotel_id": hotel_id,
                "room_type": rt["type"],
                "price_per_night": float(rt["base_price"]),
                "description": rt["desc"],
                "image_url": room_image_url
            }
            resort_data["rooms"].append(room_data)
        
        # Add to batch
        ref = database.db.collection(database.COL_HOTELS).document(hotel_id)
        batch.set(ref, resort_data)
        count += 1

    batch.commit()
    print(f"Created {count} resorts with rooms.")

if __name__ == "__main__":
    create_resort_inventory()
