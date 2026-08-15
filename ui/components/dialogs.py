import customtkinter as ctk
from core import theme, fonts
import logging
from services.transaction_service import TransactionService 
from core.security import verify_password
from db import get_db

class SuccessDialog(ctk.CTkToplevel):

    def __init__(self, parent, customer_data: dict, on_create_account=None, on_customer_management=None):
        """
        Success modal confirming customer creation and offering direct contextual actions.

        :param parent: Parent frame/window
        :param customer_data: Dict containing created customer details (customer_id, full_name, government_id_type, etc.)
        :param on_create_account: Callback receiving customer_data to transition directly to Account Creation
        :param on_customer_management: Callback to return to Customer Management
        """
        super().__init__(parent)

        self.customer_data = customer_data
        self.on_create_account_callback = on_create_account
        self.on_customer_management_callback = on_customer_management

        # Window Configuration
        self.title("Customer Created")
        self.geometry("480x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 240
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 240
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        # Header Container (Success Icon & Title)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(24, 16))

        icon_lbl = ctk.CTkLabel(
            header_frame,
            text="✓",
            font=("Montserrat", 32, "bold"),
            text_color="#10B981"  # Emerald Success Green
        )
        icon_lbl.pack()

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Customer Created Successfully",
            font=fonts.SECTION_TITLE,
            text_color=theme.TEXT
        )
        title_lbl.pack(pady=(4, 0))

        # Customer Summary Card
        card = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            corner_radius=8,
            border_width=1,
            border_color=theme.BORDER
        )
        card.pack(fill="x", padx=32, pady=(0, 20))

        # Format details
        cust_id = self.customer_data.get("customer_id", "N/A")
        
        # Build full name dynamically if stored split or together
        full_name = self.customer_data.get("full_name")
        if not full_name:
            first = self.customer_data.get("first_name", "")
            middle = self.customer_data.get("middle_name", "")
            last = self.customer_data.get("last_name", "")
            full_name = " ".join(filter(None, [first, middle, last]))

        id_type = self.customer_data.get("government_id_type", "Gov ID")
        id_num = self.customer_data.get("government_id_number", "N/A")
        phone = self.customer_data.get("phone", "N/A")

        summary_rows = [
            ("Customer ID", cust_id),
            ("Customer Name", full_name),
            ("Government ID", f"{id_type} - {id_num}"),
            ("Phone", phone)
        ]

        for idx, (label_text, val_text) in enumerate(summary_rows):
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=16, pady=8)

            lbl = ctk.CTkLabel(
                row_frame,
                text=label_text,
                font=("Montserrat", 11, "bold"),
                text_color="#6B7280",
                anchor="w"
            )
            lbl.pack(side="left")

            val = ctk.CTkLabel(
                row_frame,
                text=val_text,
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT,
                anchor="e"
            )
            val.pack(side="right")

            # Subtle inner line separator except last row
            if idx < len(summary_rows) - 1:
                sep = ctk.CTkFrame(card, height=1, fg_color="#E5E7EB")
                sep.pack(fill="x", padx=16)

        # Divider
        divider = ctk.CTkFrame(self, height=1, fg_color=theme.BORDER)
        divider.pack(fill="x", padx=32, pady=(0, 20))

        # Actions Container
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=32)

        # Primary Action: Create Bank Account
        create_acc_btn = ctk.CTkButton(
            actions_frame,
            text="Create Bank Account",
            font=fonts.BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            height=42,
            command=self._handle_create_account
        )
        create_acc_btn.pack(fill="x", pady=(0, 10))

        # Secondary Action: Back to Customer Management
        mgmt_btn = ctk.CTkButton(
            actions_frame,
            text="Back to Customer Management",
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            height=38,
            command=self._handle_customer_management
        )
        mgmt_btn.pack(fill="x")

    def _handle_create_account(self):
        self.destroy()
        if callable(self.on_create_account_callback):
            self.on_create_account_callback(self.customer_data)

    def _handle_customer_management(self):
        self.destroy()
        if callable(self.on_customer_management_callback):
            self.on_customer_management_callback()


