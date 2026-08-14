from typing import Dict, Any, Optional
import datetime

from db import get_db


class TransactionRepository:
    """Handles MongoDB operations for fund transfers."""

    @property
    def collection(self):
        return get_db()["transactions"]

    @property
    def counters(self):
        return get_db()["counters"]

    # =========================================================
    # ACCOUNT OPERATIONS
    # =========================================================

    def get_account(
        self,
        account_number: str
    ) -> Optional[Dict[str, Any]]:

        if not account_number:
            return None

        return get_db()["accounts"].find_one(
            {
                "account_number": account_number.strip()
            },
            {
                "_id": 0
            }
        )

    def update_account_balance(
        self,
        account_number: str,
        new_balance: float
    ) -> bool:

        result = get_db()["accounts"].update_one(
            {
                "account_number": account_number.strip()
            },
            {
                "$set": {
                    "balance": float(new_balance),
                    "updated_at": datetime.datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            }
        )

        return result.modified_count > 0

    def mark_overdraft_used(
        self,
        account_number: str
    ) -> bool:

        result = get_db()["accounts"].update_one(
            {
                "account_number": account_number.strip()
            },
            {
                "$set": {
                    "overdraft_used": True,
                    "updated_at": datetime.datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            }
        )

        return result.modified_count > 0

    # =========================================================
    # TRANSACTION ID
    # =========================================================

    def generate_transaction_id(self) -> str:
        """
        Generates a sequential transaction ID.

        Example:
        TX100000001
        TX100000002
        """

        counter_key = "transaction_seq"

        result = self.counters.find_one_and_update(
            {
                "_id": counter_key
            },
            {
                "$inc": {
                    "seq": 1
                }
            },
            upsert=True,
            return_document=True
        )

        seq_number = result.get("seq", 1)

        if seq_number < 100000001:

            self.counters.update_one(
                {
                    "_id": counter_key
                },
                {
                    "$set": {
                        "seq": 100000001
                    }
                }
            )

            seq_number = 100000001

        return f"TX{seq_number}"

    # =========================================================
    # TRANSACTION LOG
    # =========================================================

    def insert_transaction(
        self,
        transaction_record: Dict[str, Any]
    ) -> bool:

        try:

            now = datetime.datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            record = transaction_record.copy()

            record["created_at"] = now
            record["updated_at"] = now

            result = self.collection.insert_one(record)

            return result.inserted_id is not None

        except Exception as e:

            print(
                f"[TransactionRepository Error - "
                f"insert_transaction]: {e}"
            )

            return False

    def get_transaction_by_id(
        self,
        transaction_id: str
    ) -> Optional[Dict[str, Any]]:

        return self.collection.find_one(
            {
                "transaction_id": transaction_id
            },
            {
                "_id": 0
            }
        )

    def log_failed_withdrawal_attempt(
        self,
        account_number: str,
        amount: str,
        reason: str
    ) -> bool:
        """Logs a failed withdrawal attempt for auditing purposes."""
        try:
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            record = {
                "transaction_type": "WITHDRAWAL_FAILED",
                "account_number": account_number.strip() if account_number else "",
                "amount": amount.strip() if amount else "",
                "reason": reason,
                "created_at": now,
                "updated_at": now
            }
            result = self.collection.insert_one(record)
            return result.inserted_id is not None
        except Exception as e:
            print(
                f"[TransactionRepository Error - "
                f"log_failed_withdrawal_attempt]: {e}"
            )
            return False

    def reset_overdraft_status(
        self,
        account_number: str
    ) -> bool:

        result = get_db()["accounts"].update_one(
            {
                "account_number": account_number.strip()
            },
            {
                "$set": {
                    "overdraft_used": False,
                    "updated_at": datetime.datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            }
        )

        return result.modified_count > 0

    def log_failed_deposit_attempt(
        self,
        account_number: str,
        amount: str,
        reason: str
    ) -> bool:
        """Logs a failed deposit attempt for auditing purposes."""
        try:
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            record = {
                "transaction_type": "DEPOSIT_FAILED",
                "account_number": account_number.strip() if account_number else "",
                "amount": amount.strip() if amount else "",
                "reason": reason,
                "created_at": now,
                "updated_at": now
            }
            result = self.collection.insert_one(record)
            return result.inserted_id is not None
        except Exception as e:
            print(
                f"[TransactionRepository Error - "
                f"log_failed_deposit_attempt]: {e}"
            )
            return False

    def get_all_transactions(self) -> list:
        """Retrieves all permanent transaction records sorted by creation date descending."""
        try:
            return list(
                self.collection.find(
                    {},
                    {"_id": 0}
                ).sort("created_at", -1)
            )
        except Exception as e:
            print(f"[TransactionRepository Error - get_all_transactions]: {e}")
            return []