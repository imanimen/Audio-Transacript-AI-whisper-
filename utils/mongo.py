from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB connection details
mongo_url = os.getenv("MONGO_URL")

# Create a MongoDB client and connect to the server
client = MongoClient(mongo_url)

"""
Inserts a document into the 'sounds_data' collection in the 'sounds' database.

Args:
    result (dict): A dictionary containing the data to be inserted.
    file_id (str): The ID of the file associated with the data.

Returns:
    None
"""
def insert(result, file_id):
    # Specify the database and collection
    db = client.sounds
    collection = db.sounds_data

    # Append file_id to the result dictionary
    result['file_id'] = file_id

    # Insert the result into the collection
    collection.insert_one(result)

"""
Uploads a file to the MongoDB database.

Args:
    path (str): The file path to be uploaded.

Returns:
    None
"""
def uploadFile(path):
    # Specify the database and collection
    database_name = "service_files"  # Specify your desired database name
    collection_name = "service_files"  # Specify your desired collection name

    db = client[database_name]
    collection = db[collection_name]

    # Create a document to insert
    document = {"path": path}

    # Insert the document into the collection
    collection.insert_one(document)