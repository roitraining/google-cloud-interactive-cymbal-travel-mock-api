import sys
import os
from google.cloud import firestore

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

from app import database

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.to_dict()}")
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def reset_cars():
    if not database.db:
        print("Database not initialized.")
        return

    print("Deleting existing car inventory...")
    cars_ref = database.db.collection(database.COL_CARS)
    delete_collection(cars_ref, 10)
    print("Deleted all cars.")

    print("Re-saving inventory...")
    database.save_inventory()
    print("Done.")

if __name__ == "__main__":
    reset_cars()
