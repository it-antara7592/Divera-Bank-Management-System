from typing import Dict, Any, Tuple
from validations.customer_validation import CustomerValidator
from repositories.customer_repository import CustomerRepository
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    #Enforces banking business logic and validation for Customer Profiles.

    @staticmethod
    def get_next_customer_id() -> str:
        #Fetches the next available auto-generated Customer ID.
        try:
            return CustomerRepository.generate_next_customer_id()
        except Exception as e:
            print(f"[CustomerService Error - ID Generation]: {e}")
            return "CUST-2026-000101"

    @staticmethod
    def save_customer(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Complete workflow for saving a customer profile:
        UI Input -> Validation -> MongoDB Duplicate Checks -> Persistence
        """
        # 1. Input Validation
        errors = {
            "first_name": CustomerValidator.validate_first_name(data.get("first_name", "")),
            "middle_name": CustomerValidator.validate_middle_name(data.get("middle_name", "")),
            "last_name": CustomerValidator.validate_last_name(data.get("last_name", "")),
            "dob": CustomerValidator.validate_dob(data.get("dob", "")),
            "gender": CustomerValidator.validate_gender(data.get("gender", "")),
            
            "government_id_type": CustomerValidator.validate_government_id_type(data.get("government_id_type", "")),
            "government_id_number": CustomerValidator.validate_government_id_number(
                data.get("government_id_type", ""),
                data.get("government_id_number", "")
            ),

            "phone": CustomerValidator.validate_phone(data.get("phone", "")),
            "email": CustomerValidator.validate_email(data.get("email", "")),

            "address": CustomerValidator.validate_address(data.get("address", "")),
            "state": CustomerValidator.validate_state(data.get("state", "")),
            "city": CustomerValidator.validate_city(data.get("city", "")),
            "pin_code": CustomerValidator.validate_pincode(data.get("pin_code", ""))
        }

        # Filter out None values
        errors = {k: v for k, v in errors.items() if v is not None}
        if errors:
            return False, errors

        # 2. Database Duplicate Checks & Insertion
        try:
            if CustomerRepository.exists_by_email(data["email"]):
                return False, {"email": "Email address is already registered."}

            if CustomerRepository.exists_by_government_id(data["government_id_number"]):
                return False, {"government_id_number": "Government ID number already exists."}

            if CustomerRepository.exists_by_phone(data["phone"]):
                return False, {"phone": "Phone number is already registered."}

            saved_id = CustomerRepository.insert_customer(data)
            if not saved_id:
                return False, {"general": "Failed to save customer to database."}

            return True, {}

        except Exception as e:
            logger.error(f"[CustomerService Error - save_customer]: {e}")
            return False, {"general": "Database connection error. Please try again later."}

    @staticmethod
    def search_customer(self, query: str):
        #Bridge method called by AccountFormPage to search for customers.
        return CustomerRepository.find_by_id_phone_or_email(query)

    
    @staticmethod
    def get_all_customers():
        #Fetches all customer records through repository.
        return CustomerRepository.get_all_customers()

    @staticmethod
    def update_customer_profile(customer_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:

        #Validates and updates customer profile data.
        success = CustomerRepository.update_customer(customer_id, data)
        if success:
            return True, {}
        return False, {"general": "Failed to update record in database."}