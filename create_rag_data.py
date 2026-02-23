import os
import shutil
from google.cloud import storage

# Configuration
LOCAL_DIR = "rag_data"
# Default from environment or fallback
BUCKET_NAME_ENV = os.environ.get("RAG_BUCKET_NAME", "cymbal-travel-faqs-dar")

# Mock Resort Data
RESORT_NAME = "Cymbal Resort & Spa"

# Content Templates
ABOUT_US = """About {resort_name}
{resort_name} is a world-class luxury destination offering unforgettable experiences in some of the most beautiful locations on Earth. 
Founded in 2015, we blend local culture with modern elegance to create the perfect getaway for families, couples, and solo travelers.
Our mission is to provide exceptional service, sustainable luxury, and memories that last a lifetime.
"""

POLICIES = """{resort_name} Policies & Information

Check-in / Check-out:
- Check-in time: 3:00 PM
- Check-out time: 11:00 AM
- Early check-in and late check-out are subject to availability and may incur additional fees.

Cancellation Policy:
- Standard Rate: Free cancellation up to 48 hours before check-in.
- Non-Refundable Rate: No refund upon cancellation, but dates may be modified for a fee.
- Holiday Season: Cancellations must be made 7 days in advance.

Pet Policy:
- We are a pet-friendly resort!
- Dogs up to 50 lbs are welcome with a $75 per stay cleaning fee.
- Service animals are always welcome free of charge.

Smoking Policy:
- All indoor areas, including guest rooms and balconies, are 100% non-smoking.
- Designated outdoor smoking areas are available.
- A $500 cleaning fee applies for smoking in rooms.
"""

DINING = """Dining at {resort_name}

1. The Ocean Breeze (Seafood & Grill)
   - Open for Lunch (12pm-3pm) and Dinner (6pm-10pm).
   - Features fresh, locally sourced seafood and ocean views.
   - Reservations recommended for dinner.

2. Mountain Peak Bistro (Casual Dining)
   - Open for Breakfast (7am-11am) and Lunch (12pm-4pm).
   - Buffet breakfast and a la carte lunch menu.

3. The Velvet Lounge (Bar & Cocktails)
   - Open daily from 5pm to 1am.
   - Live music on Fridays and Saturdays.
   - Happy Hour: 5pm-7pm daily.

In-Room Dining:
- Available 24 hours a day.
- A $5 delivery charge applies to all orders.
"""

AMENITIES = """Resort Amenities

Pools:
- Main Infinity Pool: Open 8am-8pm.
- Adults-Only Serenity Pool: Open 9am-10pm.
- Kids Splash Zone: Open 9am-6pm.

Spa & Wellness:
- The Cymbal Spa offers massages, facials, and body treatments.
- Open daily 9am-7pm. Appointments required.
- Fitness Center: Open 24/7 with key card access.
- Yoga classes held every morning at 8am on the beach/terrace.

Connectivity:
- Complimentary high-speed Wi-Fi is available throughout the resort.
- Business Center with printing services available in the lobby.
"""

ACTIVITIES = """Activities & Experiences

Water Sports:
- Snorkeling gear and kayaks are complimentary for guests.
- Jet ski rentals and guided diving tours are available for a fee.

Kids Club:
- Camp Cymbal is open for children aged 4-12.
- Hours: 9am-5pm daily.
- Activities include arts & crafts, treasure hunts, and movie nights.

Excursions:
- Concierge can book local tours, sunset cruises, and cultural experiences.
- Shuttle service to downtown/shopping districts runs every hour.
"""

