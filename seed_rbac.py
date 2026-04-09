from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://chaitany-thakar:85173221cP@cluster0.flpifkn.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.edupath_db
users_collection = db.get_collection("users")

def seed_users():
    # Clear existing users
    users_collection.delete_many({})
    
    users = [
        {
            "username": "admin1",
            "password": "123", # In real apps, we hash this
            "role": "admin",
            "name": "Project Admin"
        },
        {
            "username": "teacher1",
            "password": "123",
            "role": "teacher",
            "name": "Prof. Sharma"
        },
        {
            "username": "2024001",
            "password": "123",
            "role": "student",
            "name": "Chaitany Thakar",
            "career_track": "Data Science",
            "attended": 5
        }
    ]
    
    users_collection.insert_many(users)
    print("✅ RBAC Users Seeded: admin1, teacher1, 2024001 (Pass: 123)")

if __name__ == "__main__":
    seed_users()