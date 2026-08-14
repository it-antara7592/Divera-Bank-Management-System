import logging
import customtkinter as ctk
import tkinter.messagebox as tkmb

from core import theme, fonts
from services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class TransactionHistoryPage(ctk.CTkFrame):
    """
    Transaction History Page.

    Uses one fixed column layout for both the table header
    and transaction rows so that all columns remain aligned.
    """

    # =========================================================
    # TABLE COLUMN WIDTHS
    # =========================================================

    # These are PIXEL widths.
    #
    # Date        = 190
    # Type / ID   = 250
    # Account     = 250
    # Debit       = 150
    # Credit      = 150
    # Balance     = 150
    # Remarks     = 320
    #
    # Total = 1460 px
    #
    # If you want the table wider/narrower, change these values.
    TABLE_COLUMNS = [
        250,
        250,
        250,
        200,
        200,
        245,
        330
    ]

    TABLE_HEADERS = [
        "Date / Time",
        "Type / ID",
        "Account / Cust",
        "Debit (₹)",
        "Credit (₹)",
        "Balance (₹)",
        "Remarks"
    ]

    def __init__(
        self,
        parent,
        transaction_service=None,
        on_back=None
    ):
        super().__init__(
            parent,
            fg_color=theme.BACKGROUND
        )

        self.pack(
            fill="both",
            expand=True
        )

        self.transaction_service = (
            transaction_service
            or TransactionService()
        )

        self.on_back = on_back

        self.transactions_data = []
        self.filtered_data = []

        self.setup_ui()
        self.load_transactions()

    # =========================================================
    # UI SETUP
    # =========================================================

    def setup_ui(self):
        self._create_header()
        self._create_footer()
        self._create_content()

    # =========================================================
    # PAGE HEADER
    # =========================================================

    def _create_header(self):

        header = ctk.CTkFrame(
            self,
            height=120,
            fg_color=theme.PRIMARY,
            corner_radius=0
        )

        header.pack(
            fill="x",
            side="top"
        )

        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="TRANSACTION HISTORY",
            font=fonts.APP_TITLE,
            text_color="white"
        )

        title.pack(
            pady=(20, 4)
        )

        subtitle = ctk.CTkLabel(
            header,
            text=(
                "View and filter permanent account logs, "
                "deposits, withdrawals, and transfers."
            ),
            font=fonts.BODY_TEXT,
            text_color="#D8E6F3"
        )

        subtitle.pack()

    # =========================================================
    # FOOTER
    # =========================================================

    def _create_footer(self):

        footer = ctk.CTkFrame(
            self,
            height=35,
            fg_color="white",
            corner_radius=0
        )

        footer.pack(
            fill="x",
            side="bottom"
        )

        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer,
            text="Version 1.0     © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # =========================================================
    # CONTENT
    # =========================================================

    def _create_content(self):

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        content.columnconfigure(
            0,
            weight=1
        )

        content.rowconfigure(
            1,
            weight=1
        )

        # -----------------------------------------------------
        # FILTER CARD
        # -----------------------------------------------------

        filter_card = ctk.CTkFrame(
            content,
            fg_color=theme.CARD,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.MEDIUM_RADIUS
        )

        filter_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 15)
        )

        filter_inner = ctk.CTkFrame(
            filter_card,
            fg_color="transparent"
        )

        filter_inner.pack(
            fill="x",
            padx=20,
            pady=15
        )

        for i in range(4):
            filter_inner.columnconfigure(
                i,
                weight=1
            )

        # Search
        self.search_entry = self._create_filter_field(
            filter_inner,
            0,
            "Search (Acc No / Customer ID)",
            "Enter account or customer ID"
        )

        # Type
        self.type_dropdown = self._create_filter_dropdown(
            filter_inner,
            1,
            "Transaction Type",
            [
                "All Types",
                "Cash Deposit",
                "Cash Withdrawal",
                "Funds Transfer"
            ]
        )

        # Date
        self.date_entry = self._create_filter_field(
            filter_inner,
            2,
            "Date (YYYY-MM-DD)",
            "e.g., 2026-03-30"
        )

        # Buttons
        button_box = ctk.CTkFrame(
            filter_inner,
            fg_color="transparent"
        )

        button_box.grid(
            row=0,
            column=3,
            sticky="se",
            padx=(10, 0)
        )

        ctk.CTkButton(
            button_box,
            text="Back",
            height=38,
            font=fonts.SECONDARY_BUTTON,
            fg_color="#F3F4F6",
            hover_color="#E5E7EB",
            text_color=theme.TEXT_SECONDARY,
            command=self.on_back
        ).pack(
            side="left",
            padx=(0, 5)
        )

        ctk.CTkButton(
            button_box,
            text="Apply Filters",
            height=38,
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.apply_filters
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ctk.CTkButton(
            button_box,
            text="Reset",
            height=38,
            font=fonts.SECONDARY_BUTTON,
            fg_color="#F3F4F6",
            text_color=theme.TEXT_SECONDARY,
            hover_color="#E5E7EB",
            command=self.reset_filters
        ).pack(
            side="left"
        )

        # -----------------------------------------------------
        # TABLE CARD
        # -----------------------------------------------------

        table_card = ctk.CTkFrame(
            content,
            fg_color=theme.CARD,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.MEDIUM_RADIUS
        )

        table_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        table_card.columnconfigure(
            0,
            weight=1
        )

        table_card.rowconfigure(
            1,
            weight=1
        )

        # -----------------------------------------------------
        # TABLE TITLE
        # -----------------------------------------------------

        table_title = ctk.CTkFrame(
            table_card,
            fg_color="transparent",
            height=50
        )

        table_title.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(15, 5)
        )

        table_title.pack_propagate(False)

        ctk.CTkLabel(
            table_title,
            text="Permanent Transaction Records",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY
        ).pack(
            side="left"
        )

        self.record_count_lbl = ctk.CTkLabel(
            table_title,
            text="Showing 0 records",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY
        )

        self.record_count_lbl.pack(
            side="right"
        )

        # -----------------------------------------------------
        # TABLE CONTAINER
        # -----------------------------------------------------

        table_container = ctk.CTkFrame(
            table_card,
            fg_color="transparent"
        )

        table_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20)
        )

        table_container.columnconfigure(
            0,
            weight=1
        )

        table_container.rowconfigure(
            1,
            weight=1
        )

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        self.table_header = ctk.CTkFrame(
            table_container,
            fg_color="#E2E8F0",
            height=36,
            corner_radius=6
        )

        self.table_header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 4)
        )

        self.table_header.pack_propagate(False)

        self._configure_columns(
            self.table_header
        )

        self._create_table_header()

        # -----------------------------------------------------
        # SCROLLABLE DATA AREA
        # -----------------------------------------------------

        self.table_scroll = ctk.CTkScrollableFrame(
            table_container,
            fg_color="#F8FAFC",
            corner_radius=8
        )

        self.table_scroll.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        self.table_scroll.columnconfigure(
            0,
            weight=1
        )

    # =========================================================
    # FILTER FIELD
    # =========================================================

    def _create_filter_field(
        self,
        parent,
        column,
        label_text,
        placeholder
    ):

        box = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        box.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(0, 10)
        )

        ctk.CTkLabel(
            box,
            text=label_text,
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 2)
        )

        entry = ctk.CTkEntry(
            box,
            height=38,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            placeholder_text=placeholder,
            font=fonts.LOGIN_ENTRY
        )

        entry.pack(
            fill="x"
        )

        return entry

    # =========================================================
    # FILTER DROPDOWN
    # =========================================================

    def _create_filter_dropdown(
        self,
        parent,
        column,
        label_text,
        values
    ):

        box = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        box.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(0, 10)
        )

        ctk.CTkLabel(
            box,
            text=label_text,
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 2)
        )

        dropdown = ctk.CTkComboBox(
            box,
            values=values,
            height=38,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            button_color="#D1DFEC",
            font=fonts.LOGIN_ENTRY
        )

        dropdown.set(
            values[0]
        )

        dropdown.pack(
            fill="x"
        )

        return dropdown

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

            elif index == 6:
                anchor = "center"
                

            else:
                anchor = "w"

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

            self.transactions_data = (
                self.transaction_service
                .get_all_transactions()
            )

            self.filtered_data = list(
                self.transactions_data
            )

            self.render_table()

        except Exception as e:

            logger.exception(
                "Failed to load transaction history."
            )

            tkmb.showerror(
                "Database Error",
                f"Unable to load transaction records: {e}"
            )

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
                    "matching the criteria."
                ),
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY
            )

            empty_label.grid(
                row=0,
                column=0,
                pady=30
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

            # Funds Transfer is DEBIT from the
            # source account.
            if tx_type == "Funds Transfer":

                debit = (
                    f"₹{amount:,.2f}"
                )

                credit = "—"

            elif is_credit:

                debit = "—"

                credit = (
                    f"₹{amount:,.2f}"
                )

            else:

                debit = (
                    f"₹{amount:,.2f}"
                )

                credit = "—"

            # -------------------------------------------------
            # BALANCE
            # -------------------------------------------------

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
                    justify = "right"

                elif column_index==5:
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

    # =========================================================
    # APPLY FILTERS
    # =========================================================

    def apply_filters(self):

        query = (
            self.search_entry
            .get()
            .strip()
            .lower()
        )

        selected_type = (
            self.type_dropdown
            .get()
        )

        date_query = (
            self.date_entry
            .get()
            .strip()
        )

        filtered = []

        for tx in self.transactions_data:

            # -------------------------------------------------
            # SEARCH
            # -------------------------------------------------

            account_match = (
                query in str(
                    tx.get(
                        "account_number",
                        ""
                    )
                ).lower()
                or
                query in str(
                    tx.get(
                        "from_account",
                        ""
                    )
                ).lower()
                or
                query in str(
                    tx.get(
                        "to_account",
                        ""
                    )
                ).lower()
            )

            customer_match = (
                query in str(
                    tx.get(
                        "customer_id",
                        ""
                    )
                ).lower()
                or
                query in str(
                    tx.get(
                        "from_customer_id",
                        ""
                    )
                ).lower()
                or
                query in str(
                    tx.get(
                        "to_customer_id",
                        ""
                    )
                ).lower()
            )

            if query and not (
                account_match
                or customer_match
            ):

                continue

            # -------------------------------------------------
            # TYPE
            # -------------------------------------------------

            tx_type = tx.get(
                "transaction_type",
                ""
            )

            if (
                selected_type != "All Types"
                and selected_type != tx_type
            ):

                continue

            # -------------------------------------------------
            # DATE
            # -------------------------------------------------

            created_at = str(
                tx.get(
                    "created_at",
                    ""
                )
            )

            if (
                date_query
                and not created_at.startswith(
                    date_query
                )
            ):

                continue

            filtered.append(
                tx
            )

        self.filtered_data = filtered

        self.render_table()

    # =========================================================
    # RESET FILTERS
    # =========================================================

    def reset_filters(self):

        self.search_entry.delete(
            0,
            "end"
        )

        self.type_dropdown.set(
            "All Types"
        )

        self.date_entry.delete(
            0,
            "end"
        )

        self.filtered_data = list(
            self.transactions_data
        )

        self.render_table()