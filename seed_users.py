"""
Seed Script for Users and Authentication
Creates users collection with test credentials
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import secrets

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "edupath_db")


def hash_password(password: str) -> str:
    """Hash a password using SHA256 with salt"""
    salt = os.urandom(16).hex()
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(password: str, hash_str: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hash_hex = hash_str.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False


async def seed_users():
    """Seed users collection with test credentials"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🌱 Seeding Users Collection...\n")
    
    # Clear existing users
    await db.users.delete_many({})
    
    # Test user data
    users_data = [
        # Students
        {
            "user_id": "2024001",
            "username": "2024001",
            "password_hash": hash_password("student123"),
            "name": "Rajesh Kumar",
            "email": "rajesh.kumar@university.edu",
            "role": "student",
            "department": "CE",
            "semester": 2,
            "created_at": datetime.utcnow(),
            "last_login": None
        },
        {
            "user_id": "2024002",
            "username": "2024002",
            "password_hash": hash_password("student123"),
            "name": "Priya Singh",
            "email": "priya.singh@university.edu",
            "role": "student",
            "department": "IT",
            "semester": 2,
            "created_at": datetime.utcnow(),
            "last_login": None
        },
        {
            "user_id": "2024003",
            "username": "2024003",
            "password_hash": hash_password("student123"),
            "name": "Amit Patel",
            "email": "amit.patel@university.edu",
            "role": "student",
            "department": "EC",
            "semester": 2,
            "created_at": datetime.utcnow(),
            "last_login": None
        },
        # Teachers
        {
            "user_id": "T001",
            "username": "teacher01",
            "password_hash": hash_password("teacher123"),
            "name": "Dr. Sharma",
            "email": "sharma@university.edu",
            "role": "teacher",
            "department": "CE",
            "created_at": datetime.utcnow(),
            "last_login": None
        },
        {
            "user_id": "T002",
            "username": "teacher02",
            "password_hash": hash_password("teacher123"),
            "name": "Prof. Desai",
            "email": "desai@university.edu",
            "role": "teacher",
            "department": "IT",
            "created_at": datetime.utcnow(),
            "last_login": None
        },
        # Admin
        {
            "user_id": "ADMIN001",
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "name": "System Admin",
            "email": "admin@university.edu",
            "role": "admin",
            "created_at": datetime.utcnow(),
            "last_login": None
        }
    ]
    
    # Insert users
    result = await db.users.insert_many(users_data)
    print(f"✓ Inserted {len(result.inserted_ids)} users")
    print("\n📋 TEST USER CREDENTIALS:\n")
    print("=" * 60)
    print("STUDENTS:")
    print("  • Username: 2024001  | Password: student123")
    print("  • Username: 2024002  | Password: student123")
    print("  • Username: 2024003  | Password: student123")
    print("\nTEACHERS:")
    print("  • Username: teacher01 | Password: teacher123")
    print("  • Username: teacher02 | Password: teacher123")
    print("\nADMIN:")
    print("  • Username: admin    | Password: admin123")
    print("=" * 60)
    
    client.close()
    print("\n✅ User seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_users())
