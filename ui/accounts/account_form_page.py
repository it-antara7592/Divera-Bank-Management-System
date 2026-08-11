import customtkinter as ctk
import datetime

from core import theme
from core import fonts
from services.account_service import AccountService
from services.customer_service import CustomerService
from ui.components.dialogs import AccountSuccessDialog, ConfirmDialog


class AccountFormPage(ctk.CTkFrame):
    """
    Account Opening Form Page.
    Strictly aligns with the exact theme attributes and design hierarchy of CustomerFormPage.
    """

    def __init__(self, parent, on_back=None, prefill_customer=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.prefill_customer = prefill_customer

        # Services
        self.account_service = AccountService()
        self.customer_service = CustomerService()

        # State tracking
        self.selected_customer = None
        self.active_accounts_state = {"Savings": None, "Current": None}
        self.fields = {}
        self.error_labels = {}

        # Root Layout Setup
        self.pack(fill="both", expand=True)

        # 1. Header (Banner Style)
        self._build_header()

        # 2. Scrollable Content Wrapper
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BACKGROUND,
            corner_radius=0
        )
        self.content.pack(fill="both", expand=True)

        # 3. Main Container Grid
        self.main_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=25)

        # Build Section Cards inside main_frame
        self._build_customer_lookup_card()
        self._build_account_details_card()
        self._on_account_type_changed(self.cb_account_type.get())
        self._build_action_buttons()

        # 4. Footer Section
        self._build_footer()

        # Handle prefilled data if passed from Customer Creation flow
        if self.prefill_customer:
            self._apply_prefilled_customer(self.prefill_customer)

    # =========================================================================
    # 1. HEADER
    # =========================================================================
    def _build_header(self):
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
            text="ACCOUNT FORM",
            font=fonts.APP_TITLE,
            text_color="white"
        )
        title.pack(pady=(20, 4))

        subtitle = ctk.CTkLabel(
            header,
            text="Open a new customer bank account.",
            font=fonts.BODY_TEXT,
            text_color="#D8E6F3"
        )
        subtitle.pack()

    # =========================================================================
    # CARD 1: Customer Information
    # =========================================================================
    def _build_customer_lookup_card(self):
        card = ctk.CTkFrame(
            self.main_frame,
            fg_color=theme.CARD,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.MEDIUM_RADIUS
        )
        card.pack(fill="x", pady=(0, 20), ipadx=20, ipady=20)

        # Section Title
        ctk.CTkLabel(
            card,
            text="Customer Information",
            font=fonts.CARD_TITLE,
            text_color=theme.PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 15))

        # Search Bar Row
        search_frame = ctk.CTkFrame(card, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            search_frame,
            text="Search Customer (ID / Phone / Email)",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        ).pack(anchor="w", pady=(0, 5))

        input_row = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_row.pack(fill="x")

        self.search_entry = ctk.CTkEntry(
            input_row,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY,
            placeholder_text="Enter Customer ID, Phone number, or Email..."
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda event: self._handle_customer_search())

        btn_search = ctk.CTkButton(
            input_row,
            text="Search",
            height=42,
            width=120,
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.BUTTON_PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            corner_radius=theme.SMALL_RADIUS,
            command=self._handle_customer_search
        )
        btn_search.pack(side="left")

        # Error label for search
        self.error_labels["search"] = ctk.CTkLabel(
            search_frame,
            text="",
            font=fonts.SMALL_TEXT,
            text_color=theme.ERROR
        )
        self.error_labels["search"].pack(anchor="w", pady=(4, 0))

        # Read-Only Details Grid
        info_grid = ctk.CTkFrame(card, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(10, 10))
        info_grid.columnconfigure((0, 1, 2), weight=1)

        self._build_readonly_field(info_grid, "customer_id", "Customer ID", 0, 0)
        self._build_readonly_field(info_grid, "customer_name", "Full Name", 0, 1)
        self._build_readonly_field(info_grid, "contact_info", "Contact Info", 0, 2)

        # Active Accounts Status Indicator Box
        status_box = ctk.CTkFrame(
            card,
            fg_color=theme.ENTRY_BG,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.SMALL_RADIUS
        )
        status_box.pack(fill="x", padx=20, pady=(15, 5), ipadx=10, ipady=10)

        ctk.CTkLabel(
            status_box,
            text="Existing Accounts Status",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=10, pady=(0, 5))

        self.lbl_account_status = ctk.CTkLabel(
            status_box,
            text="No customer selected.",
            font=fonts.LOGIN_ENTRY,
            text_color=theme.TEXT_SECONDARY
        )
        self.lbl_account_status.pack(anchor="w", padx=10)

    def _build_readonly_field(self, parent, key, label_text, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        ).pack(anchor="w", pady=(0, 5))

        entry = ctk.CTkEntry(
            frame,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY,
            state="disabled"
        )
        entry.pack(fill="x")
        self.fields[key] = entry

    # =========================================================================
    # CARD 2: Account Details
    # =========================================================================
    def _build_account_details_card(self):
        card = ctk.CTkFrame(
            self.main_frame,
            fg_color=theme.CARD,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.MEDIUM_RADIUS
        )
        card.pack(fill="x", pady=(0, 20), ipadx=20, ipady=20)

        ctk.CTkLabel(
            card,
            text="Account Details",
            font=fonts.CARD_TITLE,
            text_color=theme.PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 15))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20)
        grid.columnconfigure((0, 1), weight=1)

        # 1. Account Type ComboBox
        f_type = ctk.CTkFrame(grid, fg_color="transparent")
        f_type.grid(row=0, column=0, sticky="ew", padx=(0, 15), pady=10)

        ctk.CTkLabel(
            f_type,
            text="Account Type",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        ).pack(anchor="w", pady=(0, 5))

        self.cb_account_type = ctk.CTkComboBox(
            f_type,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY,
            values=["Savings", "Current"],
            command=self._on_account_type_changed
        )
        self.cb_account_type.pack(fill="x")
        self.fields["account_type"] = self.cb_account_type

        self.error_labels["account_type"] = ctk.CTkLabel(
            f_type,
            text="",
            font=fonts.SMALL_TEXT,
            text_color=theme.ERROR
        )
        self.error_labels["account_type"].pack(anchor="w", pady=(4, 0))

        # 2. Opening Date (Read-Only)
        f_date = ctk.CTkFrame(grid, fg_color="transparent")
        f_date.grid(row=0, column=1, sticky="ew", padx=(15, 0), pady=10)

        ctk.CTkLabel(
            f_date,
            text="Opening Date",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        ).pack(anchor="w", pady=(0, 5))

        today_str = datetime.date.today().strftime("%d/%m/%Y")
        entry_date = ctk.CTkEntry(
            f_date,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY
        )
        entry_date.insert(0, today_str)
        entry_date.configure(state="disabled")
        entry_date.pack(fill="x")
        self.fields["opening_date"] = entry_date

        # 3. Initial Deposit Amount
        f_dep = ctk.CTkFrame(grid, fg_color="transparent")
        f_dep.grid(row=1, column=0, sticky="ew", padx=(0, 15), pady=10)

        self.lbl_deposit_hint = ctk.CTkLabel(
            f_dep,
            text="Initial Deposit (Min ₹1,000)",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        )
        self.lbl_deposit_hint.pack(anchor="w", pady=(0, 5))

        entry_deposit = ctk.CTkEntry(
            f_dep,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY,
            placeholder_text="Enter initial deposit amount"
        )
        entry_deposit.pack(fill="x")
        self.fields["initial_deposit"] = entry_deposit

        self.error_labels["initial_deposit"] = ctk.CTkLabel(
            f_dep,
            text="",
            font=fonts.SMALL_TEXT,
            text_color=theme.ERROR
        )
        self.error_labels["initial_deposit"].pack(anchor="w", pady=(4, 0))

        # =========================================================================
        # ---> ADD ACCOUNT NUMBER FIELD HERE (Row 1, Col 1) <---
        # =========================================================================
        f_acc_num = ctk.CTkFrame(grid, fg_color="transparent")
        f_acc_num.grid(row=1, column=1, sticky="ew", padx=(15, 0), pady=10)

        ctk.CTkLabel(
            f_acc_num,
            text="Account Number",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        ).pack(anchor="w", pady=(0, 5))

        entry_acc_num = ctk.CTkEntry(
            f_acc_num,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY,
            state="disabled"
        )
        entry_acc_num.pack(fill="x")
        self.fields["account_number"] = entry_acc_num

        self.error_labels["account_number"] = ctk.CTkLabel(
            f_acc_num,
            text="",
            font=fonts.SMALL_TEXT,
            text_color=theme.ERROR
        )
        self.error_labels["account_number"].pack(anchor="w", pady=(4, 0))
        
        # 5. Overdraft Facility (Read-Only)
        f_od = ctk.CTkFrame(grid, fg_color="transparent")
        f_od.grid(row=2, column=0, sticky="ew", padx=(0, 15), pady=10)

        ctk.CTkLabel(
            f_od,
            text="Overdraft Facility",
            font=fonts.LOGIN_LABEL,
            text_color=theme.TEXT
        ).pack(anchor="w", pady=(0, 5))

        entry_od = ctk.CTkEntry(
            f_od,
            height=42,
            fg_color=theme.ENTRY_BG,
            border_color=theme.ENTRY_BORDER,
            font=fonts.LOGIN_ENTRY
        )
        entry_od.insert(0, "₹ 0.00")
        entry_od.configure(state="disabled")
        entry_od.pack(fill="x")
        self.fields["overdraft"] = entry_od
        
        # General error container for card
        self.error_labels["general"] = ctk.CTkLabel(
            card,
            text="",
            font=fonts.SMALL_TEXT,
            text_color=theme.ERROR
        )
        self.error_labels["general"].pack(anchor="w", padx=20, pady=(5, 10))

    # =========================================================================
    # ACTION BUTTONS
    # =========================================================================
    def _build_action_buttons(self):
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(25, 20))

        # Back Button
        btn_back = ctk.CTkButton(
            button_frame,
            text="Back",
            height=42,
            width=110,
            font=fonts.PRIMARY_BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color=theme.BORDER,
            corner_radius=theme.SMALL_RADIUS,
            command=self._handle_back
        )
        btn_back.pack(side="left")

        # Right Action Buttons Group (Clear + Save)
        right_group = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_group.pack(side="right")

        btn_clear = ctk.CTkButton(
            right_group,
            text="Clear",
            height=42,
            width=110,
            font=fonts.PRIMARY_BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color=theme.BORDER,
            corner_radius=theme.SMALL_RADIUS,
            command=self._clear_form
        )
        btn_clear.pack(side="left", padx=(0, 10))

        btn_save = ctk.CTkButton(
            right_group,
            text="Save",
            height=42,
            width=160,
            font=fonts.PRIMARY_BUTTON,
            fg_color=theme.BUTTON_PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            corner_radius=theme.SMALL_RADIUS,
            command=self._confirm_create_account
        )
        btn_save.pack(side="left")

    # =========================================================================
    # FOOTER
    # =========================================================================
    def _build_footer(self):
        footer = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )
        footer.pack(fill="x", side="bottom", pady=(10, 20))

        ctk.CTkLabel(
            footer,
            text="Version 1.0     © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY
        ).pack()

    # =========================================================================
    # BUSINESS LOGIC & EVENT HANDLERS
    # =========================================================================
    def _on_account_type_changed(self, choice: str):
        if choice == "Savings":
            self.lbl_deposit_hint.configure(text="Initial Deposit (Min ₹1,000)")
        else:
            self.lbl_deposit_hint.configure(text="Initial Deposit (Min ₹5,000)")
        self._clear_errors()

        # 1. Fetch preview account number using your account service
        if hasattr(self.account_service, "get_next_account_number"):
            next_acc_num = self.account_service.get_next_account_number(choice)
            self._set_field_value("account_number", next_acc_num)

        # 2. Dynamically update Overdraft Facility field based on account type
        overdraft_val = "₹ 50,000.00" if choice == "Current" else "₹ 0.00"
        self._set_field_value("overdraft", overdraft_val)

    def _handle_customer_search(self):
        query = self.search_entry.get().strip()
        self._clear_errors()

        if not query:
            self.error_labels["search"].configure(text="Please enter a Customer ID, Phone, or Email.")
            return

        customer = None
        if hasattr(self.customer_service, "search_customer"):
            customer = self.customer_service.search_customer(query)

        if not customer:
            self.error_labels["search"].configure(text="No active customer found matching query.")
            self._reset_customer_selection()
            return

        self._apply_customer_selection(customer)

    def _apply_prefilled_customer(self, customer_data: dict):
        if customer_data:
            self._apply_customer_selection(customer_data)

    def _apply_customer_selection(self, customer: dict):
        self.selected_customer = customer

        cust_id = customer.get("customer_id", "")
        full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer.get("customer_name", "")
        contact = customer.get("phone", "") or customer.get("email", "")

        # Synchronize Search Box with Customer ID automatically
        if cust_id and self.search_entry.get().strip() != cust_id:
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, cust_id)

        self._set_field_value("customer_id", cust_id)
        self._set_field_value("customer_name", full_name)
        self._set_field_value("contact_info", contact)

        if hasattr(self.account_service, "get_customer_active_accounts"):
            self.active_accounts_state = self.account_service.get_customer_active_accounts(cust_id) or {}

        sb = self.active_accounts_state.get("Savings")
        ca = self.active_accounts_state.get("Current")

        sb_txt = f"Active ({sb.get('account_number')})" if sb else "None"
        ca_txt = f"Active ({ca.get('account_number')})" if ca else "None"

        status_str = f"Savings Account: {sb_txt}   |   Current Account: {ca_txt}"
        self.lbl_account_status.configure(text=status_str, text_color=theme.PRIMARY)

    def _reset_customer_selection(self):
        self.selected_customer = None
        self._set_field_value("customer_id", "")
        self._set_field_value("customer_name", "")
        self._set_field_value("contact_info", "")
        self.lbl_account_status.configure(text="No customer selected.", text_color=theme.TEXT_SECONDARY)

    def _set_field_value(self, key: str, value: str):
        entry = self.fields.get(key)
        if entry and isinstance(entry, ctk.CTkEntry):
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, value)
            entry.configure(state="disabled")

    def _confirm_create_account(self):
        self._clear_errors()

        if not self.selected_customer:
            self.error_labels["general"].configure(text="Please search and select an active customer first.")
            return

        raw_deposit = self.fields["initial_deposit"].get()
        # Clean currency characters and formatting
        clean_deposit = raw_deposit.replace("₹", "").replace("$", "").replace(",", "").strip()
        account_type = self.cb_account_type.get()
        min_required = 1000 if account_type == "Savings" else 5000

        try:
            val = float(clean_deposit)
            if val < min_required:
                self.error_labels["initial_deposit"].configure(
                    text=f"Minimum initial deposit for {account_type} is ₹{min_required:,}."
                )
                return
        except ValueError:
            self.error_labels["initial_deposit"].configure(text="Please enter a valid numeric deposit amount.")
            return

        # Derive full name directly from state dictionary rather than UI component
        cust_name = f"{self.selected_customer.get('first_name', '')} {self.selected_customer.get('last_name', '')}".strip() or self.selected_customer.get("customer_name", "")

        payload = {
            "customer_id": self.selected_customer.get("customer_id", ""),
            "customer_name": cust_name,
            "account_type": account_type,
            "opening_date": datetime.date.today().strftime("%Y-%m-%d"),
            "initial_deposit": val
        }

        # Check existing accounts via service layer
        is_existing = False
        if hasattr(self.account_service, "repo") and hasattr(self.account_service.repo, "find_active_account_by_type"):
            is_existing = self.account_service.repo.find_active_account_by_type(
                payload["customer_id"], payload["account_type"]
            )

        if is_existing:
            msg = f"Customer already has an Active {payload['account_type']} Account."
            self.error_labels["general"].configure(text=msg)
            return

        ConfirmDialog(
            parent=self,
            title="Confirm Account Creation",
            message=f"Are you sure you want to open a new {payload['account_type']} Account for {payload['customer_name']} with an initial deposit of ₹{val:,.2f}?",
            confirm_text="Confirm",        # Overrides "Discard & Leave"
            cancel_text="Cancel",          # Overrides "Keep Editing"
            is_destructive=False,          # Changes button color from Red to Primary Blue
            on_confirm=lambda: self._execute_account_creation(payload)
        )

    def _execute_account_creation(self, payload: dict):
        success, errors, account_record = False, {}, None
        if hasattr(self.account_service, "create_account"):
            success, errors, account_record = self.account_service.create_account(payload)
        else:
            success = True
            account_record = {
                "account_number": "ACC10009872",
                "customer_name": payload["customer_name"],
                "account_type": payload["account_type"],
                "initial_deposit": payload["initial_deposit"]
            }

        if not success:
            for field_key, err_msg in errors.items():
                if field_key in self.error_labels:
                    self.error_labels[field_key].configure(text=err_msg)
            return

        # Note: Bypasses confirmation prompt when user clicks through success screen
        AccountSuccessDialog(
            parent=self,
            account_data=account_record,
            on_account_management=self._execute_back_navigation,
            on_deposit=lambda acc: self.controller.show_frame("DepositPage")  # or your deposit navigation callback
        )

    def _clear_errors(self):
        for lbl in self.error_labels.values():
            lbl.configure(text="")

    def _clear_form(self):
        self.search_entry.delete(0, "end")
        self.fields["initial_deposit"].delete(0, "end")
        self.cb_account_type.set("Savings")
        self._on_account_type_changed("Savings")
        self._reset_customer_selection()
        self._clear_errors()

    # =========================================================================
    # NAVIGATION HANDLERS
    # =========================================================================
    def _handle_back(self):
        """Shows confirmation only if form contains unsubmitted data."""
        has_unsaved_data = bool(self.selected_customer or self.fields["initial_deposit"].get().strip())

        if has_unsaved_data:
            ConfirmDialog(
                parent=self,
                title="Confirm Navigation",
                message="Are you sure you want to leave this page? Any unsaved account details will be lost.",
                on_confirm=self._execute_back_navigation
            )
        else:
            self._execute_back_navigation()

    def _execute_back_navigation(self):
        if callable(self.on_back):
            self.on_back()