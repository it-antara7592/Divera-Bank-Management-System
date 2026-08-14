import os
import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

# Database connection setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)

# Database instance
db = client["divera_bank_db"]

# Common Collections
customers_collection = db["customers"]
accounts_collection = db["accounts"]
admins_collection = db["admins"]
counters_collection = db["counters"]
transactions_collection = db["transactions"]

def get_database():
    """Returns the database instance and ensures indexes/seeding run on first load."""
    _init_database(db)
    return db


# Alias for compatibility with existing imports
get_db = get_database

def _init_database(database):
    #Initializes indexes and seeds the initial admin profile if empty.
    try:
        # 1. Customers Collection Indexes
        database["customers"].create_index([("customer_id", ASCENDING)], unique=True)
        database["customers"].create_index([("email", ASCENDING)], unique=True, sparse=True)
        database["customers"].create_index([("phone", ASCENDING)], unique=True, sparse=True)
        database["customers"].create_index([("government_id_number", ASCENDING)], unique=True, sparse=True)

        # 2. Accounts Collection Indexes
        database["accounts"].create_index([("account_number", ASCENDING)], unique=True)
        database["accounts"].create_index([("customer_id", ASCENDING), ("account_type", ASCENDING), ("status", ASCENDING)])

        # 3. Admins Collection Indexes & Seeding
        database["admins"].create_index([("username", ASCENDING)], unique=True)
        database["admins"].create_index([("employee_id", ASCENDING)], unique=True, sparse=True)

        # 3. Transaction Collection Indexes
        database["transactions"].create_index([("transaction_id", ASCENDING)],unique=True)
        database["transactions"].create_index([("from_account", ASCENDING)])
        database["transactions"].create_index([("to_account", ASCENDING)])
        database["transactions"].create_index([("created_at", ASCENDING)])
        database["transactions"].create_index([("transaction_type", ASCENDING)])
        database["transactions"].create_index([("status", ASCENDING)])

        if database["admins"].count_documents({}) == 0:
            from core.security import hash_password
            default_admin = {
                "username": "admin",
                "employee_id": "EMP1001",
                "email": "admin@diverabank.com",
                "full_name": "Diya Sharma",
                "role": "Bank Operator",
                "department": "Accounts & Transactions",
                "password": hash_password("1234"),
                "reset_code": hash_password("DBMS-RESET-2026"),
                "passcode": hash_password("7777"),
                "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            database["admins"].insert_one(default_admin)
            print("[DB Initialization]: Default admin profile seeded successfully.")

    except PyMongoError as e:
        print(f"[DB Initialization Warning]: Could not set up indexes/seeding: {e}")