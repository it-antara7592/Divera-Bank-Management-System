from typing import Dict, Any, Tuple, Optional
from validations.account_validation import AccountValidation
from repositories.account_repository import AccountRepository
from repositories.customer_repository import CustomerRepository
import logging

logger = logging.getLogger(__name__)

class AccountService:
    #Enforces banking business logic for Account Management.

    def __init__(self, account_repo: Optional[AccountRepository] = None):
        self.repo = account_repo or AccountRepository()

    def get_next_account_number(self, account_type: str = "Savings") -> str:
        return self.repo.generate_next_account_number(
            account_type,
            commit=False
    )
    
    def create_account(self, payload: Dict[str, str]) -> Tuple[bool, Dict[str, str], Optional[Dict[str, Any]]]:
        """
        Executes business workflow for account creation:
        1. Input Validation
        2. Customer Existence Verification & Full Name Extraction
        3. Active Account Policy Check (1 Active Savings, 1 Active Current)
        4. Auto-generation of Account Number (atomically increments on save)
        5. Persistence to MongoDB with Overdraft Schema mapping
        """
        # Step 1: Input Validation
        is_valid, errors = AccountValidation.validate_creation(payload)
        if not is_valid:
            return False, errors, None

        customer_search_query = payload["customer_id"].strip()
        account_type = payload["account_type"].strip()

        # Step 2: Fetch Exact Customer Record from MongoDB
        customer = CustomerRepository.find_by_id_phone_or_email(customer_search_query)
        if not customer:
            return False, {"customer_id": "Customer profile not found in database."}, None

        customer_id = customer["customer_id"]
        names = [customer.get("first_name"), customer.get("middle_name"), customer.get("last_name")]
        exact_customer_name = " ".join([n.strip() for n in names if n and n.strip()])

        # Step 3: Enforce Active Account Policy
        existing_active = self.repo.find_active_account_by_type(customer_id, account_type)
        if existing_active:
            error_msg = f"Customer already has an Active {account_type} Account ({existing_active.get('account_number')})."
            return False, {"general": error_msg}, None

        # Step 4: Auto-generate Account Number (Commits sequence increment upon saving)
        account_number = self.repo.generate_next_account_number(account_type, commit=True)

        # Step 5: Construct Record Payload with Overdraft Schema
        raw_deposit = str(payload.get("initial_deposit", "0")).strip()
        deposit_amount = float(raw_deposit) if raw_deposit else 0.0
        overdraft_limit = 0.0 if account_type == "Savings" else 50000.0

        account_record = {
            "account_number": account_number,
            "customer_id": customer_id,
            "customer_name": exact_customer_name,
            "account_type": account_type,
            "opening_date": payload.get("opening_date", ""),
            "balance": deposit_amount,
            "balance_used": False,
            "overdraft": overdraft_limit,
            "status": "Active"
        }

        # Step 6: Save via Repository
        saved = self.repo.insert_account(account_record)
        if not saved:
            return False, {"general": "Database error: Failed to save account record."}, None

        return True, {}, account_record

    def close_account(self, account_number: str) -> Tuple[bool, str]:
        # Closes an active account only when the balance is exactly zero.
        account = self.repo.find_account_by_number(account_number)

        if not account:
            return False, "Account number not found."

        if account.get("status") == "Closed":
            return False, "This account is already closed."

        balance = float(account.get("balance", 0.0))

        # Positive balance → customer still has money
        if balance > 0:
            return False, (
                f"Cannot close account with remaining balance "
                f"(₹{balance:,.2f}). Withdraw funds first."
            )

        # Negative balance → outstanding overdraft
        if balance < 0:
            return False, (
                f"Cannot close account while overdraft is outstanding "
                f"(₹{abs(balance):,.2f}). Please repay the overdraft first."
            )

        # Balance is exactly zero → account can be closed
        success = self.repo.close_account(account_number)

        if success:
            return True, (
                f"Account {account_number} has been successfully closed."
            )

        return False, "Failed to close account due to a database error."

    def get_customer_active_accounts(self, customer_id: str) -> Dict[str, Optional[Dict[str, Any]]]:
        #Retrieves active accounts for GUI indicators.
        return {
            "Savings": self.repo.find_active_account_by_type(customer_id, "Savings"),
            "Current": self.repo.find_active_account_by_type(customer_id, "Current")
        }

    @staticmethod
    def get_all_accounts() -> list:
        #Retrieves all account records for directory display.
        try:
            return AccountRepository.get_all_accounts()
        except Exception as e:
            print(f"[AccountService Error - get_all_accounts]: {e}")
            return []

    def get_account_balance(self, account_number: str) -> float:
        #Retrieves live balance for a specific account number from the database.
        try:
            account = self.repo.find_account_by_number(account_number)
            if account and "balance" in account:
                return float(account["balance"])
            return 0.0
        except Exception as e:
            print(f"[AccountService Error - get_account_balance]: {e}")
            return 0.0