class ConfirmDialog(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        title="Discard Changes?",
        message="You have unsaved changes. Are you sure you want to leave?",
        confirm_text="Discard & Leave",
        cancel_text="Keep Editing",
        is_destructive=True,
        on_confirm=None
    ):
        """
        Confirmation modal supporting both destructive (discard/delete) actions
        and standard affirmative (confirm/save) actions.

        :param parent: Parent frame/window
        :param title: Title for the popup window
        :param message: Confirmation message text
        :param confirm_text: Text for primary action button
        :param cancel_text: Text for secondary/cancel button
        :param is_destructive: If True, uses Red button styling. If False, uses Primary Blue styling.
        :param on_confirm: Callback executed if the user confirms
        """
        super().__init__(parent)

        self.on_confirm_callback = on_confirm
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.is_destructive = is_destructive

        # Window Configuration
        self.title(title)
        self.geometry("420x210")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 105
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui(message)

    def _build_ui(self, message):
        # Message Display
        msg_label = ctk.CTkLabel(
            self,
            text=message,
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT,
            wraplength=370,
            justify="center"
        )
        msg_label.pack(pady=(35, 25))

        # Button Container
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30)

        # Cancel / Neutral Button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=self.cancel_text,
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            width=140,
            height=38,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        # Confirm Button (Styled conditionally based on is_destructive)
        btn_fg = "#EF4444" if self.is_destructive else theme.PRIMARY
        btn_hover = "#DC2626" if self.is_destructive else theme.BUTTON_PRIMARY_HOVER

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=self.confirm_text,
            font=fonts.BUTTON,
            fg_color=btn_fg,
            hover_color=btn_hover,
            text_color="white",
            width=140,
            height=38,
            command=self._handle_confirm
        )
        confirm_btn.pack(side="right")

    def _handle_confirm(self):
        self.destroy()
        if callable(self.on_confirm_callback):
            self.on_confirm_callback()


class AccountSuccessDialog(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        account_data: dict,
        on_account_management=None
    ):
        super().__init__(parent)

        self.account_data = account_data
        self.on_account_management_callback = on_account_management

        self.title("Account Created")
        self.geometry("480x480")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()

        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 240
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 260

        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(pady=(24, 16))

        icon = ctk.CTkLabel(
            header,
            text="✓",
            font=("Montserrat", 32, "bold"),
            text_color="#10B981"
        )
        icon.pack()

        title = ctk.CTkLabel(
            header,
            text="Account Created Successfully",
            font=fonts.SECTION_TITLE,
            text_color=theme.TEXT
        )
        title.pack(pady=(4, 0))

        card = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            corner_radius=8,
            border_width=1,
            border_color=theme.BORDER
        )
        card.pack(fill="x", padx=32, pady=(0, 20))

        overdraft_val = self.account_data.get('overdraft', 0.0)
        overdraft_str = f"₹ {overdraft_val:,.2f}"

        rows = [
            ("Account Number", self.account_data.get("account_number", "N/A")),
            ("Customer Name", self.account_data.get("customer_name", "N/A")),
            ("Account Type", self.account_data.get("account_type", "N/A")),
            ("Opening Balance", f"₹ {self.account_data.get('balance', 0):,.2f}"),
            ("Overdraft Facility", overdraft_str),
            ("Status", self.account_data.get("status", "Active"))
        ]

        for i, (label, value) in enumerate(rows):
            row = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            row.pack(fill="x", padx=16, pady=8)

            left = ctk.CTkLabel(
                row,
                text=label,
                font=("Montserrat", 11, "bold"),
                text_color="#6B7280"
            )
            left.pack(side="left")

            right = ctk.CTkLabel(
                row,
                text=str(value),
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT
            )
            right.pack(side="right")

            if i < len(rows) - 1:
                sep = ctk.CTkFrame(
                    card,
                    height=1,
                    fg_color="#E5E7EB"
                )
                sep.pack(fill="x", padx=16)

        divider = ctk.CTkFrame(
            self,
            height=1,
            fg_color=theme.BORDER
        )
        divider.pack(fill="x", padx=32, pady=(0, 20))

        actions = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        actions.pack(fill="x", padx=32)

        manage_btn = ctk.CTkButton(
            actions,
            text="Back to Account Management",
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            height=38,
            command=self._handle_management
        )
        manage_btn.pack(fill="x")

    def _handle_management(self):
        self.destroy()
        if callable(self.on_account_management_callback):
            self.on_account_management_callback()
logger = logging.getLogger(__name__)


