"""
Database Initialization & Migration Script for EduPath Optimizer
Handles:
- Database creation
- Collection indexes
- Initial data setup
- Multi-campus initialization
- Database validation
"""

import asyncio
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from backend.config import settings
from datetime import datetime
import json

# Color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


async def connect_database() -> tuple[AsyncClient, AsyncDatabase]:
    """Connect to MongoDB"""
    try:
        client = AsyncClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGODB_DATABASE]
        # Test connection
        await db.command('ping')
        print(f"{GREEN}✓ MongoDB connection successful{RESET}")
        return client, db
    except Exception as e:
        print(f"{RED}✗ MongoDB connection failed: {e}{RESET}")
        raise


async def create_collections(db: AsyncDatabase):
    """Create all required collections"""
    collections_to_create = [
        'students',
        'subjects',
        'attendance',
        'academic_performance',
        'curriculum_map',
        'campuses',
        'departments',
        'users',
    ]
    
    print(f"\n{BOLD}Creating collections...{RESET}")
    for collection_name in collections_to_create:
        try:
            if collection_name not in await db.list_collection_names():
                await db.create_collection(collection_name)
                print(f"{GREEN}✓ Created collection: {collection_name}{RESET}")
            else:
                print(f"{YELLOW}⚠ Collection already exists: {collection_name}{RESET}")
        except Exception as e:
            print(f"{RED}✗ Failed to create {collection_name}: {e}{RESET}")


async def create_indexes(db: AsyncDatabase):
    """Create database indexes for performance & uniqueness"""
    print(f"\n{BOLD}Creating indexes...{RESET}")
    
    indexes = {
        'students': [
            ([('student_id', ASCENDING)], {'unique': True}),
            ([('campus_id', ASCENDING), ('department_id', ASCENDING)], {}),
            ([('email', ASCENDING)], {}),
        ],
        'subjects': [
            ([('subject_code', ASCENDING), ('campus_id', ASCENDING)], {'unique': True}),
            ([('teacher_id', ASCENDING), ('campus_id', ASCENDING)], {}),
        ],
        'attendance': [
            ([('student_id', ASCENDING), ('subject_code', ASCENDING)], {}),
            ([('date', DESCENDING)], {}),
            ([('campus_id', ASCENDING), ('department_id', ASCENDING)], {}),
        ],
        'academic_performance': [
            ([('student_id', ASCENDING), ('subject_code', ASCENDING)], {'unique': True}),
            ([('campus_id', ASCENDING), ('department_id', ASCENDING)], {}),
        ],
        'curriculum_map': [
            ([('prerequisite_subject', ASCENDING), ('current_subject', ASCENDING)], {}),
            ([('campus_id', ASCENDING)], {}),
        ],
        'campuses': [
            ([('campus_id', ASCENDING)], {'unique': True}),
        ],
        'departments': [
            ([('department_id', ASCENDING), ('campus_id', ASCENDING)], {'unique': True}),
        ],
        'users': [
            ([('email', ASCENDING)], {'unique': True}),
            ([('campus_id', ASCENDING)], {}),
        ],
    }
    
    for collection_name, index_list in indexes.items():
        collection = db[collection_name]
        for fields, options in index_list:
            try:
                await collection.create_index(fields, **options)
                index_name = ', '.join([f[0] for f in fields])
                print(f"{GREEN}✓ {collection_name}: indexed on {index_name}{RESET}")
            except Exception as e:
                print(f"{RED}✗ Failed to create index on {collection_name}: {e}{RESET}")


async def initialize_campuses(db: AsyncDatabase):
    """Initialize campus records (for multi-campus support)"""
    print(f"\n{BOLD}Initializing campuses...{RESET}")
    
    campuses = [
        {
            'campus_id': 'CAMPUS_001',
            'name': 'Main Campus',
            'location': 'Primary Location',
            'created_at': datetime.utcnow(),
            'active': True,
        },
        {
            'campus_id': 'CAMPUS_002',
            'name': 'Extension Campus',
            'location': 'Secondary Location',
            'created_at': datetime.utcnow(),
            'active': True,
        },
    ]
    
    try:
        for campus in campuses:
            result = await db.campuses.update_one(
                {'campus_id': campus['campus_id']},
                {'$set': campus},
                upsert=True
            )
            print(f"{GREEN}✓ Campus initialized: {campus['name']}{RESET}")
    except Exception as e:
        print(f"{RED}✗ Failed to initialize campuses: {e}{RESET}")


