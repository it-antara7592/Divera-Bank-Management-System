from typing import Dict, Any, List, Optional
import datetime
from db import get_db
from pymongo import ReturnDocument
from repositories.stats_repository import StatsRepository


class AccountRepository:
    """Handles all MongoDB operations for Bank Accounts."""

    @property
    def collection(self):
        return get_db()["accounts"]

    @property
    def counters(self):
        return get_db()["counters"]

    @staticmethod
    def _get_collection():
        return get_db()["accounts"]

    @staticmethod
    def get_all_accounts() -> list:
        """Fetches all account documents from MongoDB."""
        try:
            return list(AccountRepository._get_collection().find({}, {"_id": 0}))
        except Exception as e:
            print(f"[AccountRepository Error - get_all_accounts]: {e}")
            return []
        
    def generate_next_account_number(self, account_type: str, commit: bool = False) -> str:
        """
        Generates or previews an auto-incrementing Account Number.
        Format: SB100000001 or CA100000001
        :param commit: If True, increments the counter permanently. If False, only previews the next ID.
        """
        prefix = "SB" if account_type == "Savings" else "CA"
        counter_key = f"account_seq_{account_type.lower()}"
        counters = self.counters # or your collection reference

        if commit:
            # Atomically increment and lock the sequence only when saving the account
            result = counters.find_one_and_update(
                {"_id": counter_key},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            seq_number = result.get("seq", 1)
            # Ensure it starts at your base sequence (e.g., 100000001)
            if seq_number < 100000001:
                counters.update_one({"_id": counter_key}, {"$set": {"seq": 100000001}})
                seq_number = 100000001
        else:
            # Preview the next sequence value without changing the database counter
            counter_doc = counters.find_one({"_id": counter_key})
            if not counter_doc:
                seq_number = 100000001
            else:
                seq_number = counter_doc.get("seq", 100000000) + 1

        return f"{prefix}{seq_number}"

    def find_active_account_by_type(self, customer_id: str, account_type: str) -> Optional[Dict[str, Any]]:
        """Retrieves active account for a customer of a specific type."""
        if not customer_id or not account_type:
            return None

        return self.collection.find_one(
            {
                "customer_id": customer_id.strip(),
                "account_type": {"$regex": f"^{account_type.strip()}$", "$options": "i"},
                "status": "Active"
            },
            {"_id": 0}
        )

    def find_account_by_number(self, account_number: str) -> Optional[Dict[str, Any]]:
        """Retrieves an account record by account number."""
        return self.collection.find_one({"account_number": account_number.strip()}, {"_id": 0})

    def find_all_accounts_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieves all accounts (Active and Closed) belonging to a customer."""
        cursor = self.collection.find({"customer_id": customer_id.strip()}, {"_id": 0})
        return list(cursor)

    def insert_account(self, account_record: Dict[str, Any]) -> bool:
        """Inserts a new account into MongoDB with created_at and updated_at."""
        try:
            record = account_record.copy()
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            record["created_at"] = now
            record["updated_at"] = now
            record["status"] = "Active"

            result = self.collection.insert_one(record)
            return result.inserted_id is not None
        except Exception as e:
            print(f"[AccountRepository Error - insert_account]: {e}")
            return False

    def close_account(self, account_number: str) -> bool:
        """Soft-closes an active account and updates updated_at."""
        try:
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            result = self.collection.update_one(
                {"account_number": account_number.strip(), "status": "Active"},
                {
                    "$set": {
                        "status": "Closed",
                        "updated_at": now
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"[AccountRepository Error - close_account]: {e}")
            return False

    def get_account_balance(self, account_number: str) -> float:
        """Retrieves only the balance field for a specific account number."""
        try:
            record = self.collection.find_one(
                {"account_number": account_number.strip()},
                {"_id": 0, "balance": 1}
            )
            if record and "balance" in record:
                return float(record["balance"])
            return 0.0
        except Exception as e:
            print(f"[AccountRepository Error - get_account_balance]: {e}")
            return 0.0

    class DashboardService:
        @staticmethod
        def fetch_stats() -> dict:
            return StatsRepository.get_dashboard_stats()