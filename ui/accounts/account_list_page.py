import logging
from pathlib import Path
from PIL import Image
import customtkinter as ctk
from core import theme, fonts
from services.account_service import AccountService

logger = logging.getLogger(__name__)


class AccountListPage(ctk.CTkFrame):

    def __init__(self, parent, on_back, on_open_details=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.on_open_details = on_open_details  # Callback to navigate to Account Details Page
        self.selected_account_number = None
        self.selected_account_data = None

        self.current_filter_type = "All"
        self.current_filter_status = "All"

        self.accounts_db = self._fetch_accounts_from_db()
        self.filtered_accounts = list(self.accounts_db)
        self.row_frames = {}

        self._create_layout()
        self.pack(fill="both", expand=True)

    def _fetch_accounts_from_db(self):
        """Fetch records using AccountService / AccountRepository."""
        try:
            records = AccountService.get_all_accounts()
            formatted_list = []
            for doc in records:
                formatted_list.append({
                    "account_number": doc.get("account_number", "N/A"),
                    "customer_id": doc.get("customer_id", "N/A"),
                    "customer_name": doc.get("customer_name", "N/A"),
                    "account_type": doc.get("account_type", "Savings"),
                    "opening_date": doc.get("opening_date", "N/A"),
                    "status": doc.get("status", "Active"),
                    "raw_doc": doc
                })
            return formatted_list
        except Exception as e:
            logger.error(f"Failed to fetch account data: {e}")
            return []

    def _create_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_header()

        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.PRIMARY,
            scrollbar_button_hover_color=theme.BUTTON_PRIMARY_HOVER,
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=50, pady=20)

        self._build_body()

    def build_header(self):
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
            text="Return Dashboard",
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
        page_title = ctk.CTkLabel(
            self.content,
            text="Account Directory & Records",
            font=("Montserrat", 26, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        )
        page_title.pack(fill="x", pady=(10, 2))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Manage savings and current accounts, view operational configurations, and process account lifecycles.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle.pack(fill="x", pady=(0, 20))

        self._build_search_bar()
        self._build_toolbar()
        self._build_table()

    def _build_search_bar(self):
        search_card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        search_card.pack(fill="x", pady=(0, 15))

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill="x", padx=20, pady=15)

        search_label = ctk.CTkLabel(
            search_inner,
            text="🔍 Find Account:",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        )
        search_label.pack(side="left", padx=(0, 15))

        self.search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Search by Account Number or Customer ID...",
            height=40,
            font=fonts.BODY_TEXT,
            border_color=theme.BORDER,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self._perform_search())

        search_btn = ctk.CTkButton(
            search_inner,
            text="Search",
            width=100,
            height=40,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            command=self._perform_search,
        )
        search_btn.pack(side="right")

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        # View details button
        self.view_btn = ctk.CTkButton(
            toolbar,
            text="View Account Details",
            height=38,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            state="disabled",
            command=self._navigate_to_details,
        )
        self.view_btn.pack(side="left")

        info_lbl = ctk.CTkLabel(
            toolbar,
            text="* Select a row or double-click to inspect account details.",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY,
        )
        info_lbl.pack(side="left", padx=(15, 0))

        # Filters on the right side
        filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filter_frame.pack(side="right")

        type_lbl = ctk.CTkLabel(filter_frame, text="Type:", font=fonts.SMALL_TEXT, text_color=theme.TEXT_SECONDARY)
        type_lbl.pack(side="left", padx=(0, 5))

        self.type_filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Savings", "Current"],
            width=100,
            height=32,
            fg_color=theme.CARD,
            button_color='#CBD5E1',
            button_hover_color=theme.BUTTON_PRIMARY_HOVER,
            text_color=theme.TEXT,
            font=fonts.SMALL_TEXT,
            command=self._on_type_filter_change,
        )
        self.type_filter_menu.pack(side="left", padx=(0, 15))
        self.type_filter_menu.set("All")

        status_lbl = ctk.CTkLabel(filter_frame, text="Status:", font=fonts.SMALL_TEXT, text_color=theme.TEXT_SECONDARY)
        status_lbl.pack(side="left", padx=(0, 5))

        self.status_filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Active", "Closed"],
            width=100,
            height=32,
            fg_color=theme.CARD,
            button_color='#CBD5E1',
            button_hover_color=theme.BUTTON_PRIMARY_HOVER,
            text_color=theme.TEXT,
            font=fonts.SMALL_TEXT,
            command=self._on_status_filter_change,
        )
        self.status_filter_menu.pack(side="left")
        self.status_filter_menu.set("All")

    def _build_table(self):
        self.table_card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        self.table_card.pack(fill="x", pady=(0, 25))

        header_frame = ctk.CTkFrame(self.table_card, fg_color="#F1F5F9", height=42, corner_radius=0)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        columns = [
            ("Account No", 180),
            ("Customer ID", 160),
            ("Customer Name", 200),
            ("Type", 120),
            ("Status", 100),
        ]

        for title, width in columns:
            lbl = ctk.CTkLabel(
                header_frame,
                text=title,
                font=("Montserrat", 12, "bold"),
                text_color=theme.PRIMARY,
                width=width,
                anchor="w",
            )
            lbl.pack(side="left", padx=12, pady=8)

        self.rows_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows_container.pack(fill="x")

        self._render_table_rows()

    def _render_table_rows(self):
        for widget in self.rows_container.winfo_children():
            widget.destroy()

        self.row_frames.clear()

        if not self.filtered_accounts:
            no_data = ctk.CTkLabel(
                self.rows_container,
                text="No account records found matching the criteria.",
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY,
                pady=30,
            )
            no_data.pack(fill="x")
            return

        for idx, account in enumerate(self.filtered_accounts):
            acc_no = account["account_number"]
            bg_color = theme.CARD if idx % 2 == 0 else "#F8FAFC"

            row = ctk.CTkFrame(
                self.rows_container,
                fg_color=bg_color,
                height=48,
                corner_radius=0,
                border_width=1,
                border_color="#F1F5F9",
            )
            row.pack(fill="x")
            row.pack_propagate(False)

            row.bind("<Button-1>", lambda e, acc=account: self._select_account(acc))
            row.bind("<Double-Button-1>", lambda e, acc=account: self._handle_double_click(acc))

            cells = [
                (account["account_number"], 180, "bold"),
                (account["customer_id"], 160, "normal"),
                (account["customer_name"], 200, "normal"),
                (account["account_type"], 120, "normal"),
                (account["status"], 100, "bold"),
            ]

            for text, width, weight in cells:
                cell_lbl = ctk.CTkLabel(
                    row,
                    text=text,
                    font=("Montserrat", 12, weight),
                    text_color=theme.PRIMARY if weight == "bold" else theme.TEXT,
                    width=width,
                    anchor="w",
                )
                cell_lbl.pack(side="left", padx=12, pady=10)
                cell_lbl.bind("<Button-1>", lambda e, acc=account: self._select_account(acc))
                cell_lbl.bind("<Double-Button-1>", lambda e, acc=account: self._handle_double_click(acc))

            self.row_frames[acc_no] = row

    def _select_account(self, account):
        self.selected_account_number = account["account_number"]
        self.selected_account_data = account
        self.view_btn.configure(state="normal")

        for acc_no, row in self.row_frames.items():
            if acc_no == account["account_number"]:
                row.configure(fg_color="#E0F2FE")
            else:
                row.configure(fg_color=theme.CARD)

    def _handle_double_click(self, account):
        self._select_account(account)
        self._navigate_to_details()

    def _on_type_filter_change(self, choice):
        self.current_filter_type = choice
        self._perform_search()

    def _on_status_filter_change(self, choice):
        self.current_filter_status = choice
        self._perform_search()

    def _perform_search(self):
        query = self.search_entry.get().strip().lower()

        filtered = []
        for acc in self.accounts_db:
            matches_query = (
                not query
                or query in acc["account_number"].lower()
                or query in acc["customer_id"].lower()
            )

            matches_type = (
                self.current_filter_type == "All"
                or acc["account_type"].lower() == self.current_filter_type.lower()
            )

            matches_status = (
                self.current_filter_status == "All"
                or acc["status"].lower() == self.current_filter_status.lower()
            )

            if matches_query and matches_type and matches_status:
                filtered.append(acc)

        self.filtered_accounts = filtered
        self.selected_account_number = None
        self.selected_account_data = None
        self.view_btn.configure(state="disabled")
        self._render_table_rows()

    def _navigate_to_details(self):
        """Navigates to the read-only Account Details Page."""
        if self.on_open_details and self.selected_account_data:
            self.on_open_details(self.selected_account_data)