from typing import Dict, Tuple


class TransactionValidation:
    #Validates fund transfer input before business logic execution.

    @staticmethod
    def validate_transfer_input(
        from_account: str,
        to_account: str,
        amount: str
    ) -> Tuple[bool, Dict[str, str]]:

        errors = {}

        from_account = from_account.strip()
        to_account = to_account.strip()
        amount = amount.strip()

        if not from_account:
            errors["from_account"] = (
                "Source account number is required."
            )

        if not to_account:
            errors["to_account"] = (
                "Destination account number is required."
            )

        if (
            from_account
            and to_account
            and from_account == to_account
        ):
            errors["to_account"] = (
                "Source and destination accounts cannot be the same."
            )

        if not amount:
            errors["amount"] = "Transfer amount is required."
        else:
            try:
                amount_value = float(amount)

                if amount_value <= 0:
                    errors["amount"] = (
                        "Transfer amount must be greater than ₹0."
                    )

            except ValueError:
                errors["amount"] = (
                    "Transfer amount must be a valid number."
                )

        return len(errors) == 0, errors

    @staticmethod
    def validate_withdrawal_input(
        account_number: str,
        amount: str
    ) -> Tuple[bool, Dict[str, str]]:

        errors = {}

        account_number = account_number.strip()
        amount = amount.strip()

        if not account_number:
            errors["account_number"] = (
                "Account number is required."
            )

        if not amount:
            errors["amount"] = "Withdrawal amount is required."
        else:
            try:
                amount_value = float(amount)

                if amount_value <= 0:
                    errors["amount"] = (
                        "Withdrawal amount must be greater than ₹0."
                    )

            except ValueError:
                errors["amount"] = (
                    "Withdrawal amount must be a valid number."
                )

        return len(errors) == 0, errors

    @staticmethod
    def validate_deposit_input(
        account_number: str,
        amount: str,
        is_overdraft_repayment: bool = False,
        account_type: str = ""
    ) -> Tuple[bool, Dict[str, str]]:

        errors = {}

        account_number = account_number.strip()
        amount = amount.strip()

        if not account_number:
            errors["account_number"] = (
                "Account number is required."
            )

        if not amount:
            errors["amount"] = "Deposit amount is required."
        else:
            try:
                amount_value = float(amount)

                if amount_value <= 0:
                    errors["amount"] = (
                        "Deposit amount must be greater than ₹0."
                    )

            except ValueError:
                errors["amount"] = (
                    "Deposit amount must be a valid number."
                )

        if is_overdraft_repayment:
            if account_type.lower() != "current":
                errors["general"] = (
                    "Overdraft repayment option is only available for Current accounts."
                )

        return len(errors) == 0, errors