async def initialize_departments(db: AsyncDatabase):
    """Initialize department records (for multi-department support)"""
    print(f"\n{BOLD}Initializing departments...{RESET}")
    
    departments = [
        {
            'department_id': 'DEPT_001',
            'name': 'Computer Science',
            'campus_id': 'CAMPUS_001',
            'created_at': datetime.utcnow(),
            'active': True,
        },
        {
            'department_id': 'DEPT_002',
            'name': 'Mechanical Engineering',
            'campus_id': 'CAMPUS_001',
            'created_at': datetime.utcnow(),
            'active': True,
        },
        {
            'department_id': 'DEPT_003',
            'name': 'Business Administration',
            'campus_id': 'CAMPUS_002',
            'created_at': datetime.utcnow(),
            'active': True,
        },
    ]
    
    try:
        for dept in departments:
            result = await db.departments.update_one(
                {'department_id': dept['department_id']},
                {'$set': dept},
                upsert=True
            )
            print(f"{GREEN}✓ Department initialized: {dept['name']}{RESET}")
    except Exception as e:
        print(f"{RED}✗ Failed to initialize departments: {e}{RESET}")


async def validate_database(db: AsyncDatabase) -> bool:
    """Validate database is properly initialized"""
    print(f"\n{BOLD}Validating database...{RESET}")
    
    checks = {
        'collections': ['students', 'subjects', 'attendance', 'academic_performance', 'campuses', 'departments'],
        'indexes': True,
    }
    
    all_valid = True
    
    # Check collections exist
    existing_collections = await db.list_collection_names()
    for collection in checks['collections']:
        if collection in existing_collections:
            print(f"{GREEN}✓ Collection exists: {collection}{RESET}")
        else:
            print(f"{RED}✗ Collection missing: {collection}{RESET}")
            all_valid = False
    
    # Check data
    try:
        campuses_count = await db.campuses.count_documents({})
        depts_count = await db.departments.count_documents({})
        print(f"{GREEN}✓ Data check: {campuses_count} campuses, {depts_count} departments{RESET}")
    except Exception as e:
        print(f"{RED}✗ Data validation failed: {e}{RESET}")
        all_valid = False
    
    return all_valid


async def print_summary(db: AsyncDatabase):
    """Print initialization summary"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Database Initialization Summary{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    try:
        collections = await db.list_collection_names()
        print(f"\n{BLUE}Collections ({len(collections)}){RESET}:")
        for col in sorted(collections):
            count = await db[col].count_documents({})
            print(f"  • {col}: {count} documents")
        
        print(f"\n{BLUE}Campuses{RESET}:")
        async for campus in db.campuses.find():
            print(f"  • {campus['name']} ({campus['campus_id']})")
        
        print(f"\n{BLUE}Departments{RESET}:")
        async for dept in db.departments.find():
            print(f"  • {dept['name']} ({dept['department_id']}) - Campus: {dept['campus_id']}")
        
        print(f"\n{GREEN}{BOLD}✓ Database initialized successfully!{RESET}")
    except Exception as e:
        print(f"{RED}✗ Error printing summary: {e}{RESET}")


async def main():
    """Main initialization function"""
    print(f"\n{BOLD}{BLUE}{'='*60}")
    print(f"EduPath Optimizer - Database Initialization")
    print(f"{'='*60}{RESET}\n")
    
    print(f"Configuration:")
    print(f"  Database: {settings.MONGODB_DATABASE}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  University: {settings.UNIVERSITY_NAME}")
    print(f"  Multi-Campus: {settings.ENABLE_MULTI_CAMPUS}")
    
    client = None
    try:
        client, db = await connect_database()
        
        # Initialize database
        await create_collections(db)
        await create_indexes(db)
        await initialize_campuses(db)
        await initialize_departments(db)
        
        # Validate
        is_valid = await validate_database(db)
        
        # Print summary
        await print_summary(db)
        
        if is_valid:
            print(f"\n{GREEN}{BOLD}Status: READY FOR DEPLOYMENT ✓{RESET}")
        else:
            print(f"\n{YELLOW}{BOLD}Status: SETUP COMPLETED WITH WARNINGS ⚠{RESET}")
        
    except Exception as e:
        print(f"\n{RED}{BOLD}Initialization failed: {e}{RESET}")
        exit(1)
    finally:
        if client:
            client.close()
            print(f"\n{BLUE}Database connection closed{RESET}")


if __name__ == "__main__":
    asyncio.run(main())
