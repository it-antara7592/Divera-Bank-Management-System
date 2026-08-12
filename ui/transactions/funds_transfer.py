import logging
import customtkinter as ctk
import tkinter.messagebox as tkmb

from core import theme, fonts
from services.transaction_service import TransactionService
from ui.components.dialogs import ConfirmDialog,TransactionFundTransferDialog ,ManagerAuthorizationDialog

logger = logging.getLogger(__name__)


class FundsTransferPage(ctk.CTkFrame):
    """GUI page for transferring funds between two active accounts."""

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
        self.source_account = None
        self.destination_account = None
        self.pending_transfer = None

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
            text="FUNDS TRANSFER",
            font=fonts.APP_TITLE,
            text_color="white"
        )
        title.pack(pady=(20, 4))

        subtitle = ctk.CTkLabel(
            header,
            text="Execute secure account-to-account transactions.",
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
            text="Version 1.0    © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _create_content(self):
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(
            content,
            fg_color=theme.CARD,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.MEDIUM_RADIUS
        )
        card.pack(fill="x", padx=20, pady=(0, 20), ipadx=20, ipady=20)

        ctk.CTkLabel(
            card,
            text="🔄 Transfer Funds",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            card,
            text="Transfer money securely from one active account to another.",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Main Grid Layout for Left & Right Panels
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20)
        grid.columnconfigure((0, 1), weight=1)

        # Left Panel: Source Account
        f_left = ctk.CTkFrame(grid, fg_color="transparent")
        f_left.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)

        self._add_section_title(f_left, "FROM ACCOUNT")
        self.from_account_entry = self._create_search_row(f_left, "Source Account Number", "Enter account number")
        
        self.from_search_button = ctk.CTkButton(
            f_left,
            text="Search Source Account",
            height=40,
            corner_radius=theme.SMALL_RADIUS,
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.search_source_account
        )
        self.from_search_button.pack(fill="x", pady=(0, 15))
        self.from_info = self._create_account_info_box(f_left)

        # Right Panel: Destination Account
        f_right = ctk.CTkFrame(grid, fg_color="transparent")
        f_right.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)

        self._add_section_title(f_right, "TO ACCOUNT")
        self.to_account_entry = self._create_search_row(f_right, "Destination Account Number", "Enter account number")
        
        self.to_search_button = ctk.CTkButton(
            f_right,
            text="Search Destination Account",
            height=40,
            corner_radius=theme.SMALL_RADIUS,
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.search_destination_account
        )
        self.to_search_button.pack(fill="x", pady=(0, 15))
        self.to_info = self._create_account_info_box(f_right)

        # Amount Section
        amount_card = ctk.CTkFrame(card, fg_color="transparent")
        amount_card.pack(fill="x", padx=20, pady=(15, 0))

        self._add_section_title(amount_card, "TRANSFER AMOUNT")
        self._add_label(amount_card, "Amount")

        self.amount_entry = ctk.CTkEntry(
            amount_card,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            placeholder_text="Enter amount",
            font=fonts.LOGIN_ENTRY
        )
        self.amount_entry.pack(fill="x", pady=(0, 20))

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
            text="Transfer Funds",
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.handle_transfer
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

    def search_source_account(self):
        self._search_account(is_source=True)

    def search_destination_account(self):
        self._search_account(is_source=False)

    def _search_account(self, is_source: bool):
        entry = self.from_account_entry if is_source else self.to_account_entry
        info_box = self.from_info if is_source else self.to_info
        account_type_str = "source" if is_source else "destination"

        account_number = entry.get().strip()
        if not account_number:
            tkmb.showwarning(
                "Missing Account Number",
                f"Please enter the {account_type_str} account number."
            )
            return

        account = self.transaction_service.get_account_details(account_number)
        if not account:
            if is_source:
                self.source_account = None
            else:
                self.destination_account = None
            
            self._clear_info_box(info_box)
            tkmb.showerror("Account Not Found", f"{account_type_str.capitalize()} account does not exist.")
            return

        if is_source:
            self.source_account = account
        else:
            self.destination_account = account

        self._display_account(info_box, account)

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
    # TRANSFER & WORKFLOW
    # =========================================================

    def handle_transfer(self):
        from_account = self.from_account_entry.get().strip()
        to_account = self.to_account_entry.get().strip()
        amount = self.amount_entry.get().strip()

        is_valid, errors, transfer_details = self.transaction_service.validate_transfer(
            from_account, to_account, amount
        )

        if not is_valid:
            reason = next(iter(errors.values()), "Transfer validation failed.")
            if from_account or to_account or amount:
                # Resolve source account object safely to log the failure accurately if it exists
                source_obj = self.transaction_service.repo.get_account(from_account)
                if source_obj:
                    self.transaction_service._log_failed_transaction(
                        transaction_id="TXN-FAIL-" + __import__("uuid").uuid4().hex[:6].upper(),
                        account=source_obj,
                        amount=float(amount) if amount.replace('.', '', 1).isdigit() else 0.0,
                        reason=reason
                    )
            tkmb.showerror("Transfer Failed", reason)
            return

        self.pending_transfer = transfer_details
        source = transfer_details["source"]
        destination = transfer_details["destination"]
        transfer_amount = transfer_details["amount"]

        overdraft_text = ""
        if transfer_details["will_use_overdraft"]:
            overdraft_text = "\n\n⚠ This transfer will use the one-time overdraft facility."

        message = (
            "Please confirm the following transfer:\n\n"
            f"From:\n{source.get('customer_name', 'Unknown')} ({source.get('account_number', '')})\n\n"
            f"To:\n{destination.get('customer_name', 'Unknown')} ({destination.get('account_number', '')})\n\n"
            f"Amount: ₹{transfer_amount:,.2f}{overdraft_text}"
        )

        self._show_confirmation(message)

    def _show_confirmation(self, message):
        try:
            TransactionFundTransferDialog(
                self,
                title="Confirm Funds Transfer",
                message=message,
                confirm_text="Confirm Transfer",
                cancel_text="Cancel",
                is_destructive=False,
                on_confirm=self._after_confirmation
            )
        except TypeError:
            logger.exception("ConfirmDialog constructor mismatch.")
            tkmb.showerror("Dialog Error", "Unable to open the transfer confirmation dialog.")

    def _after_confirmation(self):
        try:
            if not self.pending_transfer:
                return
            ManagerAuthorizationDialog(
                self,
                on_authorized=self._after_authorization
            )
        except TypeError:
            logger.exception("ManagerAuthorizationDialog constructor mismatch.")
            tkmb.showerror("Authorization Error", "Unable to open the authorization dialog.")

    def _after_authorization(self):
        if not self.pending_transfer:
            return

        transfer_details = self.pending_transfer
        self.pending_transfer = None

        success, message = self.transaction_service.execute_transfer(transfer_details)

        if success:
            tkmb.showinfo("Transfer Successful", message)
            self.clear_form()
        else:
            tkmb.showerror("Transfer Failed", message)

    # =========================================================
    # FORM UTILITIES
    # =========================================================

    def clear_form(self):
        self.from_account_entry.delete(0, "end")
        self.to_account_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")

        self.source_account = None
        self.destination_account = None
        self.pending_transfer = None

        self._clear_info_box(self.from_info)
        self._clear_info_box(self.to_info)

    def handle_back(self):
        self.pending_transfer = None
        if self.on_back:
            self.on_back()