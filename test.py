import os
from enum import Enum

from pymongo import MongoClient


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
# Load database credentials from environment variables
user = os.environ.get("ATLAS_USER")
pwd = os.environ.get("ATLAS_PWD")
db = os.environ.get("ATLAS_DB") 
uri = f"mongodb+srv://{user}:{pwd}@cluster0.koz4qat.mongodb.net/test?retryWrites=true&w=majority"

# Connect to MongoDB Atlas
client = MongoClient(uri)

database = client.get_database(db)
users_collection = database.get_collection("users")
# get the user with the username: "medbc"
u = users_collection.find_one({"username": "medbc"})
print(u)