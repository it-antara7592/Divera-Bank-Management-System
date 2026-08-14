from typing import Dict, Any, Optional
import datetime
import re
from db import get_db
from pymongo import ReturnDocument


class CustomerRepository:
    """Handles all MongoDB operations for Customer profiles."""

    @staticmethod
    def _get_collection():
        return get_db()["customers"]

    @staticmethod
    def _get_counters_collection():
        return get_db()["counters"]

    @staticmethod
    def generate_next_customer_id(commit: bool = False) -> str:
        """
        Generates or previews an auto-incrementing Customer ID.
        Format: CUST-YYYY-XXXXXX (e.g., CUST-2026-000101)
        :param commit: If True, increments the counter permanently. If False, only previews the next ID.
        """
        current_year = datetime.datetime.now().year
        counter_id = f"customer_id_{current_year}"
        counters = CustomerRepository._get_counters_collection()

        if commit:
            # Atomically increment and lock the sequence only when saving
            result = counters.find_one_and_update(
                {"_id": counter_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            seq_number = result.get("seq", 1)
            if seq_number < 101:
                counters.update_one({"_id": counter_id}, {"$set": {"seq": 101}})
                seq_number = 101
        else:
            # Preview the next sequence value without incrementing the database counter
            counter_doc = counters.find_one({"_id": counter_id})
            if not counter_doc:
                seq_number = 101
            else:
                seq_number = counter_doc.get("seq", 100) + 1

        return f"CUST-{current_year}-{seq_number:06d}"

    @staticmethod
    def exists_by_email(email: str) -> bool:
        """Checks if a customer exists with the given email address (case-insensitive)."""
        if not email or not email.strip():
            return False
        clean_email = email.strip()
        safe_email = re.escape(clean_email)
        doc = CustomerRepository._get_collection().find_one(
            {"email": {"$regex": f"^{safe_email}$", "$options": "i"}}
        )
        return doc is not None

    @staticmethod
    def exists_by_government_id(gov_id_number: str) -> bool:
        """Checks if a customer exists with the given Government ID number."""
        if not gov_id_number or not gov_id_number.strip():
            return False
        doc = CustomerRepository._get_collection().find_one(
            {"government_id_number": gov_id_number.strip()}
        )
        return doc is not None

    @staticmethod
    def exists_by_phone(phone: str) -> bool:
        """Checks if a customer exists with the given phone number."""
        if not phone or not phone.strip():
            return False
        doc = CustomerRepository._get_collection().find_one(
            {"phone": phone.strip()}
        )
        return doc is not None

    @staticmethod
    def insert_customer(data: Dict[str, Any]) -> Optional[str]:
        """
        Inserts a new customer record into MongoDB with created_at and updated_at.
        Returns customer_id on success, None on failure.
        """
        try:
            record = data.copy()
            
            # Commit and officially claim the next sequential ID upon actual insertion
            if not record.get("customer_id") or record.get("customer_id").startswith("CUST-"):
                record["customer_id"] = CustomerRepository.generate_next_customer_id(commit=True)

            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            record["created_at"] = now
            record["updated_at"] = now
            record["status"] = "Active"

            result = CustomerRepository._get_collection().insert_one(record)
            if result.inserted_id:
                return record.get("customer_id")
            return None
        except Exception as e:
            print(f"[CustomerRepository Error - insert_customer]: {e}")
            return None

    @staticmethod
    def find_by_id_phone_or_email(query: str) -> Optional[Dict[str, Any]]:
        """
        Search helper to look up active customers by Customer ID, Phone Number, or Email.
        Safely escapes special regex characters and enforces Active status.
        """
        if not query or not str(query).strip():
            return None

        clean_query = str(query).strip()
        safe_query = re.escape(clean_query)
        collection = CustomerRepository._get_collection()

        search_filter = {
            "$and": [
                {
                    "$or": [
                        {"customer_id": {"$regex": f"^{safe_query}$", "$options": "i"}},
                        {"phone": {"$regex": f"^{safe_query}$", "$options": "i"}},
                        {"email": {"$regex": f"^{safe_query}$", "$options": "i"}}
                    ]
                },
                {"status": {"$regex": "^Active$", "$options": "i"}}
            ]
        }

        return collection.find_one(search_filter, {"_id": 0})

    @staticmethod
    def get_all_customers() -> list:
        """Fetches all customer documents from MongoDB."""
        try:
            return list(CustomerRepository._get_collection().find({}, {"_id": 0}))
        except Exception as e:
            print(f"[CustomerRepository Error - get_all_customers]: {e}")
            return []

    @staticmethod
    def update_customer(customer_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates an existing customer record in MongoDB by customer_id."""
        try:
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            update_data["updated_at"] = now
            result = CustomerRepository._get_collection().update_one(
                {"customer_id": customer_id},
                {"$set": update_data}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"[CustomerRepository Error - update_customer]: {e}")
            return False