class ManagerAuthorizationDialog(ctk.CTkToplevel):
    """
    A standalone modal dialog for manager authorization.
    Handles passcode verification via MongoDB connection.
    """

    def __init__(self, parent, on_authorized):
        """
        :param parent: Parent frame/window
        :param on_authorized: Callback function executed upon successful passcode verification
        """
        super().__init__(parent)

        self.on_authorized = on_authorized

        # Window Configuration
        self.title("Manager Authorization Required")
        self.geometry("420x250")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="🔒 Manager Authorization",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self,
            text="Enter security passcode to authorize profile changes:",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
        ).pack(pady=(0, 12))

        self.code_entry = ctk.CTkEntry(
            self, show="*", width=220, height=38, justify="center", font=fonts.BODY_TEXT
        )
        self.code_entry.pack(pady=(0, 10))
        self.code_entry.focus_set()
        self.code_entry.bind("<Return>", lambda e: self._verify_passcode())

        self.err_label = ctk.CTkLabel(
            self, text="", font=fonts.SMALL_TEXT, text_color="red"
        )
        self.err_label.pack(pady=(0, 5))

        ctk.CTkButton(
            self,
            text="Authorize & Save",
            height=38,
            width=200,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            command=self._verify_passcode,
        ).pack(pady=(5, 0))

    def _verify_passcode(self):
        entered_code = self.code_entry.get().strip()

        if not entered_code:
            self.err_label.configure(text="Please enter a passcode.")
            return

        try:
            db = get_db()
            admins_col = db["admins"]

            # Get the admin record
            record = admins_col.find_one({})

            if not record:
                self.err_label.configure(
                    text="Admin authorization record not found."
                )
                return

            # Verify entered passcode against bcrypt hash
            stored_hash = record.get("passcode", "")

            if verify_password(entered_code, stored_hash):
                self.destroy()

                if callable(self.on_authorized):
                    self.on_authorized()

            else:
                self.err_label.configure(
                    text="Invalid authorization passcode."
                )

        except Exception as e:
            logger.error(
                f"Error verifying authorization passcode: {e}"
            )
            self.err_label.configure(
                text="Database connection error. Try again."
            )

class AccountBalanceDialog(ctk.CTkToplevel):
    """
    A standalone modal dialog to securely display the live account balance.
    """
    def __init__(self, parent, account_number, balance_val):
        super().__init__(parent)

        self.title("Account Balance Details")
        self.geometry("420x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 140
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui(account_number, balance_val)

    def _build_ui(self, account_number, balance_val):
        ctk.CTkLabel(
            self,
            text="Secure Financial Report",
            font=fonts.DIALOG_TITLE,
            text_color=theme.PRIMARY
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self,
            text=f"Account: {account_number}",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY
        ).pack(pady=(0, 15))
        
        box = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=8,
            border_width=1,
            border_color=theme.BORDER
        )
        box.pack(padx=30, pady=(0, 20), fill="x", ipady=10)

        ctk.CTkLabel(
            box,
            text="Available Balance",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY
        ).pack(pady=(5, 0))

        ctk.CTkLabel(
            box,
            text=f"₹{balance_val:,.2f}",
            font=("Montserrat", 26, "bold"),
            text_color="#16A34A"
        ).pack(pady=(0, 5))

        ctk.CTkButton(
            self,
            text="Close",
            width=140,
            height=36,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.destroy,
            font=fonts.PRIMARY_BUTTON
        ).pack(pady=(0, 20))


