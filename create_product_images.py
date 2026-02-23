import os
import time
from dotenv import load_dotenv
from google.cloud import storage
from google import genai
from google.genai import types

load_dotenv()

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("GCS_IMAGE_BUCKET", "cymbal-travel-images-dar")
MODEL_NAME = "gemini-2.5-flash-image"

# Define the car inventory manually essentially matching app/database.py
CARS = [
    {"id": "economy", "title": "Cymbal Rentals Compact", "description": "Fuel efficient and compact white economy car", "category": "Economy Car"},
    {"id": "sedan", "title": "Cymbal Rentals Comfort", "description": "Comfortable silver 4-door sedan", "category": "Sedan"},
    {"id": "suv", "title": "Cymbal Rentals Explorer", "description": "Spacious blue SUV family car", "category": "SUV"},
    {"id": "sports", "title": "Cymbal Rentals Racer", "description": "Sleek red sports car", "category": "Sports Car"},
    {"id": "luxury", "title": "Cymbal Rentals S-Class", "description": "Black luxury sedan, shiny, elegant", "category": "Luxury Car"},
    {"id": "pickup", "title": "Cymbal Rentals Hauler", "description": "Rugged grey pickup truck", "category": "Pickup Truck"}
]

def generate_image(client, prompt, output_file):
    return_code = False
    max_retries = 5
    delay = 2  # Initial delay
    
    for attempt in range(max_retries):
        try:
            print(f"Generating image for prompt: {prompt[:50]}... (Attempt {attempt+1}/{max_retries})")
            
            # Application of the google-genai SDK for image generation
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
            
            # Handle response to save image bytes
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data:
                                with open(output_file, "wb") as f:
                                    f.write(part.inline_data.data)
                                print(f"Saved local image: {output_file}")
                                return True
            
            print(f"No image data found in response.")
            return False

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                print(f"Rate limit hit (429). Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"Error generating image: {e}")
                return False
                
    print("Max retries exceeded for image generation.")
    return False

def upload_to_gcs(bucket, source_file_name, destination_blob_name):
    # Uploads a file to the bucket.
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    
    # Optional: Make public if your bucket allows it
    try:
        blob.make_public()
    except:
        pass
        
    print(f"File {source_file_name} uploaded to gs://{bucket.name}/{destination_blob_name}")

def main():
    print(f"Initializing Gen AI Client for project: {PROJECT_ID}, location: {LOCATION}")
    
    # Initialize the Gen AI client with Vertex AI enabled
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    
    # Initialize GCS
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
            print(f"Found bucket: {BUCKET_NAME}")
        except Exception:
            print(f"Bucket {BUCKET_NAME} not found. Creating it...")
            bucket = storage_client.create_bucket(BUCKET_NAME, location="US")
            print(f"Created bucket: {BUCKET_NAME}")
    except Exception as e:
        print(f"Could not initialize GCS client: {e}")
        return

    # Create temp dir
    os.makedirs("generated_images", exist_ok=True)
    
    for item in CARS:
        sku = item['id']
        title = item['title']
        description = item['description']
        category = item['category']
        
        # Prompt Engineering
        prompt = f"Professional studio product photography of a {title}. {description}. The item is a high-quality rental vehicle ({category}). Clean white background, 4k, ultra-realistic, photorealistic, commercial car photography."
        
        local_filename = f"generated_images/{sku}.jpg"
        gcs_filename = f"{sku}.jpg"
        
        # Check if exists in GCS
        blob = bucket.blob(gcs_filename)
        if blob.exists():
            print(f"Image {gcs_filename} already exists in GCS. Skipping.")
            continue
            
        # Generate & Upload
        if generate_image(client, prompt, local_filename):
            upload_to_gcs(bucket, local_filename, gcs_filename)
            
        # Rate limiting
        time.sleep(2)

    print("\nImage generation complete! Check your GCS bucket.")

if __name__ == "__main__":
    main()
