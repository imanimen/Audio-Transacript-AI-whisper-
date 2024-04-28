from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
def insert(result, file_id):
    # MongoDB connection details
    uri = os.getenv('MONGO_URL')

    # Create a new client and connect to the MongoDB server
    client = MongoClient(uri)

    # Specify the database and collection
    db = client.sounds
    collection = db.sounds_data

    # Append file_id to the result dictionary
    result['file_id'] = file_id

    # Insert the result into the collection
    collection.insert_one(result)
    client.close()
    