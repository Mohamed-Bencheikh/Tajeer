import os
from dotenv import load_dotenv
from pymongo import MongoClient
# Load database credentials from environment variables
load_dotenv()
user = os.environ.get("ATLAS_USER")
pwd = os.environ.get("ATLAS_PWD")
db = os.environ.get("ATLAS_DB")
url = os.environ.get("ATLAS_URL")
uri = f"mongodb+srv://{user}:{pwd}@{url}"
# Connect to MongoDB Atlas
client = MongoClient(uri)
database = client.get_database(db)
users_collection = database.get_collection("users")

# for u in users_collection.find():
#     print(u["username"])


def create_user(fullname, username, email, password, role='user'):
    """
    Creates a new user in the database.
    """
    if users_collection.find_one({"email": email}):
        raise Exception("Email already in use!")

    doc = {
        "fullname": fullname,
        "username": username,
        "email": email,
        "password": password,
        "role": role
    }
    users_collection.insert_one(doc)


def fetch_all_users():
    """
    Fetches all users from the database.
    """
    users = users_collection.find()
    return dict(users)


def fetch_user(username):
    """
    Fetches a single user from the database.
    """
    user = users_collection.find_one({"username": username})
    if user:
        return user
    else:
        raise Exception("User not found!")


def update_user(username, data: dict):
    """
    Updates a single user in the database.
    """
    if users_collection.find_one({"username": username}):
        users_collection.update_one({"username": username}, {"$set": data})
        return "User updated!"
    else:
        raise Exception("User not found!")


def remove_user(username):
    """
    Removes a single user from the database.
    """
    if users_collection.find_one({"username": username}):
        users_collection.delete_one({"username": username})
        return "User removed!"
    else:
        raise Exception("User not found!")