class TransactionFundTransferDialog(ctk.CTkToplevel):
    """
    A standalone dialog dedicated specifically to transaction fund transfers.
    """
    def __init__(
        self,
        parent,
        title="Fund Transfer Confirmation",
        message="",
        confirm_text="Confirm Transfer",
        cancel_text="Cancel",
        is_destructive=False,
        on_confirm=None
    ):
        super().__init__(parent)

        self.on_confirm_callback = on_confirm
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.is_destructive = is_destructive
        self.raw_message = message

        # Window Configuration
        self.title(title)
        self.geometry("460x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 230
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 230
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        # Header Container (Icon & Title)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 12))

        icon_lbl = ctk.CTkLabel(
            header_frame,
            text="⇄",
            font=("Montserrat", 28, "bold"),
            text_color=theme.PRIMARY
        )
        icon_lbl.pack()

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Verify Fund Transfer",
            font=fonts.SECTION_TITLE,
            text_color=theme.TEXT
        )
        title_lbl.pack(pady=(2, 0))

        # Main Details Container Card
        card = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER
        )
        card.pack(fill="x", padx=28, pady=(0, 20))

        # Parse message content to display structured rows if it follows standard formatting
        # Fallback to plain label if formatting differs
        try:
            lines = self.raw_message.split("\n")
            # Extract basic details safely
            from_text = ""
            to_text = ""
            amount_text = ""
            warning_text = ""
            
            for idx, line in enumerate(lines):
                if "From:" in line and idx + 1 < len(lines):
                    from_text = lines[idx + 1]
                elif "To:" in line and idx + 1 < len(lines):
                    to_text = lines[idx + 1]
                elif "Amount:" in line:
                    amount_text = line.replace("Amount:", "").strip()
                elif "overdraft" in line.lower():
                    warning_text += line + "\n"

            if from_text and to_text and amount_text:
                # --- Structured Layout ---
                # From Section
                from_frame = ctk.CTkFrame(card, fg_color="transparent")
                from_frame.pack(fill="x", padx=16, pady=(16, 8))
                ctk.CTkLabel(from_frame, text="FROM ACCOUNT", font=("Montserrat", 10, "bold"), text_color="#64748B").pack(anchor="w")
                ctk.CTkLabel(from_frame, text=from_text, font=fonts.BODY_TEXT, text_color=theme.TEXT).pack(anchor="w", pady=(2, 0))

                # Separator line
                ctk.CTkFrame(card, height=1, fg_color="#E2E8F0").pack(fill="x", padx=16)

                # To Section
                to_frame = ctk.CTkFrame(card, fg_color="transparent")
                to_frame.pack(fill="x", padx=16, pady=8)
                ctk.CTkLabel(to_frame, text="TO ACCOUNT", font=("Montserrat", 10, "bold"), text_color="#64748B").pack(anchor="w")
                ctk.CTkLabel(to_frame, text=to_text, font=fonts.BODY_TEXT, text_color=theme.TEXT).pack(anchor="w", pady=(2, 0))

                # Separator line
                ctk.CTkFrame(card, height=1, fg_color="#E2E8F0").pack(fill="x", padx=16)

                # Amount Box Section
                amt_frame = ctk.CTkFrame(card, fg_color="#EEF2F6", corner_radius=6)
                amt_frame.pack(fill="x", padx=16, pady=(8, 16))
                ctk.CTkLabel(amt_frame, text="TRANSFER AMOUNT", font=("Montserrat", 10, "bold"), text_color="#475569").pack(anchor="w", padx=12, pady=(8, 0))
                ctk.CTkLabel(amt_frame, text=amount_text, font=("Montserrat", 20, "bold"), text_color=theme.PRIMARY).pack(anchor="w", padx=12, pady=(0, 8))

                if warning_text:
                    warn_frame = ctk.CTkFrame(card, fg_color="#FEF3C7", corner_radius=6)
                    warn_frame.pack(fill="x", padx=16, pady=(0, 16))
                    ctk.CTkLabel(warn_frame, text=warning_text.strip(), font=fonts.SMALL_TEXT, text_color="#B45309", wraplength=340, justify="left").pack(padx=12, pady=8, anchor="w")

            else:
                raise ValueError("Fallback to raw text")

        except Exception:
            # Fallback wrapper if parsing fails
            msg_label = ctk.CTkLabel(
                card,
                text=self.raw_message,
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT,
                wraplength=380,
                justify="left"
            )
            msg_label.pack(padx=16, pady=16, anchor="w")

        # Button Container
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=28, pady=(0, 24))

        # Cancel / Secondary Action
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=self.cancel_text,
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            width=190,
            height=42,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        # Confirm / Primary Action
        btn_fg = "#EF4444" if self.is_destructive else theme.PRIMARY
        btn_hover = "#DC2626" if self.is_destructive else theme.BUTTON_PRIMARY_HOVER

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=self.confirm_text,
            font=fonts.BUTTON,
            fg_color=btn_fg,
            hover_color=btn_hover,
            text_color="white",
            width=190,
            height=42,
            command=self._handle_confirm
        )
        confirm_btn.pack(side="right")

    def _handle_confirm(self):
        self.destroy()
        if callable(self.on_confirm_callback):
            self.on_confirm_callback()

