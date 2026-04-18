from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "edupath_db")

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    # Create indexes - Phase 1
    await db.students.create_index("student_id", unique=True)
    await db.attendance.create_index([("student_id", 1), ("subject_code", 1), ("date", 1)])
    await db.subjects.create_index("subject_code", unique=True)
    # Create indexes - Phase 2 & 3
    await db.academic_performance.create_index([("student_id", 1), ("subject_code", 1)])
    await db.curriculum_map.create_index([("prerequisite_code", 1), ("current_code", 1)])
    print(f"Connected to MongoDB: {DB_NAME}")

async def disconnect_db():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_db():
    return db
