import sys
import os

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from app import database


if __name__ == "__main__":
    print("Initializing inventory (Resorts & Cars)...")
    if database.save_inventory():
       print("Done.")
    else:
       print("Failed to initialize database.")
