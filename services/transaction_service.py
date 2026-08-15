import logging
from typing import Dict, Any, Tuple
from repositories.transaction_repository import TransactionRepository
from validations.transaction_validation import TransactionValidation
logger = logging.getLogger(__name__)


class TransactionService:
    """
    Handles banking transaction business logic.

    Supported transactions:
    - Funds Transfer
    - Cash Withdrawal
    - Cash Deposit

    Transaction records permanently store:
    - Transaction ID
    - Transaction type
    - Account information
    - Customer information
    - Amount
    - Balance before
    - Balance after
    - Status
    - Failure reason when applicable

    MongoDB multi-document transactions are intentionally
    not used for this project.
    """

    def __init__(self, transaction_repo=None):

        self.repo = (
            transaction_repo
            or TransactionRepository()
        )

    # =========================================================
    # ACCOUNT LOOKUP
    # =========================================================

    def get_account_details(
        self,
        account_number: str
    ):
        return self.repo.get_account(account_number)

    # =========================================================
    # VALIDATE TRANSFER
    # =========================================================

    def validate_transfer(
        self,
        from_account: str,
        to_account: str,
        amount: str
    ) -> Tuple[
        bool,
        Dict[str, str],
        Dict[str, Any]
    ]:

        is_valid, errors = (
            TransactionValidation
            .validate_transfer_input(
                from_account,
                to_account,
                amount
            )
        )

        if not is_valid:
            return False, errors, {}

        try:
            amount_value = float(amount)
        except (ValueError, TypeError):
            return (
                False,
                {
                    "amount":
                    "Invalid transfer amount."
                },
                {}
            )

        # -----------------------------------------------------
        # SOURCE ACCOUNT
        # -----------------------------------------------------

        source = self.repo.get_account(from_account)

        if not source:
            return (
                False,
                {
                    "from_account":
                    "Source account does not exist."
                },
                {}
            )

        # -----------------------------------------------------
        # DESTINATION ACCOUNT
        # -----------------------------------------------------

        destination = self.repo.get_account(to_account)

        if not destination:
            return (
                False,
                {
                    "to_account":
                    "Destination account does not exist."
                },
                {}
            )

        # -----------------------------------------------------
        # ACCOUNT STATUS
        # -----------------------------------------------------

        if source.get("status") != "Active":
            return (
                False,
                {
                    "from_account":
                    "Source account is not active."
                },
                {}
            )

        if destination.get("status") != "Active":
            return (
                False,
                {
                    "to_account":
                    "Destination account is not active."
                },
                {}
            )

        # -----------------------------------------------------
        # SAME ACCOUNT CHECK
        # -----------------------------------------------------

        if (
            source.get("account_number")
            == destination.get("account_number")
        ):
            return (
                False,
                {
                    "general":
                    "Source and destination accounts "
                    "cannot be the same."
                },
                {}
            )

        # -----------------------------------------------------
        # BALANCE / OVERDRAFT CHECK
        # -----------------------------------------------------

        balance = float(
            source.get("balance", 0.0)
        )

        overdraft_limit = float(
            source.get("overdraft", 0.0)
        )

        overdraft_used = bool(
            source.get("overdraft_used", False)
        )

        will_use_overdraft = False

        if amount_value > balance:

            required_overdraft = (
                amount_value - balance
            )

            if overdraft_limit <= 0:
                return (
                    False,
                    {
                        "amount":
                        "Insufficient balance."
                    },
                    {}
                )

            if overdraft_used:
                return (
                    False,
                    {
                        "amount":
                        "Insufficient balance. "
                        "The one-time overdraft facility "
                        "has already been used."
                    },
                    {}
                )

            if required_overdraft > overdraft_limit:
                return (
                    False,
                    {
                        "amount":
                        "Insufficient balance. "
                        f"Available overdraft is "
                        f"₹{overdraft_limit:,.2f}."
                    },
                    {}
                )

            will_use_overdraft = True

        # -----------------------------------------------------
        # TRANSFER DETAILS
        # -----------------------------------------------------

        transfer_details = {
            "source": source,
            "destination": destination,
            "amount": amount_value,
            "will_use_overdraft": will_use_overdraft
        }

        return True, {}, transfer_details

    # =========================================================
    # EXECUTE TRANSFER
    # =========================================================

    def execute_transfer(
        self,
        transfer_details: Dict[str, Any]
    ) -> Tuple[bool, str]:

        source = transfer_details["source"]
        destination = transfer_details["destination"]

        amount = float(
            transfer_details["amount"]
        )

        will_use_overdraft = bool(
            transfer_details.get(
                "will_use_overdraft",
                False
            )
        )

        source_number = source["account_number"]
        destination_number = destination["account_number"]

        source_balance = float(
            source.get("balance", 0.0)
        )

        destination_balance = float(
            destination.get("balance", 0.0)
        )

        # -----------------------------------------------------
        # CALCULATE NEW BALANCES
        # -----------------------------------------------------

        new_source_balance = (
            source_balance - amount
        )

        new_destination_balance = (
            destination_balance + amount
        )

        transaction_id = (
            self.repo.generate_transaction_id()
        )

        # -----------------------------------------------------
        # UPDATE SOURCE BALANCE
        # -----------------------------------------------------

        source_updated = (
            self.repo.update_account_balance(
                source_number,
                new_source_balance
            )
        )

        if not source_updated:

            self._log_failed_transfer_transaction(
                transaction_id,
                source,
                destination,
                amount,
                "Failed to update source account balance."
            )

            return (
                False,
                "Transfer failed while updating "
                "the source account."
            )

        # -----------------------------------------------------
        # UPDATE OVERDRAFT STATUS
        # -----------------------------------------------------

        if will_use_overdraft:

            overdraft_updated = (
                self.repo.mark_overdraft_used(
                    source_number
                )
            )

            if not overdraft_updated:

                self._log_failed_transfer_transaction(
                    transaction_id,
                    source,
                    destination,
                    amount,
                    "Failed to update overdraft status."
                )

                return (
                    False,
                    "Transfer failed while updating "
                    "the overdraft facility."
                )

        # -----------------------------------------------------
        # UPDATE DESTINATION BALANCE
        # -----------------------------------------------------

        destination_updated = (
            self.repo.update_account_balance(
                destination_number,
                new_destination_balance
            )
        )

        if not destination_updated:

            self._log_failed_transfer_transaction(
                transaction_id,
                source,
                destination,
                amount,
                "Failed to update destination account."
            )

            return (
                False,
                "Transfer failed while updating "
                "the destination account."
            )

        # -----------------------------------------------------
        # SUCCESSFUL TRANSFER RECORD
        # -----------------------------------------------------

        transaction_record = {

            "transaction_id":
                transaction_id,

            "transaction_type":
                "Funds Transfer",

            # Source account
            "from_account":
                source_number,

            # Destination account
            "to_account":
                destination_number,

            # Customer information
            "from_customer_id":
                source.get("customer_id"),

            "to_customer_id":
                destination.get("customer_id"),

            "from_customer_name":
                source.get("customer_name"),

            "to_customer_name":
                destination.get("customer_name"),

            # Amount
            "amount":
                amount,

            # IMPORTANT:
            # Transfer is outgoing from source account.
            "balance_before":
                source_balance,

            "balance_after":
                new_source_balance,

            "to_balance_before":
                destination_balance,
                
            "to_balance_after": 
                new_destination_balance,

            "overdraft_used":
                will_use_overdraft,

            "status":
                "Completed"
        }

        transaction_saved = (
            self.repo.insert_transaction(
                transaction_record
            )
        )

        if not transaction_saved:

            return (
                False,
                "Transfer completed, but the transaction "
                "log could not be saved. Please check "
                "the transaction records."
            )

        return (
            True,
            f"₹{amount:,.2f} transferred successfully.\n\n"
            f"Transaction ID: {transaction_id}"
        )

    # =========================================================
    # FAILED TRANSFER
    # =========================================================

    def log_failed_transfer_attempt(
        self,
        from_account: str,
        to_account: str,
        amount: str,
        reason: str
    ):

        try:

            source = None
            destination = None

            if from_account:
                source = self.repo.get_account(
                    from_account
                )

            if to_account:
                destination = self.repo.get_account(
                    to_account
                )

            transaction_id = (
                self.repo.generate_transaction_id()
            )

            try:
                amount_value = (
                    float(amount)
                    if amount
                    else 0.0
                )
            except (ValueError, TypeError):
                amount_value = 0.0

            record = {

                "transaction_id":
                    transaction_id,

                "transaction_type":
                    "Funds Transfer",

                "from_account":
                    from_account or None,

                "to_account":
                    to_account or None,

                "from_customer_id":
                    source.get("customer_id")
                    if source else None,

                "to_customer_id":
                    destination.get("customer_id")
                    if destination else None,

                "from_customer_name":
                    source.get("customer_name")
                    if source else None,

                "to_customer_name":
                    destination.get("customer_name")
                    if destination else None,

                "amount":
                    amount_value,

                "overdraft_used":
                    False,

                "status":
                    "Failed",

                "failure_reason":
                    reason
            }

            self.repo.insert_transaction(record)

        except Exception:
            logger.exception("Failed to log transfer attempt.")

    def _log_failed_transfer_transaction(
        self,
        transaction_id,
        source,
        destination,
        amount,
        reason
    ):

        record = {

            "transaction_id":
                transaction_id,

            "transaction_type":
                "Funds Transfer",

            "from_account":
                source.get("account_number"),

            "to_account":
                destination.get("account_number"),

            "from_customer_id":
                source.get("customer_id"),

            "to_customer_id":
                destination.get("customer_id"),

            "from_customer_name":
                source.get("customer_name"),

            "to_customer_name":
                destination.get("customer_name"),

            "amount":
                amount,

            "overdraft_used":
                False,

            "status":
                "Failed",

            "failure_reason":
                reason
        }

        self.repo.insert_transaction(record)

    # =========================================================
    # BACKWARD COMPATIBILITY FOR TRANSFER UI
    # =========================================================

    def log_failed_attempt(
        self,
        from_account,
        to_account=None,
        amount=None,
        reason=None
    ):
        """
        Compatibility wrapper for existing transfer UI code.

        The old UI may call:
            log_failed_attempt(
                from_account,
                to_account,
                amount,
                reason
            )
        """

        return self.log_failed_transfer_attempt(
            from_account,
            to_account,
            amount,
            reason
        )

    # =========================================================
    # VALIDATE WITHDRAWAL
    # =========================================================

    def validate_withdrawal(
        self,
        account_number: str,
        amount: str
    ) -> Tuple[
        bool,
        Dict[str, str],
        Dict[str, Any]
    ]:

        is_valid, errors = (
            TransactionValidation
            .validate_withdrawal_input(
                account_number,
                amount
            )
        )

        if not is_valid:
            return False, errors, {}

        try:
            amount_value = float(amount)
        except (ValueError, TypeError):
            return (
                False,
                {
                    "amount":
                    "Invalid withdrawal amount."
                },
                {}
            )

        account = self.repo.get_account(
            account_number
        )

        if not account:
            return (
                False,
                {
                    "account_number":
                    "Account does not exist."
                },
                {}
            )

        if account.get("status") != "Active":
            return (
                False,
                {
                    "account_number":
                    "Account is not active."
                },
                {}
            )

        balance = float(
            account.get("balance", 0.0)
        )

        overdraft_limit = float(
            account.get("overdraft", 0.0)
        )

        overdraft_used = bool(
            account.get("overdraft_used", False)
        )

        will_use_overdraft = False

        if amount_value > balance:

            required_overdraft = (
                amount_value - balance
            )

            if overdraft_limit <= 0:
                return (
                    False,
                    {
                        "amount":
                        "Insufficient balance."
                    },
                    {}
                )

            if overdraft_used:
                return (
                    False,
                    {
                        "amount":
                        "Insufficient balance. "
                        "The one-time overdraft facility "
                        "has already been used."
                    },
                    {}
                )

            if required_overdraft > overdraft_limit:
                return (
                    False,
                    {
                        "amount":
                        "Insufficient balance. "
                        f"Available overdraft is "
                        f"₹{overdraft_limit:,.2f}."
                    },
                    {}
                )

            will_use_overdraft = True

        withdrawal_details = {

            "account":
                account,

            "amount":
                amount_value,

            "will_use_overdraft":
                will_use_overdraft
        }

        return True, {}, withdrawal_details

    # =========================================================
    # EXECUTE WITHDRAWAL
    # =========================================================

    def execute_withdrawal(
        self,
        withdrawal_details: Dict[str, Any]
    ) -> Tuple[bool, str]:

        account = withdrawal_details["account"]

        amount = float(
            withdrawal_details["amount"]
        )

        will_use_overdraft = bool(
            withdrawal_details.get(
                "will_use_overdraft",
                False
            )
        )

        account_number = account["account_number"]

        account_balance = float(
            account.get("balance", 0.0)
        )

        # -----------------------------------------------------
        # CALCULATE NEW BALANCE
        # -----------------------------------------------------

        new_account_balance = (
            account_balance - amount
        )

        transaction_id = (
            self.repo.generate_transaction_id()
        )

        # -----------------------------------------------------
        # UPDATE ACCOUNT
        # -----------------------------------------------------

        account_updated = (
            self.repo.update_account_balance(
                account_number,
                new_account_balance
            )
        )

        if not account_updated:

            self._log_failed_withdrawal_transaction(
                transaction_id,
                account,
                amount,
                "Failed to update account balance."
            )

            return (
                False,
                "Withdrawal failed while updating "
                "the account."
            )

        # -----------------------------------------------------
        # OVERDRAFT
        # -----------------------------------------------------

        if will_use_overdraft:

            overdraft_updated = (
                self.repo.mark_overdraft_used(
                    account_number
                )
            )

            if not overdraft_updated:

                self._log_failed_withdrawal_transaction(
                    transaction_id,
                    account,
                    amount,
                    "Failed to update overdraft status."
                )

                return (
                    False,
                    "Withdrawal failed while updating "
                    "the overdraft facility."
                )

        # -----------------------------------------------------
        # SUCCESSFUL WITHDRAWAL RECORD
        # -----------------------------------------------------

        transaction_record = {

            "transaction_id":
                transaction_id,

            "transaction_type":
                "Cash Withdrawal",

            "account_number":
                account_number,

            "customer_id":
                account.get("customer_id"),

            "customer_name":
                account.get("customer_name"),

            "amount":
                amount,

            "balance_before":
                account_balance,

            "balance_after":
                new_account_balance,

            "overdraft_used":
                will_use_overdraft,

            "status":
                "Completed"
        }

        transaction_saved = (
            self.repo.insert_transaction(
                transaction_record
            )
        )

        if not transaction_saved:

            return (
                False,
                "Withdrawal completed, but the transaction "
                "log could not be saved. Please check "
                "the transaction records."
            )

        return (
            True,
            f"₹{amount:,.2f} withdrawn successfully.\n\n"
            f"Transaction ID: {transaction_id}"
        )

    # =========================================================
    # FAILED WITHDRAWAL
    # =========================================================

    def log_failed_withdrawal_attempt(
        self,
        account_number: str,
        amount: str,
        reason: str
    ):

        try:

            account = None

            if account_number:
                account = self.repo.get_account(
                    account_number
                )

            transaction_id = (
                self.repo.generate_transaction_id()
            )

            try:
                amount_value = (
                    float(amount)
                    if amount
                    else 0.0
                )
            except (ValueError, TypeError):
                amount_value = 0.0

            record = {

                "transaction_id":
                    transaction_id,

                "transaction_type":
                    "Cash Withdrawal",

                "account_number":
                    account_number or None,

                "customer_id":
                    account.get("customer_id")
                    if account else None,

                "customer_name":
                    account.get("customer_name")
                    if account else None,

                "amount":
                    amount_value,

                "overdraft_used":
                    False,

                "status":
                    "Failed",

                "failure_reason":
                    reason
            }

            self.repo.insert_transaction(record)

        except Exception:
            logger.exception("Failed to log withdrawal attempt.")

    def _log_failed_withdrawal_transaction(
        self,
        transaction_id,
        account,
        amount,
        reason
    ):

        record = {

            "transaction_id":
                transaction_id,

            "transaction_type":
                "Cash Withdrawal",

            "account_number":
                account.get("account_number"),

            "customer_id":
                account.get("customer_id"),

            "customer_name":
                account.get("customer_name"),

            "amount":
                amount,

            "overdraft_used":
                False,

            "status":
                "Failed",

            "failure_reason":
                reason
        }

        self.repo.insert_transaction(record)

    # =========================================================
    # VALIDATE DEPOSIT
    # =========================================================

    def validate_deposit(
        self,
        account_number: str,
        amount: str,
        is_overdraft_repayment: bool = False,
        account_type: str = ""
    ) -> Tuple[
        bool,
        Dict[str, str],
        Dict[str, Any]
    ]:

        is_valid, errors = (
            TransactionValidation
            .validate_deposit_input(
                account_number,
                amount,
                is_overdraft_repayment,
                account_type
            )
        )

        if not is_valid:
            return False, errors, {}

        try:
            amount_value = float(amount)
        except (ValueError, TypeError):
            return (
                False,
                {
                    "amount":
                    "Invalid deposit amount."
                },
                {}
            )

        account = self.repo.get_account(
            account_number
        )

        if not account:
            return (
                False,
                {
                    "account_number":
                    "Account does not exist."
                },
                {}
            )

        if account.get("status") != "Active":
            return (
                False,
                {
                    "account_number":
                    "Account is not active."
                },
                {}
            )

        account_acc_type = account.get(
            "account_type",
            ""
        ).lower()

        overdraft_used = bool(
            account.get(
                "overdraft_used",
                False
            )
        )

        balance = float(
            account.get("balance", 0.0)
        )

        if is_overdraft_repayment:

            if account_acc_type != "current":
                return (
                    False,
                    {
                        "general":
                        "Overdraft repayment is only "
                        "available for Current accounts."
                    },
                    {}
                )

            if balance >= 0:
                return (
                    False,
                    {
                        "general":
                        "This account has no outstanding overdraft."
                    },
                    {}
                )

            if not overdraft_used:
                return (
                    False,
                    {
                        "general":
                        "This account has no active overdraft "
                        "to repay."
                    },
                    {}
                )
            # Repayment must exactly match the outstanding amount
            outstanding_overdraft = abs(balance)

            if amount_value != outstanding_overdraft:
                return (
                    False,
                    {
                        "amount":
                        f"Overdraft repayment must be exactly "
                        f"₹{outstanding_overdraft:,.2f}."
                    },
                    {}
                )

        deposit_details = {

            "account":
                account,

            "amount":
                amount_value,

            "is_overdraft_repayment":
                is_overdraft_repayment
        }

        return True, {}, deposit_details

    # =========================================================
    # EXECUTE DEPOSIT
    # =========================================================

    def execute_deposit(
        self,
        deposit_details: Dict[str, Any]
    ) -> Tuple[bool, str]:

        account = deposit_details["account"]

        amount = float(
            deposit_details["amount"]
        )

        is_overdraft_repayment = bool(
            deposit_details.get(
                "is_overdraft_repayment",
                False
            )
        )

        account_number = account["account_number"]

        account_balance = float(
            account.get("balance", 0.0)
        )

        # -----------------------------------------------------
        # CALCULATE NEW BALANCE
        # -----------------------------------------------------

        new_account_balance = (
            account_balance + amount
        )

        transaction_id = (
            self.repo.generate_transaction_id()
        )

        # -----------------------------------------------------
        # UPDATE ACCOUNT
        # -----------------------------------------------------

        account_updated = (
            self.repo.update_account_balance(
                account_number,
                new_account_balance
            )
        )

        if not account_updated:

            self._log_failed_deposit_transaction(
                transaction_id,
                account,
                amount,
                "Failed to update account balance."
            )

            return (
                False,
                "Deposit failed while updating "
                "the account."
            )

        # -----------------------------------------------------
        # RESET OVERDRAFT
        # -----------------------------------------------------

        # -----------------------------------------------------
        # RESET OVERDRAFT
        # -----------------------------------------------------

        if is_overdraft_repayment:

            # Safety check: repayment must completely clear
            # the negative overdraft balance.
            if round(new_account_balance, 2) != 0:
                self._log_failed_deposit_transaction(
                    transaction_id,
                    account,
                    amount,
                    "Overdraft repayment did not fully clear "
                    "the outstanding overdraft balance."
                )

                return (
                    False,
                    "Overdraft repayment must fully clear "
                    "the outstanding overdraft balance."
                )

            overdraft_reset = (
                self.repo.reset_overdraft_status(
                    account_number
                )
            )

            if not overdraft_reset:

                self._log_failed_deposit_transaction(
                    transaction_id,
                    account,
                    amount,
                    "Failed to reset overdraft status."
                )

                return (
                    False,
                    "Deposit failed while resetting "
                    "the overdraft facility."
                )

        # -----------------------------------------------------
        # SUCCESSFUL DEPOSIT RECORD
        # -----------------------------------------------------

        transaction_record = {

            "transaction_id":
                transaction_id,

            "transaction_type":
                "Cash Deposit",

            "account_number":
                account_number,

            "customer_id":
                account.get("customer_id"),

            "customer_name":
                account.get("customer_name"),

            "amount":
                amount,

            "balance_before":
                account_balance,

            "balance_after":
                new_account_balance,

            "overdraft_reset":
                is_overdraft_repayment,

            "status":
                "Completed"
        }

        transaction_saved = (
            self.repo.insert_transaction(
                transaction_record
            )
        )

        if not transaction_saved:

            return (
                False,
                "Deposit completed, but the transaction "
                "log could not be saved. Please check "
                "the transaction records."
            )

        success_msg = (
            f"₹{amount:,.2f} deposited successfully.\n\n"
            f"Transaction ID: {transaction_id}"
        )

        if is_overdraft_repayment:
            success_msg += (
                "\nOverdraft facility has been "
                "successfully reset."
            )

        return True, success_msg

    # =========================================================
    # FAILED DEPOSIT
    # =========================================================

    def log_failed_deposit_attempt(
        self,
        account_number: str,
        amount: str,
        reason: str
    ):

        try:

            account = None

            if account_number:
                account = self.repo.get_account(
                    account_number
                )

            transaction_id = (
                self.repo.generate_transaction_id()
            )

            try:
                amount_value = (
                    float(amount)
                    if amount
                    else 0.0
                )
            except (ValueError, TypeError):
                amount_value = 0.0

            record = {

                "transaction_id":
                    transaction_id,

                "transaction_type":
                    "Cash Deposit",

                "account_number":
                    account_number or None,

                "customer_id":
                    account.get("customer_id")
                    if account else None,

                "customer_name":
                    account.get("customer_name")
                    if account else None,

                "amount":
                    amount_value,

                "overdraft_reset":
                    False,

                "status":
                    "Failed",

                "failure_reason":
                    reason
            }

            self.repo.insert_transaction(record)

        except Exception:
            logger.exception("Failed to log deposit attempt.")

    def _log_failed_deposit_transaction(
        self,
        transaction_id,
        account,
        amount,
        reason
    ):

        record = {

            "transaction_id":
                transaction_id,

            "transaction_type":
                "Cash Deposit",

            "account_number":
                account.get("account_number"),

            "customer_id":
                account.get("customer_id"),

            "customer_name":
                account.get("customer_name"),

            "amount":
                amount,

            "overdraft_reset":
                False,

            "status":
                "Failed",

            "failure_reason":
                reason
        }

        self.repo.insert_transaction(record)

    # =========================================================
    # GET ALL TRANSACTIONS
    # =========================================================

    def get_all_transactions(self) -> list:
        """Fetch all permanent transaction records."""
        return self.repo.get_all_transactions()