class TransactionWithdrawalDialog(ctk.CTkToplevel):
    """
    A standalone dialog dedicated specifically to cash withdrawal confirmations.
    """
    def __init__(
        self,
        parent,
        title="Withdrawal Confirmation",
        message="",
        confirm_text="Confirm Withdrawal",
        cancel_text="Cancel",
        is_destructive=False,
        on_confirm=None
    ):
        super().__init__(parent)

        self.on_confirm_callback = on_confirm
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.is_destructive = is_destructive
        self.raw_message = message

        # Window Configuration
        self.title(title)
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 230
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 210
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        # Header Container (Icon & Title)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 12))

        icon_lbl = ctk.CTkLabel(
            header_frame,
            text="💵",
            font=("Montserrat", 24, "bold"),
            text_color=theme.PRIMARY
        )
        icon_lbl.pack()

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Verify Cash Withdrawal",
            font=fonts.SECTION_TITLE,
            text_color=theme.TEXT
        )
        title_lbl.pack(pady=(2, 0))

        # Main Details Container Card
        card = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER
        )
        card.pack(fill="x", padx=28, pady=(0, 5))

        # Parse message content to display structured rows if it follows standard formatting
        # Fallback to plain label if formatting differs
        try:
            lines = self.raw_message.split("\n")
            account_text = ""
            amount_text = ""
            warning_text = ""
            
            for idx, line in enumerate(lines):
                if "Account:" in line and idx + 1 < len(lines):
                    account_text = lines[idx + 1]
                elif "Amount:" in line:
                    amount_text = line.replace("Amount:", "").strip()
                elif "overdraft" in line.lower():
                    warning_text += line + "\n"

            if account_text and amount_text:
                # --- Structured Layout ---
                # Account Section
                acc_frame = ctk.CTkFrame(card, fg_color="transparent")
                acc_frame.pack(fill="x", padx=16, pady=(16, 8))
                ctk.CTkLabel(acc_frame, text="ACCOUNT DETAILS", font=("Montserrat", 10, "bold"), text_color="#64748B").pack(anchor="w")
                ctk.CTkLabel(acc_frame, text=account_text, font=fonts.BODY_TEXT, text_color=theme.TEXT).pack(anchor="w", pady=(2, 0))

                # Separator line
                ctk.CTkFrame(card, height=1, fg_color="#E2E8F0").pack(fill="x", padx=16)

                # Amount Box Section
                amt_frame = ctk.CTkFrame(card, fg_color="#EEF2F6", corner_radius=6)
                amt_frame.pack(fill="x", padx=16, pady=(12, 16))
                ctk.CTkLabel(amt_frame, text="WITHDRAWAL AMOUNT", font=("Montserrat", 10, "bold"), text_color="#475569").pack(anchor="w", padx=12, pady=(8, 0))
                ctk.CTkLabel(amt_frame, text=amount_text, font=("Montserrat", 20, "bold"), text_color=theme.PRIMARY).pack(anchor="w", padx=12, pady=(0, 8))

                if warning_text:
                    warn_frame = ctk.CTkFrame(card, fg_color="#FEF3C7", corner_radius=6)
                    warn_frame.pack(fill="x", padx=16, pady=(0, 16))
                    ctk.CTkLabel(warn_frame, text=warning_text.strip(), font=fonts.SMALL_TEXT, text_color="#B45309", wraplength=340, justify="left").pack(padx=12, pady=8, anchor="w")

            else:
                raise ValueError("Fallback to raw text")

        except Exception:
            # Fallback wrapper if parsing fails
            msg_label = ctk.CTkLabel(
                card,
                text=self.raw_message,
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT,
                wraplength=380,
                justify="left"
            )
            msg_label.pack(padx=16, pady=16, anchor="w")

        # Button Container
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=28, pady=(0, 24))

        # Cancel / Secondary Action
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=self.cancel_text,
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            width=190,
            height=42,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        # Confirm / Primary Action
        btn_fg = "#EF4444" if self.is_destructive else theme.PRIMARY
        btn_hover = "#DC2626" if self.is_destructive else theme.BUTTON_PRIMARY_HOVER

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=self.confirm_text,
            font=fonts.BUTTON,
            fg_color=btn_fg,
            hover_color=btn_hover,
            text_color="white",
            width=190,
            height=42,
            command=self._handle_confirm
        )
        confirm_btn.pack(side="right")

    def _handle_confirm(self):
        self.destroy()
        if callable(self.on_confirm_callback):
            self.on_confirm_callback()

