import logging
import customtkinter as ctk
import tkinter.messagebox as tkmb

from core import theme, fonts
from services.transaction_service import TransactionService
from ui.components.dialogs import TransactionDepositDialog, ManagerAuthorizationDialog

logger = logging.getLogger(__name__)


class DepositPage(ctk.CTkFrame):
    """GUI page for processing account cash deposits."""

    def __init__(
        self,
        parent,
        transaction_service=None,
        on_back=None
    ):
        super().__init__(parent, fg_color=theme.BACKGROUND)
        self.pack(fill="both", expand=True)

        self.transaction_service = transaction_service or TransactionService()
        self.on_back = on_back

        # Form state
        self.account_data = None
        self.pending_deposit = None

        self.setup_ui()

    # =========================================================
    # UI SETUP
    # =========================================================

    def setup_ui(self):
        self._create_header()
        self._create_footer()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(
            self,
            height=120,
            fg_color=theme.PRIMARY,
            corner_radius=0
        )
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="CASH DEPOSIT",
            font=fonts.APP_TITLE,
            text_color="white"
        )
        title.pack(pady=(20, 4))

        subtitle = ctk.CTkLabel(
            header,
            text="Process secure account cash deposits and credit adjustments.",
            font=fonts.BODY_TEXT,
            text_color="#D8E6F3"
        )
        subtitle.pack()

    def _create_footer(self):
        footer = ctk.CTkFrame(self, height=35, fg_color="white", corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer,
            text="Version 1.0     © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _create_content(self):
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Center Container Wrapper for a single-column card layout
        center_wrapper = ctk.CTkFrame(content, fg_color="transparent")
        center_wrapper.pack(anchor="center", fill="x", padx=230, pady=10)
        center_wrapper.columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            center_wrapper,
            fg_color=theme.CARD,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.MEDIUM_RADIUS
        )
        card.grid(row=0, column=0, sticky="ew", ipadx=20, ipady=20)

        ctk.CTkLabel(
            card,
            text="💵 Account Deposit",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            card,
            text="Enter account details and specify deposit amount.",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Single Column Panel Form
        f_center = ctk.CTkFrame(card, fg_color="transparent")
        f_center.pack(fill="x", padx=20, pady=10)

        self._add_section_title(f_center, "ACCOUNT DETAILS")
        self.account_entry = self._create_search_row(f_center, "Account Number", "Enter account number")
        
        self.search_button = ctk.CTkButton(
            f_center,
            text="Search Account",
            height=40,
            corner_radius=theme.SMALL_RADIUS,
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.search_account
        )
        self.search_button.pack(fill="x", pady=(0, 15))
        self.account_info = self._create_account_info_box(f_center)

        # Deposit Amount & Overdraft Option Section
        amount_card = ctk.CTkFrame(card, fg_color="transparent")
        amount_card.pack(fill="x", padx=20, pady=(15, 0))

        self._add_section_title(amount_card, "DEPOSIT AMOUNT")
        self._add_label(amount_card, "Amount")

        self.amount_entry = ctk.CTkEntry(
            amount_card,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            placeholder_text="Enter deposit amount",
            font=fonts.LOGIN_ENTRY
        )
        self.amount_entry.pack(fill="x", pady=(0, 15))

        # Overdraft Repayment Option Checkbox (Initially disabled until Current account is searched)
        self.overdraft_var = ctk.BooleanVar(value=False)
        self.overdraft_checkbox = ctk.CTkCheckBox(
            amount_card,
            text="Process as Overdraft Repayment / Limit Reset",
            variable=self.overdraft_var,
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            state="disabled"
        )
        self.overdraft_checkbox.pack(anchor="w", pady=(0, 20))

        # Action Buttons Container (Balanced Widths)
        btn_container = ctk.CTkFrame(card, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(10, 10))
        btn_container.columnconfigure((0, 1, 2), weight=1)

        btn_common_kwargs = {
            "master": btn_container,
            "height": 42,
            "corner_radius": theme.SMALL_RADIUS,
        }

        ctk.CTkButton(
            **btn_common_kwargs,
            text="Process Deposit",
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.handle_deposit
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            **btn_common_kwargs,
            text="Clear Form",
            font=fonts.SECONDARY_BUTTON,
            fg_color="#F3F4F6",
            text_color=theme.TEXT_SECONDARY,
            hover_color="#E5E7EB",
            command=self.clear_form
        ).grid(row=0, column=1, sticky="ew", padx=(8, 8))

        ctk.CTkButton(
            **btn_common_kwargs,
            text="Back",
            font=fonts.SECONDARY_BUTTON,
            fg_color="#F3F4F6",
            text_color=theme.TEXT_SECONDARY,
            hover_color="#E5E7EB",
            command=self.handle_back
        ).grid(row=0, column=2, sticky="ew", padx=(8, 0))

    # =========================================================
    # UI HELPERS
    # =========================================================

    def _add_section_title(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=fonts.TABLE_HEADER,
            text_color=theme.PRIMARY,
            anchor="w"
        ).pack(fill="x", pady=(8, 6))

    def _add_label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x", pady=(2, 4))

    def _create_search_row(self, parent, label, placeholder):
        self._add_label(parent, label)
        entry = ctk.CTkEntry(
            parent,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            corner_radius=8,
            placeholder_text=placeholder,
            font=fonts.LOGIN_ENTRY
        )
        entry.pack(fill="x", pady=(0, 8))
        return entry

    def _create_account_info_box(self, parent):
        frame = ctk.CTkFrame(
            parent,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color="#E5E7EB"
        )
        frame.pack(fill="x", pady=(0, 10))

        labels = {}
        fields = [
            ("Account Number", "account_number"),
            ("Customer Name", "customer_name"),
            ("Customer ID", "customer_id"),
            ("Account Type", "account_type"),
            ("Current Balance", "balance"),
            ("Overdraft", "overdraft"),
            ("Overdraft Used", "overdraft_used"),
            ("Status", "status")
        ]

        for title, key in fields:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)

            ctk.CTkLabel(
                row,
                text=f"{title}:",
                width=120,
                anchor="w",
                font=fonts.TABLE_HEADER,
                text_color=theme.TEXT_SECONDARY
            ).pack(side="left")

            value_label = ctk.CTkLabel(
                row,
                text="—",
                anchor="w",
                font=fonts.TABLE_TEXT,
                text_color=theme.TEXT
            )
            value_label.pack(side="left", fill="x", expand=True)

            labels[key] = value_label

        frame.labels = labels
        return frame

    # =========================================================
    # ACCOUNT SEARCH
    # =========================================================

    def search_account(self):
        account_number = self.account_entry.get().strip()
        if not account_number:
            tkmb.showwarning(
                "Missing Account Number",
                "Please enter the account number for deposit."
            )
            return

        account = self.transaction_service.get_account_details(account_number)
        if not account:
            self.account_data = None
            self._clear_info_box(self.account_info)
            self.overdraft_checkbox.configure(state="disabled")
            self.overdraft_var.set(False)
            tkmb.showerror("Account Not Found", "The specified account does not exist.")
            return

        self.account_data = account
        self._display_account(self.account_info, account)

        # Enable/disable overdraft checkbox based on account type (Current only)
        if account.get("account_type", "").lower() == "current":
            self.overdraft_checkbox.configure(state="normal")
        else:
            self.overdraft_checkbox.configure(state="disabled")
            self.overdraft_var.set(False)

    def _display_account(self, info_box, account):
        labels = info_box.labels
        labels["account_number"].configure(text=account.get("account_number", "—"))
        labels["customer_name"].configure(text=account.get("customer_name", "—"))
        labels["customer_id"].configure(text=account.get("customer_id", "—"))
        labels["account_type"].configure(text=account.get("account_type", "—"))
        labels["balance"].configure(text=f"₹{float(account.get('balance', 0)):,.2f}")
        labels["overdraft"].configure(text=f"₹{float(account.get('overdraft', 0)):,.2f}")
        labels["overdraft_used"].configure(text="Yes" if account.get("overdraft_used", False) else "No")
        labels["status"].configure(text=account.get("status", "—"))

    def _clear_info_box(self, info_box):
        for label in info_box.labels.values():
            label.configure(text="—")

    # =========================================================
    # DEPOSIT & WORKFLOW
    # =========================================================

    def handle_deposit(self):
        account_number = self.account_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        is_overdraft_repayment = self.overdraft_var.get()
        account_type = self.account_data.get("account_type", "") if self.account_data else ""

        # 1. Validate through the TransactionService with overdraft options
        is_valid, errors, deposit_details = self.transaction_service.validate_deposit(
            account_number, amount_str, is_overdraft_repayment, account_type
        )

        # 2. Handle validation or account status failure
        if not is_valid:
            error_message = next(iter(errors.values())) if errors else "Invalid deposit details."
            
            # Log the failed transaction attempt in the database if account exists
            account_obj = self.transaction_service.get_account_details(account_number)
            if account_obj:
                self.transaction_service.log_failed_deposit_attempt(
                    account_number=account_number,
                    amount=amount_str,
                    reason=error_message
                )
            
            tkmb.showerror("Deposit Failed", error_message)
            return

        # 3. Extract details if validation succeeds
        account = deposit_details["account"]
        amount = deposit_details["amount"]
        clears_overdraft = deposit_details.get("clears_overdraft", False) or is_overdraft_repayment

        # 4. Construct the summary message for the confirmation dialog
        msg = (
            f"Account: {account.get('account_number')}\n"
            f"Name: {account.get('customer_name')}\n"
            f"Deposit Amount: ₹{amount:,.2f}\n"
        )

        if is_overdraft_repayment:
            msg += "\nℹ️ Note: This deposit is marked as an Overdraft Repayment and will reset the initial overdraft facility limits."
        elif clears_overdraft:
            msg += "\nℹ️ Note: This deposit will clear the active negative balance and reset the account's overdraft facility."

        # Save pending state for the next confirmation step
        self.pending_deposit = deposit_details

        # 6. Open confirmation dialog
        self._show_confirmation(msg)
        
    def _show_confirmation(self, message):
        try:
            TransactionDepositDialog(
                self,
                title="Confirm Cash Deposit",
                message=message,
                confirm_text="Confirm Deposit",
                cancel_text="Cancel",
                is_destructive=False,
                on_confirm=self._after_confirmation
            )
        except TypeError:
            logger.exception("TransactionDepositDialog constructor mismatch.")
            tkmb.showerror("Dialog Error", "Unable to open the deposit confirmation dialog.")

    def _after_confirmation(self):
        try:
            if not self.pending_deposit:
                return
            ManagerAuthorizationDialog(
                self,
                on_authorized=self._after_authorization
            )
        except TypeError:
            logger.exception("ManagerAuthorizationDialog constructor mismatch.")
            tkmb.showerror("Authorization Error", "Unable to open the authorization dialog.")

    def _after_authorization(self):
        if not self.pending_deposit:
            return

        deposit_details = self.pending_deposit
        self.pending_deposit = None

        success, message = self.transaction_service.execute_deposit(deposit_details)

        if success:
            tkmb.showinfo("Deposit Successful", message)
            self.clear_form()
        else:
            tkmb.showerror("Deposit Failed", message)

    # =========================================================
    # FORM UTILITIES
    # =========================================================

    def clear_form(self):
        self.account_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.overdraft_var.set(False)
        self.overdraft_checkbox.configure(state="disabled")

        self.account_data = None
        self.pending_deposit = None

        self._clear_info_box(self.account_info)

    def handle_back(self):
        self.pending_deposit = None
        if self.on_back:
            self.on_back()