import os
import random
import shutil

# Constants
LOCAL_DIR = "rag_data"

# Mock Data Lists
CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", 
    "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", 
    "San Francisco", "Charlotte", "Indianapolis", "Seattle", "Denver", "Washington"
]

PRODUCTS = [
    "Flights", "Hotels", "Rental Cars", "Vacation Packages"
]

FAQ_TEMPLATES = [
    {"q": "What is the cancellation policy for {product}?", "a": "You can cancel any {product} booking within 24 hours for a full refund. After that, standard cancellation fees apply depending on the carrier or property."},
    {"q": "How early should I arrive for {product} in {city}?", "a": "For {product} in {city}, we recommend arriving at least 2 hours before your scheduled time to ensure a smooth check-in process."},
    {"q": "Do you offer travel insurance for {product}?", "a": "Yes, we offer comprehensive travel insurance for {product} that covers cancellations, medical emergencies, and lost luggage."},
    {"q": "Can I modify my {product} reservation?", "a": "Yes, modifications to {product} are allowed up to 48 hours before the trip, subject to availability and fare differences."},
    {"q": "Is there a loyalty program for regular travelers?", "a": "Absolutely! Join Cymbal Travel Rewards to earn points on every {product} booking, regardless of the destination."}, 
    {"q": "What payment methods do you accept for {product}?", "a": "We accept all major credit cards, PayPal, and Cymbal Pay for all {product} bookings."},
    {"q": "Are there family discounts for {product} to {city}?", "a": "We often have special family packages for {product} to popular destinations like {city}. Check our 'Deals' page for current offers."},
    {"q": "How do I get my boarding pass or ticket for {product}?", "a": "Your digital boarding pass or ticket for {product} will be emailed to you immediately after confirmation and is also available in the Cymbal Travel app."},
    {"q": "Who do I contact if I have issues with my {product} in {city}?", "a": "Our 24/7 support team is available to help with any issues regarding your {product} in {city}. Call us or chat via the app."},
    {"q": "Do you offer group booking rates for {product}?", "a": "Yes, for groups of 10 or more, we offer special group rates for {product}. Please contact our group travel department."}
]

def create_local_rag_data():
    """Generates mock RAG data files locally."""
    if os.path.exists(LOCAL_DIR):
        shutil.rmtree(LOCAL_DIR)
    os.makedirs(LOCAL_DIR)

    print(f"Generating RAG data in {LOCAL_DIR}...")

    # Generate 50 FAQs
    for i in range(1, 51):
        template = random.choice(FAQ_TEMPLATES)
        product = random.choice(PRODUCTS)
        city = random.choice(CITIES)
        
        question = template["q"].format(product=product, city=city)
        answer = template["a"].format(product=product, city=city)
        
        content = f"Question: {question}\nAnswer: {answer}"
        
        with open(f"{LOCAL_DIR}/faq{i}.txt", "w") as f:
            f.write(content)
            
    # Generate About Us
    with open(f"{LOCAL_DIR}/about_us.txt", "w") as f:
        f.write("About Cymbal Travel\n\nCymbal Travel is a premier digital travel agency dedicated to making your travel dreams a reality. From flights and hotels to car rentals and vacation packages, we provide a seamless booking experience. Founded in 2015, we have served over 1 million happy travelers worldwide.")

    # Generate Cancellation Policy
    with open(f"{LOCAL_DIR}/cancellation_policy.txt", "w") as f:
        f.write("Cymbal Travel Cancellation Policy\n\n1. 24-Hour Free Cancellation: All bookings can be cancelled within 24 hours of purchase for a full refund.\n2. Flights: After 24 hours, airline rules apply. Non-refundable tickets may receive travel credit.\n3. Hotels: Cancellations made less than 48 hours before check-in may incur a one-night charge.\n4. Cars: Prepaid rentals are refundable up to 48 hours before pick-up.\n5. Refunds are processed within 5-7 business days.")

    # Generate Locations
    with open(f"{LOCAL_DIR}/destinations.txt", "w") as f:
        f.write("Popular Destinations we serve:\n" + "\n".join(CITIES))

    print("RAG data generation complete.")

if __name__ == "__main__":
    create_local_rag_data()
