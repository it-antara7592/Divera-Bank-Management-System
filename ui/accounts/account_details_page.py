import logging
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from core import theme, fonts
from services.account_service import AccountService
from ui.components.dialogs import ManagerAuthorizationDialog
from ui.components.dialogs import AccountBalanceDialog
from ui.components.dialogs import TransactionHistoryDialog
from services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class AccountDetailsPage(ctk.CTkFrame):

    def __init__(self, parent, account_data, on_back, on_refresh_parent=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.on_refresh_parent = on_refresh_parent
        self.account_data = account_data
        self.account_number = account_data.get("account_number")
        self.service = AccountService()

        self._create_layout()
        self.pack(fill="both", expand=True)

    def _create_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()

        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.PRIMARY,
            scrollbar_button_hover_color=theme.BUTTON_PRIMARY_HOVER,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)

        self._build_body()

    def _build_header(self):
        self.header = ctk.CTkFrame(
            self, height=70, fg_color=theme.PRIMARY, corner_radius=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        left = ctk.CTkFrame(self.header, fg_color="transparent")
        left.pack(side="left", padx=25, pady=10)

        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        logo_path = BASE_DIR / "assets" / "icons" / "divera-bank-logo.png"

        try:
            if logo_path.exists():
                image = Image.open(logo_path)
                self.logo = ctk.CTkImage(
                    light_image=image, dark_image=image, size=(36, 36)
                )
                logo = ctk.CTkLabel(left, image=self.logo, text="")
                logo.pack(side="left", padx=(0, 12))
        except Exception as e:
            logger.error(f"Failed loading header logo image: {e}")

        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")

        bank = ctk.CTkLabel(
            title_frame,
            text="Divera Banking Management System",
            font=fonts.NAVBAR,
            text_color="white",
        )
        bank.pack(anchor="w")

        right = ctk.CTkFrame(self.header, fg_color="transparent")
        right.pack(side="right", padx=25, pady=10)

        back_btn = ctk.CTkButton(
            right,
            text="Back to Management",
            width=140,
            height=36,
            corner_radius=8,
            fg_color=theme.BUTTON_PRIMARY_HOVER,
            hover_color="#0F172A",
            text_color="white",
            font=fonts.BUTTON,
            command=self.on_back,
        )
        back_btn.pack(side="right")

    def _build_body(self):
        # Title & Subtitle
        page_title = ctk.CTkLabel(
            self.content,
            text=f"Account Details: {self.account_number}",
            font=fonts.PAGE_TITLE,
            text_color=theme.PRIMARY,
            anchor="w",
        )
        page_title.pack(fill="x", pady=(5, 2))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Inspect financial standing, check secure balances from database, review configurations, and process lifecycle triggers.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle.pack(fill="x", pady=(0, 20))

        # Main Info Grid Card
        info_card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        info_card.pack(fill="x", pady=(0, 15))

        inner_card = ctk.CTkFrame(info_card, fg_color="transparent")
        inner_card.pack(fill="x", padx=30, pady=25)

        # Left Column: Account Core Metadata
        meta_frame = ctk.CTkFrame(inner_card, fg_color="transparent")
        meta_frame.pack(side="left", fill="both", expand=True)

        self._add_info_row(meta_frame, "Customer ID:", self.account_data.get("customer_id", "N/A"))
        self._add_info_row(meta_frame, "Customer Name:", self.account_data.get("customer_name", "N/A"))
        self._add_info_row(meta_frame, "Account Type:", self.account_data.get("account_type", "N/A"))
        self._add_info_row(meta_frame, "Opening Date:", self.account_data.get("opening_date", "N/A"))
        self._add_info_row(meta_frame, "Account Status:", self.account_data.get("status", "Active"), is_bold=True)

        # Right Column: Financial Secure Summary Card
        fin_frame = ctk.CTkFrame(
            inner_card,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER,
        )
        fin_frame.pack(side="right", fill="both", expand=True, padx=(25, 0), ipady=5)

        fin_title = ctk.CTkLabel(
            fin_frame,
            text="Financial Standing",
            font=fonts.CARD_TITLE,
            text_color=theme.PRIMARY,
            anchor="w",
        )
        fin_title.pack(fill="x", padx=20, pady=(18, 12))

        # Explicitly structured Overdraft Row matching exact horizontal paddings
        if self.account_data.get("account_type") == "Current":
            overdraft = self.account_data.get("overdraft", 50000.0)
            
            overdraft_row = ctk.CTkFrame(fin_frame, fg_color="transparent")
            overdraft_row.pack(fill="x", padx=20, pady=(0, 10))

            overdraft_lbl = ctk.CTkLabel(
                overdraft_row,
                text="Overdraft Limit:",
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY,
                width=130,
                anchor="w",
            )
            overdraft_lbl.pack(side="left")

            overdraft_val = ctk.CTkLabel(
                overdraft_row,
                text=f"₹{overdraft:,.2f}",
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT,
                anchor="w",
            )
            overdraft_val.pack(side="left", fill="x", expand=True)

        # Secure Balance Action Container inside the financial summary card
        balance_action_frame = ctk.CTkFrame(fin_frame, fg_color="transparent")
        balance_action_frame.pack(fill="x", padx=20, pady=(4, 18))

        bal_lbl = ctk.CTkLabel(
            balance_action_frame,
            text="Account Balance:",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            width=130,
            anchor="w",
        )
        bal_lbl.pack(side="left")

        inspect_bal_btn = ctk.CTkButton(
            balance_action_frame,
            text="🔒 Reveal Balance",
            width=145,
            height=36,
            corner_radius=6,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.SECONDARY_BUTTON,
            command=self._prompt_admin_authorization,
        )
        inspect_bal_btn.pack(side="left", padx=(5, 0))

        # Actions Card Section (Toolbar Actions)
        actions_card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        actions_card.pack(fill="x", pady=(0, 20))

        actions_inner = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_inner.pack(fill="x", padx=30, pady=20)

        action_label = ctk.CTkLabel(
            actions_inner,
            text="Account Management Actions",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        )
        action_label.pack(side="left", padx=(0, 15))

        btn_container = ctk.CTkFrame(actions_inner, fg_color="transparent")
        btn_container.pack(side="right")

        # History Button
        history_btn = ctk.CTkButton(
            btn_container,
            text="Transaction History",
            height=40,
            width=160,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            command=self._on_view_transactions,
        )
        history_btn.pack(side="left", padx=8)

        # Close Account Button
        is_closed = self.account_data.get("status") == "Closed"
        close_btn_color = "#DC2626" if not is_closed else "#94A3B8"
        
        self.close_btn = ctk.CTkButton(
            btn_container,
            text="Close Account" if not is_closed else "Account Closed",
            height=40,
            width=150,
            corner_radius=8,
            fg_color=close_btn_color,
            hover_color="#B91C1C" if not is_closed else "#94A3B8",
            font=fonts.PRIMARY_BUTTON,
            state="disabled" if is_closed else "normal",
            command=self._on_close_account_click,
        )
        self.close_btn.pack(side="left", padx=8)

        # Notification / Status Banner Area
        self.msg_label = ctk.CTkLabel(
            self.content, text="", font=fonts.SMALL_TEXT, text_color="green", anchor="w"
        )
        self.msg_label.pack(fill="x", pady=(0, 10))

    def _add_info_row(self, parent, label_text, value_text, is_bold=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            width=140,
            anchor="w",
        )
        lbl.pack(side="left")

        val_font = fonts.SUCCESS if is_bold else fonts.BODY_TEXT
        val = ctk.CTkLabel(
            row,
            text=value_text,
            font=val_font,
            text_color=theme.PRIMARY if is_bold else theme.TEXT,
            anchor="w",
        )
        val.pack(side="left", fill="x", expand=True)

    def _prompt_admin_authorization(self):
        """Triggers the manager authorization dialog, checking MongoDB passcodes."""
        ManagerAuthorizationDialog(
            parent=self,
            on_authorized=self._fetch_and_show_balance_dialog
        )

    def _fetch_and_show_balance_dialog(self):
        """Fetches the live balance securely from MongoDB via service layer and opens balance dialog."""
        try:
            balance_val = self.service.get_account_balance(self.account_number)
        except Exception as e:
            logger.error(f"Failed to fetch live balance from service: {e}")
            balance_val = self.account_data.get("balance", 0.0)

        # Open the large centered modal dialog from dialogs.py
        AccountBalanceDialog(
            parent=self,
            account_number=self.account_number,
            balance_val=balance_val
        )

    # def _on_view_transactions(self):
    #     """Handler to invoke transaction history views."""
    #     self.msg_label.configure(text=f"Loading transaction ledger for {self.account_number}...", text_color=theme.PRIMARY)

    def _on_view_transactions(self):
        """Handler to invoke transaction history modal dialog."""
        self.msg_label.configure(text="")
        
        # Instantiate TransactionService and pass it to match the dialog signature
        from services.transaction_service import TransactionService
        tx_service = TransactionService()
        
        TransactionHistoryDialog(
            parent=self,
            account_number=self.account_number,
            transaction_service=tx_service
        )

    def _on_close_account_click(self):
        """Triggers business logic validation & account closure execution."""
        success, message = self.service.close_account(self.account_number)
        if success:
            self.msg_label.configure(text=message, text_color="green")
            self.account_data["status"] = "Closed"
            self.close_btn.configure(text="Account Closed", fg_color="#94A3B8", state="disabled")
            if self.on_refresh_parent:
                self.on_refresh_parent()
        else:
            self.msg_label.configure(text=message, text_color="#DC2626")