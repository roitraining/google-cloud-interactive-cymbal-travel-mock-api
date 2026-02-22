import sys
import os

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from app import database

print("Saving inventory...")
try:
    if database.save_inventory():
        print("Inventory saved successfully.")
    else:
        print("Inventory save failed (maybe DB not initialized).")
except Exception as e:
    print(f"Error: {e}")