FAQ_TEMPLATES = [
    ("Check-in Time", "What time is check-in?", "Check-in at {resort_name} is at 3:00 PM."),
    ("Check-out Time", "What time is check-out?", "Check-out is at 11:00 AM. Late check-out may be available upon request."),
    ("Pets", "Do you allow pets?", "Yes, dogs up to 50 lbs are welcome for a $75 fee per stay."),
    ("Breakfast", "Is breakfast included?", "Breakfast is included for 'Bed & Breakfast' packages. Otherwise, it is available at Mountain Peak Bistro."),
    ("Pools", "Is there a pool?", "Yes, we have a main infinity pool, an adults-only pool, and a kids' splash zone."),
    ("Gym", "Do you have a gym?", "Yes, our fitness center is open 24/7 for all guests."),
    ("WiFi", "Is there Wi-Fi?", "Yes, complimentary high-speed Wi-Fi is available throughout the property."),
    ("Cancellation", "Can I cancel my reservation?", "Standard bookings can be cancelled free of charge up to 48 hours before arrival."),
    ("Room Service", "Do you have room service?", "Yes, 24-hour in-room dining is available."),
    ("Spa", "Is there a spa?", "Yes, The Cymbal Spa offers a variety of treatments from 9am to 7pm daily."),
    ("Airport Distance", "How far is the airport?", "We are typically located within 30-45 minutes of the nearest major airport."),
    ("Airport Shuttle", "Do you offer airport shuttles?", "Yes, airport transfers can be arranged through our concierge for a fee."),
    ("Parking", "Is parking available?", "Valet parking is $30/night. Self-parking is complimentary."),
    ("Kids Activities", "Are there kids' activities?", "Yes, Camp Cymbal offers daily activities for children aged 4-12."),
    ("All Inclusive", "Is the resort all-inclusive?", "We offer both room-only and all-inclusive packages. Please check your booking details."),
    ("Dress Code", "Do you have a dress code for restaurants?", "Resort casual is required for dinner at The Ocean Breeze. No swimwear allowed in dining areas."),
    ("Weddings", "Can I host a wedding here?", "Absolutely! We have beautiful venues for weddings and events. Contact our events team."),
    ("Smoking", "Is smoking allowed?", "Smoking is prohibited in rooms and balconies. Designated outdoor areas are provided."),
    ("Balconies", "Do rooms have balconies?", "Most rooms feature a private balcony or terrace with views."),
    ("Safe", "Is there a safe in the room?", "Yes, all rooms are equipped with an electronic safe."),
    ("Towels", "Do you provide beach towels?", "Yes, complimentary beach and pool towels are provided."),
    ("Doctor", "Is there a doctor on call?", "Guest services can arrange for medical assistance 24/7 if needed."),
    ("Payment", "Do you accept cash?", "We are a cashless resort. All major credit cards and room charges are accepted."),
    ("Upgrades", "Can I upgrade my room?", "Upgrades are subject to availability upon arrival. Ask the front desk!"),
    ("Connecting Rooms", "Are there connecting rooms?", "Yes, connecting rooms are available for families upon request.")
]

def create_local_files():
    """Generates the text files locally."""
    if os.path.exists(LOCAL_DIR):
        shutil.rmtree(LOCAL_DIR)
    os.makedirs(LOCAL_DIR)
    print(f"Creating local files in '{LOCAL_DIR}'...")

    # Write Static content
    with open(f"{LOCAL_DIR}/about_us.txt", "w") as f:
        f.write(ABOUT_US.format(resort_name=RESORT_NAME))
    
    with open(f"{LOCAL_DIR}/resort_policies.txt", "w") as f:
        f.write(POLICIES.format(resort_name=RESORT_NAME))

    with open(f"{LOCAL_DIR}/dining_options.txt", "w") as f:
        f.write(DINING.format(resort_name=RESORT_NAME))

    with open(f"{LOCAL_DIR}/amenities.txt", "w") as f:
        f.write(AMENITIES.format(resort_name=RESORT_NAME))

    with open(f"{LOCAL_DIR}/activities.txt", "w") as f:
        f.write(ACTIVITIES.format(resort_name=RESORT_NAME))

    # Generate FAQs
    for i, (topic, q, a) in enumerate(FAQ_TEMPLATES):
        formatted_a = a.format(resort_name=RESORT_NAME)
        content = f"Topic: {topic}\nQuestion: {q}\nAnswer: {formatted_a}\n"
        with open(f"{LOCAL_DIR}/faq{i+1}.txt", "w") as f:
            f.write(content)
            
    print(f"Generated {len(FAQ_TEMPLATES)} FAQs and 5 info pages.")

def upload_to_gcs(bucket_name):
    """Uploads the local files to GCS."""
    print(f"Uploading files to GCS Bucket: {bucket_name}...")
    try:
        storage_client = storage.Client()
        # Ensure project is set if needed, usually inferred from env
        # storage_client = storage.Client(project="YOUR_PROJECT_ID") 
        
        try:
            bucket = storage_client.get_bucket(bucket_name)
            print(f"Bucket {bucket_name} found.")
        except Exception:
            print(f"Bucket {bucket_name} not found or accessible. Attempting to create (US region)...")
            try:
                bucket = storage_client.create_bucket(bucket_name, location="US")
                print(f"Bucket {bucket_name} created.")
            except Exception as e:
                print(f"Failed to create bucket: {e}. Please ensure it exists.")
                return

        for filename in os.listdir(LOCAL_DIR):
             if filename.endswith(".txt"):
                local_path = os.path.join(LOCAL_DIR, filename)
                blob = bucket.blob(filename)
                blob.upload_from_filename(local_path)
                print(f"Uploaded {filename}")
        
        print("Upload complete!")
        
    except Exception as e:
        print(f"Error accessing GCS: {e}")
        print("Ensure GOOGLE_APPLICATION_CREDENTIALS is set or you are authenticated via 'gcloud auth application-default login'.")

if __name__ == "__main__":
    create_local_files()
    if BUCKET_NAME_ENV:
        upload_to_gcs(BUCKET_NAME_ENV)
    else:
        print("Skipping GCS upload (RAG_BUCKET_NAME not set).")
