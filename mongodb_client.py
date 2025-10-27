from pymongo import MongoClient
from datetime import datetime
import certifi 

MONGO_URI = "mongodb://localhost:27017/" 

DB_NAME = "stock_predictor_db"
COLLECTION_NAME = "predictions"

try:
    #Timeout to detect failure quickly
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping') 
except Exception as e:
    print(f"Error initializing MongoClient: {e}")
    client = None

if client:
    db = client.get_database(DB_NAME) 
    predictions_collection = db[COLLECTION_NAME] 
else:
    predictions_collection = None 


def test_connection():
    if not client:
        return False
        
    try:
        client.admin.command('ping')
        print(f"--- Local MongoDB Connection Successful to {DB_NAME} ---")
        if COLLECTION_NAME not in db.list_collection_names():
             db.create_collection(COLLECTION_NAME)
             print(f"--- Collection '{COLLECTION_NAME}' created. ---")
        return True

    except Exception as e:
        print(f"--- Error during connection test: {e} ---")
        return False

if __name__ == '__main__':
    test_connection()