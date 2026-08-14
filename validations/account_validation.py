from typing import Dict, Tuple

# Minimum balance business rules
MINIMUM_BALANCES = {
    "Savings": 1000.0,
    "Current": 5000.0
}

class AccountValidation:
    """Validates form input data without database queries."""

    @staticmethod
    def validate_creation(payload: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
        """
        Validates account creation form fields.
        Returns (is_valid, errors_dict).
        """
        errors = {}

        # 1. Customer ID check
        customer_id = payload.get("customer_id", "").strip()
        if not customer_id:
            errors["general"] = "Customer ID is required to link an account."

        # 2. Account Type validation
        account_type = payload.get("account_type", "").strip()
        if account_type not in ["Savings", "Current"]:
            errors["account_type"] = "Invalid Account Type selected."

        # 3. Initial Deposit validation
        deposit_raw = str(payload.get("initial_deposit", "")).strip()
        if not deposit_raw:
            errors["initial_deposit"] = "Initial deposit amount is required."
        else:
            try:
                deposit_val = float(deposit_raw)
                if deposit_val < 0:
                    errors["initial_deposit"] = "Deposit amount cannot be negative."
                else:
                    min_required = MINIMUM_BALANCES.get(account_type, 1000.0)
                    if deposit_val < min_required:
                        errors["initial_deposit"] = f"Minimum opening deposit for {account_type} account is ₹{min_required:,.0f}."
            except ValueError:
                errors["initial_deposit"] = "Deposit must be a valid numeric amount."

        return len(errors) == 0, errors