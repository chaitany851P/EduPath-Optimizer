from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://chaitany-thakar:85173221cP@cluster0.flpifkn.mongodb.net/?appName=Cluster0"

# Create MongoDB client
client = MongoClient(uri, server_api=ServerApi('1'))

# Select database and collections
db = client.edupath_db
career_collection = db.get_collection("career_tracks")
timetable_collection = db.get_collection("timetables")

# Retrieve and print careers
print("Careers in the database:")
for career in career_collection.find():
    print(career)

# Retrieve and print timetables
print("\nTimetables in the database:")
for timetable in timetable_collection.find():
    print(timetable)
