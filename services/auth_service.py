import re
import logging
import pymongo
from typing import Optional, Dict, Any
from db import get_db
import datetime
from core.security import hash_password, verify_password

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    #Raised for authentication or verification failures.
    pass

class DatabaseConnectionError(Exception):
    #Raised for database connectivity failures.
    pass

class AuthService:
    def __init__(self):
        self.use_mock = False  # Switched to Live MongoDB connection by default

    def _get_database(self):
        try:
            return get_db()
        except Exception as e:
            raise DatabaseConnectionError("Could not connect to database server.") from e

    def validate_password_policy(self, password: str):
        #Enforces password complexity rules.
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character.")

    def login(self, username_or_id: str, password: str) -> Dict[str, Any]:
        #Authenticates a user against MongoDB.
        try:
            db = self._get_database()
            user = db["admins"].find_one({"$or": [{"username": username_or_id}, {"employee_id": username_or_id}]})
            if not user or not verify_password(password, user.get("password", "")):
                raise AuthenticationError("Invalid Username/ID or Password.")
            
            # Convert ObjectId to string or remove it to keep session dict clean if needed
            user["_id"] = str(user["_id"])
            return user
        except pymongo.errors.PyMongoError as e:
            raise DatabaseConnectionError("Database operation failed during login.") from e

    def update_admin_profile(self, username: str, new_full_name: str) -> bool:
        #Updates the admin's profile name in MongoDB.
        try:
            db = self._get_database()
            result = db["admins"].update_one(
                {"username": username},
                {"$set": {"full_name": new_full_name, "updated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except pymongo.errors.PyMongoError as e:
            raise DatabaseConnectionError("Failed to update profile in database.") from e

    def reset_admin_password(self, username: str, reset_code: str, new_password: str, confirm_password: str) -> bool:
        #Verifies reset code and updates password hash in MongoDB.
        if new_password != confirm_password:
            raise ValueError("Passwords do not match.")
        
        self.validate_password_policy(new_password)
        new_hash = hash_password(new_password)

        try:
            db = self._get_database()
            admin_col = db["admins"]

            user = admin_col.find_one({"username": username})
            if not user:
                raise AuthenticationError("Admin account not found.")

            if not verify_password(reset_code, user.get("reset_code", "")):
                raise AuthenticationError("Invalid Reset Code. Access Denied.")

            admin_col.update_one({"_id": user["_id"]}, {"$set": {"password": new_hash}})
            return True
        except pymongo.errors.PyMongoError as e:
            raise DatabaseConnectionError("Failed to update password in database.") from e

    def verify_transaction_code(self, username: str, txn_code: str) -> bool:
        #Verifies the special transaction code using bcrypt.
        try:
            db = self._get_database()

            user = db["admins"].find_one(
                {"username": username}
            )

            if not user:
                return False

            return verify_password(
                txn_code.strip(),
                user.get("passcode", "")
            )

        except Exception:
            return False