class TransactionDepositDialog(ctk.CTkToplevel):
    """
    A standalone dialog dedicated specifically to cash deposit confirmations.
    """
    def __init__(
        self,
        parent,
        title="Deposit Confirmation",
        message="",
        confirm_text="Confirm Deposit",
        cancel_text="Cancel",
        is_destructive=False,
        on_confirm=None
    ):
        super().__init__(parent)

        self.on_confirm_callback = on_confirm
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.is_destructive = is_destructive
        self.raw_message = message

        # Window Configuration
        self.title(title)
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 230
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 210
        self.geometry(f"+{x}+{y}")

        self.configure(fg_color=theme.BACKGROUND)

        self._build_ui()

    def _build_ui(self):
        # Header Container (Icon & Title)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 12))

        icon_lbl = ctk.CTkLabel(
            header_frame,
            text="💵",
            font=("Montserrat", 24, "bold"),
            text_color=theme.PRIMARY
        )
        icon_lbl.pack()

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Verify Cash Deposit",
            font=fonts.SECTION_TITLE,
            text_color=theme.TEXT
        )
        title_lbl.pack(pady=(2, 0))

        # Main Details Container Card
        card = ctk.CTkFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER
        )
        card.pack(fill="x", padx=28, pady=(0, 5))

        # Parse message content to display structured rows if it follows standard formatting
        # Fallback to plain label if formatting differs
        try:
            lines = self.raw_message.split("\n")
            account_text = ""
            amount_text = ""
            warning_text = ""
            
            for idx, line in enumerate(lines):
                if "Account:" in line and idx + 1 < len(lines):
                    account_text = lines[idx + 1]
                elif "Deposit Amount:" in line:
                    amount_text = line.replace("Deposit Amount:", "").strip()
                elif "overdraft" in line.lower() or "note:" in line.lower():
                    warning_text += line + "\n"

            if account_text and amount_text:
                # --- Structured Layout ---
                # Account Section
                acc_frame = ctk.CTkFrame(card, fg_color="transparent")
                acc_frame.pack(fill="x", padx=16, pady=(16, 8))
                ctk.CTkLabel(acc_frame, text="ACCOUNT DETAILS", font=("Montserrat", 10, "bold"), text_color="#64748B").pack(anchor="w")
                ctk.CTkLabel(acc_frame, text=account_text, font=fonts.BODY_TEXT, text_color=theme.TEXT).pack(anchor="w", pady=(2, 0))

                # Separator line
                ctk.CTkFrame(card, height=1, fg_color="#E2E8F0").pack(fill="x", padx=16)

                # Amount Box Section
                amt_frame = ctk.CTkFrame(card, fg_color="#EEF2F6", corner_radius=6)
                amt_frame.pack(fill="x", padx=16, pady=(12, 16))
                ctk.CTkLabel(amt_frame, text="DEPOSIT AMOUNT", font=("Montserrat", 10, "bold"), text_color="#475569").pack(anchor="w", padx=12, pady=(8, 0))
                ctk.CTkLabel(amt_frame, text=amount_text, font=("Montserrat", 20, "bold"), text_color=theme.PRIMARY).pack(anchor="w", padx=12, pady=(0, 8))

                if warning_text:
                    warn_frame = ctk.CTkFrame(card, fg_color="#FEF3C7", corner_radius=6)
                    warn_frame.pack(fill="x", padx=16, pady=(0, 16))
                    ctk.CTkLabel(warn_frame, text=warning_text.strip(), font=fonts.SMALL_TEXT, text_color="#B45309", wraplength=340, justify="left").pack(padx=12, pady=8, anchor="w")

            else:
                raise ValueError("Fallback to raw text")

        except Exception:
            # Fallback wrapper if parsing fails
            msg_label = ctk.CTkLabel(
                card,
                text=self.raw_message,
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT,
                wraplength=380,
                justify="left"
            )
            msg_label.pack(padx=16, pady=16, anchor="w")

        # Button Container
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=28, pady=(0, 24))

        # Cancel / Secondary Action
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=self.cancel_text,
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            width=190,
            height=42,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        # Confirm / Primary Action
        btn_fg = "#EF4444" if self.is_destructive else theme.PRIMARY
        btn_hover = "#DC2626" if self.is_destructive else theme.BUTTON_PRIMARY_HOVER

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=self.confirm_text,
            font=fonts.BUTTON,
            fg_color=btn_fg,
            hover_color=btn_hover,
            text_color="white",
            width=190,
            height=42,
            command=self._handle_confirm
        )
        confirm_btn.pack(side="right")

    def _handle_confirm(self):
        self.destroy()
        if callable(self.on_confirm_callback):
            self.on_confirm_callback()

