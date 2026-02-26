import os
from dotenv import load_dotenv

load_dotenv()

# Google Cloud Configuration
# In Cloud Run, Service Account is auto-detected. Locally, set this path.
# Example: /Users/doug/gcloud-keys/my-service-account.json
# If not set, it will look for default credentials.
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Service URL Configuration
# Used in OpenAPI spec for agents to know where to call
SERVICE_URL = os.getenv("SERVICE_URL", "http://localhost:8080")
SERVICE_NAME = "Cymbal Travel Mock API"

# Project ID (Optional check)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcloud-interactive-courses")
try:
    if not PROJECT_ID:
        import subprocess
        PROJECT_ID = subprocess.check_output(["gcloud", "config", "get-value", "project"], text=True).strip()
except Exception:
    pass

# Cloud Storage Bucket
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "cymbal-travel-images-dar")
BASE_IMAGE_URL = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}"

# Agent Engine Configuration
AGENT_ENGINE_RESOURCE_ID = os.getenv("AGENT_ENGINE_RESOURCE_ID", "4329730555135393792")
AGENT_LOCATION = os.getenv("AGENT_LOCATION", "us-central1")


def configure_environment():
    """
    Sets up environment variables if they are not already set.
    """
    if GOOGLE_APPLICATION_CREDENTIALS:
        print(f"Setting credentials from config: {GOOGLE_APPLICATION_CREDENTIALS}")
        # This is required for the google-cloud-firestore library to pick it up
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
    
    # Other setup if needed
    print(f"Service URL configured as: {SERVICE_URL}")

# Execute configuration
configure_environment()
