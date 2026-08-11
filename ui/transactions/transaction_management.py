import logging
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from core import theme, fonts

logger = logging.getLogger(__name__)


class TransactionManagementPage(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        on_back,
        on_deposit=None,
        on_withdraw=None,
        on_transfer=None,
        on_history=None,
    ):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.on_deposit = on_deposit
        self.on_withdraw = on_withdraw
        self.on_transfer = on_transfer
        self.on_history = on_history

        self._create_layout()
        self.pack(fill="both", expand=True)

    def _create_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Header Navigation Bar
        self.build_header()

        # 2. Main Scrollable Container
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.PRIMARY,
            scrollbar_button_hover_color=theme.BUTTON_PRIMARY_HOVER,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=50, pady=20)

        # 3. Main Body Content
        self._build_body()

    def build_header(self):
        self.header = ctk.CTkFrame(
            self, height=70, fg_color=theme.PRIMARY, corner_radius=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        # Left Side: Logo and System Title
        left = ctk.CTkFrame(self.header, fg_color="transparent")
        left.pack(side="left", padx=25, pady=10)

        # Safe Logo Image Loader
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
            else:
                logger.warning(f"Logo asset not found at path: {logo_path}")
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

        # Right Side: Return Dashboard Button
        right = ctk.CTkFrame(self.header, fg_color="transparent")
        right.pack(side="right", padx=25, pady=10)

        back_btn = ctk.CTkButton(
            right,
            text="Return Dashboard",
            width=110,
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
        # Page Title & Subtitle
        page_title = ctk.CTkLabel(
            self.content,
            text="Transaction Operations Hub",
            font=("Montserrat", 26, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        )
        page_title.pack(fill="x", pady=(10, 2))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Deposit funds, process withdrawals, transfer money between accounts, and view complete transaction histories.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle.pack(fill="x", pady=(0, 25))

        # Section 1: 2x2 Grid Action Cards (Deposit, Withdraw, Transfer, History)
        self._build_action_cards()

        # Section 2: Operational Guidelines & Compliance Protocol
        self._build_rules_section()

    def _build_action_cards(self):
        cards_container = ctk.CTkFrame(
            self.content, fg_color="transparent", width=1200, height=680
        )
        cards_container.pack_propagate(False)
        cards_container.grid_propagate(False)
        cards_container.pack(anchor="w", pady=(0, 25))

        # 2x2 Grid setup
        cards_container.columnconfigure((0, 1), weight=1, uniform="tx_cards")
        cards_container.rowconfigure((0, 1), weight=1, uniform="tx_rows")

        cards_data = [
            {
                "col": 0,
                "row": 0,
                "padding": ((0, 12), (0, 12)),
                "title": "💵  Deposit Funds",
                "desc": "Deposit funds into an active customer account while automatically updating the account balance and recording the transaction.",
                "features": [
                    "Search account by Account Number or Customer ID",
                    "Automatically updates the account balance",
                    "Creates a permanent Credit transaction record",
                ],
                "btn_text": "Initiate Deposit",
                "command": self.on_deposit,
            },
            {
                "col": 1,
                "row": 0,
                "padding": ((12, 0), (0, 12)),
                "title": "🏧  Withdraw Funds",
                "desc": "Withdraw funds from an active account after validating the available balance and recording the transaction.",
                "features": [
                    "Prevents withdrawal beyond the available balance",
                    "Automatically updates the account balance",
                    "Creates a permanent Debit transaction record",
                ],
                "btn_text": "Initiate Withdrawal",
                "command": self.on_withdraw,
            },
            {
                "col": 0,
                "row": 1,
                "padding": ((0, 12), (12, 0)),
                "title": "🔄  Fund Transfer",
                "desc": "Transfer funds securely between two active customer accounts with automatic balance updates on both accounts.",
                "features": [
                    "Direct internal account-to-account transfers",
                    "Validates both source and destination accounts",
                    "Updates balances for both accounts automatically",
                ],
                "btn_text": "Initiate Transfer",
                "command": self.on_transfer,
            },
            {
                "col": 1,
                "row": 1,
                "padding": ((12, 0), (12, 0)),
                "title": "📜  Transaction History",
                "desc": "View the complete transaction history of an account, including deposits, withdrawals, transfers, initial deposits, and account closure records.",
                "features": [
                    "Filter by date, transaction type, account number or customer id",
                    "Displays Debit, Credit, Balance, Date, and Remarks",
                    "Read-only transaction history with permanent records",
                ],
                "btn_text": "Open Transaction History",
                "command": self.on_history,
            },
        ]

        for card_info in cards_data:
            c_frame = ctk.CTkFrame(
                cards_container,
                fg_color=theme.CARD,
                corner_radius=12,
                border_width=1,
                border_color=theme.BORDER,
            )
            c_frame.grid(
                row=card_info["row"],
                column=card_info["col"],
                padx=card_info["padding"][0],
                pady=card_info["padding"][1],
                sticky="nsew",
            )

            accent = ctk.CTkFrame(
                c_frame, height=6, fg_color=theme.PRIMARY, corner_radius=0
            )
            accent.pack(fill="x", side="top")

            inner = ctk.CTkFrame(c_frame, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=25, pady=25)

            title = ctk.CTkLabel(
                inner,
                text=card_info["title"],
                font=fonts.SECTION_TITLE,
                text_color=theme.PRIMARY,
                anchor="w",
            )
            title.pack(fill="x", pady=(0, 10))

            desc = ctk.CTkLabel(
                inner,
                text=card_info["desc"],
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY,
                justify="left",
                wraplength=400,
                anchor="w",
            )
            desc.pack(fill="x", pady=(0, 18))

            for feat in card_info["features"]:
                f_row = ctk.CTkFrame(inner, fg_color="transparent")
                f_row.pack(anchor="w", pady=4)

                bullet = ctk.CTkLabel(
                    f_row,
                    text="•",
                    font=fonts.CARD_TITLE,
                    text_color=theme.PRIMARY,
                )
                bullet.pack(side="left", padx=(0, 10))

                txt = ctk.CTkLabel(
                    f_row,
                    text=feat,
                    font=fonts.BODY_TEXT,
                    text_color=theme.TEXT,
                )
                txt.pack(side="left")

            btn = ctk.CTkButton(
                inner,
                text=card_info["btn_text"],
                height=44,
                corner_radius=8,
                fg_color=theme.PRIMARY,
                hover_color=theme.BUTTON_PRIMARY_HOVER,
                font=fonts.PRIMARY_BUTTON,
                command=card_info["command"],
            )
            btn.pack(fill="x", side="bottom")

    def _build_rules_section(self):
        """Operational Guidelines & Compliance Protocol Section"""
        rules_card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=14,
            border_width=1,
            border_color=theme.BORDER,
        )
        rules_card.pack(fill="x", pady=(10, 25))

        # Section Header
        rules_header_frame = ctk.CTkFrame(rules_card, fg_color="transparent")
        rules_header_frame.pack(fill="x", padx=25, pady=(20, 6))

        rules_title = ctk.CTkLabel(
            rules_header_frame,
            text="Transaction Controls & Operational Protocol",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        )
        rules_title.pack(anchor="w")

        rules_subtitle = ctk.CTkLabel(
            rules_card,
            text="Ensure strict adherence to financial processing guidelines and ledger reconciliation standards.",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY,
        )
        rules_subtitle.pack(anchor="w", padx=25, pady=(0, 18))

        # Protocol Grid (2 Columns x 2 Rows)
        grid_container = ctk.CTkFrame(rules_card, fg_color="transparent")
        grid_container.pack(fill="x", padx=20, pady=(0, 20))
        grid_container.grid_columnconfigure(
            (0, 1), weight=1, uniform="protocol_cols"
        )

        protocols = [
            (
                "💳 Account Validation",
                "Transactions are permitted only for active accounts. Closed accounts cannot perform deposits, withdrawals, or transfers.",
            ),
            (
                "🔒 Balance & Overdraft Protection",
                "Savings accounts cannot withdraw beyond the available balance. Current accounts may withdraw within their approved overdraft limit. Transactions exceeding the available balance or overdraft limit are automatically blocked.",
            ),
            (
                "📝 Permanent Transaction Records",
                "Every deposit, withdrawal, transfer, initial deposit, and account closure is permanently recorded in the transaction history.",
            ),
            (
                "📜 Read-Only Transaction History",
                "Transaction history is available for viewing only and cannot be edited, deleted, or downloaded, ensuring a complete financial record.",
            ),
        ]

        box_bg = ("#F8FAFC", "#1E293B")
        box_border = ("#E2E8F0", "#334155")

        for index, (title_text, desc_text) in enumerate(protocols):
            col = index % 2
            row = index // 2

            rule_box = ctk.CTkFrame(
                grid_container,
                fg_color=box_bg,
                corner_radius=10,
                border_width=1,
                border_color=box_border,
            )
            rule_box.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

            r_title = ctk.CTkLabel(
                rule_box,
                text=title_text,
                font=fonts.BODY_TEXT,
                text_color=theme.PRIMARY,
                anchor="w",
            )
            r_title.pack(fill="x", padx=16, pady=(14, 4))

            r_desc = ctk.CTkLabel(
                rule_box,
                text=desc_text,
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY,
                justify="left",
                anchor="w",
                wraplength=520,
            )
            r_desc.pack(fill="x", padx=16, pady=(0, 14))