class TransactionHistoryDialog(ctk.CTkToplevel):
    # Match the exact fixed column configuration widths used across tables
    TABLE_COLUMNS = [180, 200, 200, 150, 150, 150, 190]
    TABLE_HEADERS = ["Date / Time", "Type / ID", "Account / Cust", "Debit (₹)", "Credit (₹)", "Balance (₹)", "Remarks"]

    def __init__(self, parent, account_number, transaction_service=None):
        super().__init__(parent)
        
        self.account_number = account_number
        self.transaction_service = transaction_service or TransactionService()

        self.title(f"Transaction History - {self.account_number}")
        self.geometry("1090x580")
        self.minsize(850, 480)

        # Make window modal
        self.transient(parent)
        self.grab_set()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_table_container()
        self.load_transactions()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=theme.PRIMARY, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)

        title_lbl = ctk.CTkLabel(
            header_frame,
            text=f"Permanent Transaction Records for Account: {self.account_number}",
            font=fonts.SECTION_TITLE,
            text_color="white"
        )
        title_lbl.pack(side="left", padx=20, pady=15)

        self.record_count_lbl = ctk.CTkLabel(
            header_frame,
            text="Showing 0 records",
            font=fonts.SMALL_TEXT,
            text_color="#E2E8F0"
        )
        self.record_count_lbl.pack(side="right", padx=20, pady=15)

    def _build_table_container(self):
        table_card = ctk.CTkFrame(self, fg_color=theme.BACKGROUND, corner_radius=0)
        table_card.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        # Table Header Frame
        self.table_header = ctk.CTkFrame(table_card, fg_color="#E2E8F0", corner_radius=4, height=35)
        self.table_header.grid(row=0, column=0, sticky="ew", pady=(0, 4), padx=2)
        self.table_header.grid_propagate(False)

        self._configure_columns(self.table_header)
        self._create_table_header()

        # Scrollable Frame for rows
        self.table_scroll = ctk.CTkScrollableFrame(table_card, fg_color="#F8FAFC", corner_radius=8)
        self.table_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 0))
        self.table_scroll.columnconfigure(0, weight=1)

    # =========================================================
    # TABLE COLUMN CONFIGURATION
    # =========================================================

    def _configure_columns(self, frame):
        """
        Every table frame uses the SAME column widths.

        IMPORTANT:
        We intentionally do NOT use column weights here.

        Using weights caused every row to calculate its own
        column sizes, which created the misalignment.
        """
        for index, width in enumerate(
            self.TABLE_COLUMNS
        ):
            frame.columnconfigure(
                index,
                minsize=width,
                weight=0
            )

    # =========================================================
    # TABLE HEADER
    # =========================================================

    def _create_table_header(self):
        for index, title in enumerate(
            self.TABLE_HEADERS
        ):
            if index in (3, 4, 5):
                anchor = "e"
            else:
                anchor="center"

            label = ctk.CTkLabel(
                self.table_header,
                text=title,
                font=fonts.TABLE_HEADER,
                text_color=theme.TEXT,
                anchor=anchor
            )

            label.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=10,
                pady=0
            )

    # =========================================================
    # LOAD DATA
    # =========================================================

    def load_transactions(self):
        try:
            all_txs = self.transaction_service.get_all_transactions()
            
            # Filter strictly for the specific account inside this dialog modal
            self.transactions_data = [
                tx for tx in all_txs 
                if tx.get("account_number") == self.account_number 
                or tx.get("from_account") == self.account_number 
                or tx.get("to_account") == self.account_number
            ]

            self.filtered_data = list(
                self.transactions_data
            )

            self.render_table()

        except Exception as e:
            self.record_count_lbl.configure(text="Database Error")
            self.filtered_data = []
            self.render_table()

    # =========================================================
    # RENDER TABLE
    # =========================================================

    def render_table(self):
        # Remove previous rows
        for widget in (
            self.table_scroll.winfo_children()
        ):
            widget.destroy()

        self.record_count_lbl.configure(
            text=(
                f"Showing "
                f"{len(self.filtered_data)} "
                f"records"
            )
        )

        # -----------------------------------------------------
        # EMPTY STATE
        # -----------------------------------------------------

        if not self.filtered_data:
            empty_label = ctk.CTkLabel(
                self.table_scroll,
                text=(
                    "No transaction records found "
                    "for this account."
                ),
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY
            )

            empty_label.grid(
                row=0,
                column=0,
                pady=40
            )

            return

        # -----------------------------------------------------
        # TRANSACTION ROWS
        # -----------------------------------------------------

        for row_index, tx in enumerate(
            self.filtered_data
        ):
            row_bg = (
                "#FFFFFF"
                if row_index % 2 == 0
                else "#F8FAFC"
            )

            row_frame = ctk.CTkFrame(
                self.table_scroll,
                fg_color=row_bg,
                corner_radius=4
            )

            row_frame.grid(
                row=row_index,
                column=0,
                sticky="w",
                pady=(0, 2)
            )

            # IMPORTANT:
            # Same exact column widths as header
            self._configure_columns(
                row_frame
            )

            # -------------------------------------------------
            # DATE
            # -------------------------------------------------

            date_str = str(
                tx.get(
                    "created_at",
                    "—"
                )
            )

            # -------------------------------------------------
            # TYPE / ID
            # -------------------------------------------------

            tx_type = tx.get(
                "transaction_type",
                "Transaction"
            )

            tx_id = tx.get(
                "transaction_id",
                ""
            )

            if tx_id:
                type_id_display = (
                    f"{tx_type}\n"
                    f"{tx_id}"
                )
            else:
                type_id_display = tx_type

            # -------------------------------------------------
            # ACCOUNT / CUSTOMER
            # -------------------------------------------------

            account_number = (
                tx.get("account_number")
                or tx.get("from_account")
                or "—"
            )

            destination = tx.get(
                "to_account"
            )

            if destination:
                account_display = (
                    f"{account_number}\n"
                    f"→ {destination}"
                )
            else:
                account_display = account_number

            customer_id = tx.get(
                "customer_id"
            )

            # Transfers use from_customer_id
            if not customer_id:
                customer_id = tx.get(
                    "from_customer_id"
                )

            if customer_id:
                account_customer_display = (
                    f"{account_display}\n"
                    f"ID: {customer_id}"
                )
            else:
                account_customer_display = (
                    account_display
                )

            # -------------------------------------------------
            # AMOUNT
            # -------------------------------------------------

            try:
                amount = float(
                    tx.get(
                        "amount",
                        0
                    )
                )
            except (
                TypeError,
                ValueError
            ):
                amount = 0.0

            # -------------------------------------------------
            # DEBIT / CREDIT
            # -------------------------------------------------

            is_credit = (
                tx_type in (
                    "Cash Deposit",
                    "Initial Deposit"
                )
                or bool(
                    tx.get(
                        "overdraft_reset",
                        False
                    )
                )
            )

            if tx_type == "Funds Transfer":
                if tx.get("from_account") == self.account_number:
                    # This account sent the money
                    debit = f"₹{amount:,.2f}"
                    credit = "—"

                elif tx.get("to_account") == self.account_number:
                    # This account received the money
                    debit = "—"
                    credit = f"₹{amount:,.2f}"

                else:
                    debit = "—"
                    credit = "—"

            elif is_credit:
                debit = "—"
                credit = f"₹{amount:,.2f}"

            else:
                debit = f"₹{amount:,.2f}"
                credit = "—"
           
            # -------------------------------------------------
            # BALANCE
            # -------------------------------------------------

            if tx_type == "Funds Transfer":

                if tx.get("from_account") == self.account_number:
                    # Sender's balance after the transfer
                    balance_value = tx.get(
                        "from_balance_after"
                    )

                elif tx.get("to_account") == self.account_number:
                    # Receiver's balance after the transfer
                    balance_value = tx.get(
                        "to_balance_after"
                    )

                else:
                    balance_value = None

            else:

                balance_value = tx.get(
                    "balance_after"
                )

                if balance_value is None:
                    balance_value = tx.get(
                        "balance"
                    )

                if balance_value is None:
                    balance_value = tx.get(
                        "new_balance"
                    )

            if balance_value is None:
                balance = "—"
            else:
                try:
                    balance = (
                        f"₹"
                        f"{float(balance_value):,.2f}"
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    balance = "—"

            # -------------------------------------------------
            # REMARKS
            # -------------------------------------------------

            remarks = (
                tx.get(
                    "failure_reason"
                )
                or tx.get(
                    "status"
                )
                or "Completed"
            )

            # -------------------------------------------------
            # ALL VALUES
            # -------------------------------------------------

            values = [
                date_str,
                type_id_display,
                account_customer_display,
                debit,
                credit,
                balance,
                remarks
            ]

            # -------------------------------------------------
            # CREATE CELLS
            # -------------------------------------------------

            for column_index, value in enumerate(
                values
            ):
                # ---------------------------------------------
                # ALIGNMENT
                # ---------------------------------------------

                if column_index in (
                    3,
                    4
                ):
                    # Money → right aligned
                    anchor = "e"
                    justify = "left"

                elif column_index == 5:
                    anchor = "center"
                    justify = "center"

                elif column_index == 6:
                    # Remarks → CENTER
                    anchor = "center"
                    justify = "left"

                else:
                    anchor = "w"
                    justify = "left"

                # ---------------------------------------------
                # WRAPPING
                # ---------------------------------------------

                if column_index == 1:
                    wrap_length = (
                        self.TABLE_COLUMNS[1] - 20
                    )

                elif column_index == 2:
                    wrap_length = (
                        self.TABLE_COLUMNS[2] - 20
                    )

                elif column_index == 6:
                    wrap_length = (
                        self.TABLE_COLUMNS[6] - 20
                    )

                else:
                    wrap_length = 0

                # ---------------------------------------------
                # CELL
                # ---------------------------------------------

                cell = ctk.CTkLabel(
                    row_frame,
                    text=str(value),
                    font=fonts.TABLE_TEXT,
                    text_color=theme.TEXT,
                    fg_color=row_bg,
                    anchor=anchor,
                    justify=justify,
                    wraplength=wrap_length
                )

                cell.grid(
                    row=0,
                    column=column_index,
                    # IMPORTANT:
                    # Small horizontal padding only.
                    # No large vertical padding.
                    padx=10,
                    pady=6,
                    sticky="ew"
                )