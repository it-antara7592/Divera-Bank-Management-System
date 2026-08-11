import logging
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from core import theme, fonts

logger = logging.getLogger(__name__)


class AccountManagementPage(ctk.CTkFrame):

    def __init__(self, parent, on_back, on_create=None, on_view=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.on_create = on_create
        self.on_view = on_view

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
            text="Account Management Hub",
            font=("Montserrat", 26, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        )
        page_title.pack(fill="x", pady=(10, 2))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Open new bank accounts, manage deposit categories, and oversee account statuses across client profiles.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle.pack(fill="x", pady=(0, 25))

        # Section 1: Action Cards
        self._build_action_cards()

        # Section 2: Enhanced System Protocol & Rules
        self._build_rules_section()

    def _build_action_cards(self):
        cards_container = ctk.CTkFrame(
            self.content, fg_color="transparent", width=1200, height=330
        )
        cards_container.pack_propagate(False)
        cards_container.grid_propagate(False)
        cards_container.pack(anchor="w", pady=(0, 25))

        cards_container.columnconfigure((0, 1), weight=1, uniform="cards")
        cards_container.rowconfigure(0, weight=1)

        # --- CARD 1: OPEN NEW ACCOUNT ---
        card1 = ctk.CTkFrame(
            cards_container,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        card1.grid(row=0, column=0, padx=(0, 12), sticky="nsew")

        accent1 = ctk.CTkFrame(
            card1, height=6, fg_color=theme.PRIMARY, corner_radius=0
        )
        accent1.pack(fill="x", side="top")

        c1_inner = ctk.CTkFrame(card1, fg_color="transparent")
        c1_inner.pack(fill="both", expand=True, padx=25, pady=25)

        c1_title = ctk.CTkLabel(
            c1_inner,
            text="💳  Open New Account",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
            anchor="w",
        )
        c1_title.pack(fill="x", pady=(0, 10))

        c1_desc = ctk.CTkLabel(
            c1_inner,
            text="Initiate creation of new savings, current, or term deposit accounts linked to registered customers.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            justify="left",
            wraplength=400,
            anchor="w",
        )
        c1_desc.pack(fill="x", pady=(0, 18))

        c1_features = [
            "Link account to verified Customer Identification Number (CIF)",
            "Configure initial deposit, currency, and overdraft limits",
            "Generate unique Account Number for both Savings and Current accounts",
        ]

        for feat in c1_features:
            f_row = ctk.CTkFrame(c1_inner, fg_color="transparent")
            f_row.pack(anchor="w", pady=4)

            bullet = ctk.CTkLabel(
                f_row, text="•", font=fonts.CARD_TITLE, text_color=theme.PRIMARY
            )
            bullet.pack(side="left", padx=(0, 10))

            txt = ctk.CTkLabel(
                f_row, text=feat, font=fonts.BODY_TEXT, text_color=theme.TEXT
            )
            txt.pack(side="left")

        create_btn = ctk.CTkButton(
            c1_inner,
            text="Open New Account",
            height=44,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            command=self.on_create,
        )
        create_btn.pack(fill="x", pady=(25, 0))

        # --- CARD 2: VIEW & MANAGE ACCOUNTS ---
        card2 = ctk.CTkFrame(
            cards_container,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        card2.grid(row=0, column=1, padx=(12, 0), sticky="nsew")

        accent2 = ctk.CTkFrame(
            card2, height=6, fg_color=theme.PRIMARY, corner_radius=0
        )
        accent2.pack(fill="x", side="top")

        c2_inner = ctk.CTkFrame(card2, fg_color="transparent")
        c2_inner.pack(fill="both", expand=True, padx=25, pady=25)

        c2_title = ctk.CTkLabel(
            c2_inner,
            text="📂  Account Directory & Operations",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
            anchor="w",
        )
        c2_title.pack(fill="x", pady=(0, 10))

        c2_desc = ctk.CTkLabel(
            c2_inner,
            text="Search central account ledger to inspect balances, modify limits, or manage account status flags.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            justify="left",
            wraplength=400,
            anchor="w",
        )
        c2_desc.pack(fill="x", pady=(0, 18))

        c2_features = [
            "Filter accounts by Account Number or Customer ID",
            "Close accounts safely while retaining full historical audit records in the database",
            "Inspect real-time account ledger balances and status",
        ]

        for feat in c2_features:
            f_row = ctk.CTkFrame(c2_inner, fg_color="transparent")
            f_row.pack(anchor="w", pady=4)

            bullet = ctk.CTkLabel(
                f_row, text="•", font=fonts.CARD_TITLE, text_color=theme.PRIMARY
            )
            bullet.pack(side="left", padx=(0, 10))

            txt = ctk.CTkLabel(
                f_row, text=feat, font=fonts.BODY_TEXT, text_color=theme.TEXT
            )
            txt.pack(side="left")

        view_btn = ctk.CTkButton(
            c2_inner,
            text="Open Account Directory",
            height=44,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            command=self.on_view,
        )
        view_btn.pack(fill="x", pady=(25, 0))

    def _build_rules_section(self):
        """Operational Guidelines & Compliance Protocol Section (Full Width Text)"""
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
            text="Operational Guidelines & Compliance Protocol",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        )
        rules_title.pack(anchor="w")

        rules_subtitle = ctk.CTkLabel(
            rules_card,
            text="Adhere strictly to account management rules, ledger integrity, and banking compliance standards.",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY,
        )
        rules_subtitle.pack(anchor="w", padx=25, pady=(0, 18))

        # Protocol Grid (2 Columns x 2 Rows)
        grid_container = ctk.CTkFrame(rules_card, fg_color="transparent")
        grid_container.pack(fill="x", padx=20, pady=(0, 20))
        grid_container.grid_columnconfigure((0, 1), weight=1, uniform="protocol_cols")

        protocols = [
            (
                "📋 Minimum Balance Maintenance",
                "Ensure newly opened savings and current accounts satisfy initial minimum funding requirements per regulatory guidelines.",
            ),
            (
                "🔒 Account Status & Restrictions",
                "Accounts flagged for closure or inactivity are safely archived or marked as closed. Hard deletion from the database is strictly prohibited to preserve financial audit trails.",
            ),
            (
                "🛡 KYC Profile Linking",
                "Bank accounts can only be generated for existing, active customer profiles with completed identity verification on record.",
            ),
            (
                "📜 Transaction History & Balance Tracking",
                "Securely track real-time balances, monitor transaction ledgers, and execute authorized account status updates.",
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

            # Full-width text wrapper setting
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