import os
import time
import sys
from google.cloud import storage
from google import genai
from google.genai import types

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from app import database

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"
BUCKET_NAME = "cymbal-travel-images-dar"
MODEL_NAME = "gemini-2.5-flash-image"

def generate_image(client, prompt, output_file):
    max_retries = 3
    delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Generating image for prompt: {prompt[:60]}... (Attempt {attempt+1}/{max_retries})")
            
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
                    ],
                )
            )
            
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data:
                                with open(output_file, "wb") as f:
                                    f.write(part.inline_data.data)
                                print(f"Saved local image: {output_file}")
                                return True
            
            print(f"No image data found.")
            return False

        except Exception as e:
            if "429" in str(e) or "Resource exhausted" in str(e):
                print(f"Rate limit hit (429). Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error generating image: {e}")
                return False
                
    return False

def upload_to_gcs(bucket, source_file_name, destination_blob_name):
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    try:
        blob.make_public()
    except:
        pass
    print(f"Uploaded to gs://{bucket.name}/{destination_blob_name}")

def main():
    if not database.db:
        print("Database not initialized.")
        return

    print(f"Initializing Gen AI Client: {PROJECT_ID}, {LOCATION}")
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    storage_client = storage.Client(project=PROJECT_ID)
    try:
        bucket = storage_client.get_bucket(BUCKET_NAME)
    except Exception:
        bucket = storage_client.create_bucket(BUCKET_NAME, location="US")

    os.makedirs("generated_images", exist_ok=True)
    
    # Fetch all hotels
    hotels_ref = database.db.collection(database.COL_HOTELS)
    docs = hotels_ref.stream()
    
    # Collect all tasks to process sequentially to avoid rate limits
    # Structure: (filename, prompt)
    tasks = []

    for doc in docs:
        hotel = doc.to_dict()
        loc = hotel['location']
        name = hotel['property_name']
        desc = hotel['description']
        
        # 1. Resort Image
        # URL format in DB: .../resort-bali-indonesia.jpg
        # Extract filename from URL
        resort_img_url = hotel['image_url']
        resort_filename = resort_img_url.split('/')[-1]
        
        resort_prompt = f"Professional travel photography of {name} in {loc}. {desc}. Luxury resort exterior, sunny day, blue sky, 4k, photorealistic, architectural digest style."
        tasks.append((resort_filename, resort_prompt))
        
        # 2. Room Images
        # Room URL format: .../resort-bali-indonesia-standard.jpg
        rooms = hotel.get('rooms', [])
        for room in rooms:
            room_type = room['room_type']
            room_desc = room['description']
            room_img_url = room['image_url']
            room_filename = room_img_url.split('/')[-1]
            
            room_prompt = f"Professional interior design photography of a {room_type} at {name} in {loc}. {room_desc}. Luxury hotel room, clean, bright, 4k, photorealistic."
            tasks.append((room_filename, room_prompt))

    print(f"Found {len(tasks)} images to generate/check.")
    
    for filename, prompt in tasks:
        local_path = f"generated_images/{filename}"
        
        # Check if exists in GCS
        blob = bucket.blob(filename)
        if blob.exists():
            print(f"Skipping {filename} (already exists in GCS).")
            continue
            
        print(f"Processing {filename}...")
        if generate_image(client, prompt, local_path):
            upload_to_gcs(bucket, local_path, filename)
            # Sleep to respect rate limits
            time.sleep(2) 
        else:
            print(f"Failed to generate {filename}. Skipping.")

    print("\nHotel image generation complete!")

if __name__ == "__main__":
    main()
