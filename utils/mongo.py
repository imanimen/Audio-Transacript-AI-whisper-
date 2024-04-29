from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
"""
Inserts a document into the 'sounds_data' collection in the 'sounds' database.

Args:
    result (dict): A dictionary containing the data to be inserted.
    file_id (str): The ID of the file associated with the data.

Returns:
    None
"""
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
    

"""
Uploads a file to the MongoDB database.

Args:
    path (str): The file path to be uploaded.

Returns:
    None
"""
def uploadFile(path):
    # MongoDB connection details
    mongo_url = os.getenv("MONGO_URL")

    # Create a new client and connect to the MongoDB server
    client = MongoClient(mongo_url)

    # Specify the database and collection
    database_name = "service_files"  # Specify your desired database name
    collection_name = "service_files"  # Specify your desired collection name

    db = client[database_name]
    collection = db[collection_name]

    # Create a document to insert
    document = {"path": path}

    # Insert the document into the collection
    collection.insert_one(document)    