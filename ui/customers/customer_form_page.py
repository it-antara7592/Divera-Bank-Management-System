import customtkinter as ctk
from core import theme
from core import fonts
from services.customer_service import CustomerService
from ui.components.dialogs import SuccessDialog, ConfirmDialog
from data.india_location import INDIA_LOCATIONS


class CustomerFormPage(ctk.CTkFrame):

    def __init__(self, parent, on_back=None, on_create_account=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.on_create_account = on_create_account
        self.fields = {}
        self.error_labels = {}
        self.row_counter = {}

        self.create_layout()
        self.pack(fill="both", expand=True)


    # ==================================================
    # Layout
    # ==================================================

    def create_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_header()
        self.build_content()
        self.build_footer()
        self.build_buttons()

    # ==================================================
    # Header
    # ==================================================

    def build_header(self):
        header = ctk.CTkFrame(
            self,
            height=120,
            fg_color=theme.PRIMARY,
            corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="CUSTOMER FORM",
            font=fonts.APP_TITLE,
            text_color="white"
        )
        title.pack(pady=(20, 4))

        subtitle = ctk.CTkLabel(
            header,
            text="Register a new customer profile.",
            font=fonts.BODY_TEXT,
            text_color="#D8E6F3"
        )
        subtitle.pack()

    # ==================================================
    # Scrollable Content
    # ==================================================

    def build_content(self):
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BACKGROUND,
            corner_radius=0,
            scrollbar_button_color=theme.PRIMARY,
            scrollbar_button_hover_color=theme.BUTTON_PRIMARY_HOVER
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)

        self.build_personal_information()
        self.build_identity_information()
        self.build_contact_information()
        self.build_address_information()

    # ==================================================
    # Section Card Helper
    # ==================================================

    def create_section_card(self, title_text):
        card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=16,
            border_width=1,
            border_color=theme.BORDER
        )
        card.pack(fill="x", pady=(0, 25))
        card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            card,
            text=title_text,
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=25, pady=(20, 10))

        divider = ctk.CTkFrame(card, height=1, fg_color=theme.BORDER)
        divider.grid(row=1, column=0, columnspan=2, sticky="ew", padx=25, pady=(0, 15))

        self.row_counter[card] = 2
        return card

    # ==================================================
    # Generic Field Builders
    # ==================================================

    def add_entry(self, parent, label_text, placeholder, key, disabled=False):
        row = self.row_counter[parent]

        lbl = ctk.CTkLabel(
            parent,
            text=label_text,
            width=160,
            anchor="w",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT
        )
        lbl.grid(row=row, column=0, sticky="w", padx=(25, 20), pady=(5, 0))

        entry = ctk.CTkEntry(
            parent,
            width=430,
            height=38,
            placeholder_text=placeholder
        )
        entry.grid(row=row, column=1, sticky="w", padx=(0, 25), pady=(5, 0))

        error = ctk.CTkLabel(
            parent,
            text="",
            font=("Montserrat", 11),
            text_color="#EF4444"
        )
        error.grid(row=row + 1, column=1, sticky="w", padx=(0, 25), pady=(2, 6))

        if disabled:
            entry.insert(0, placeholder)
            entry.configure(state="disabled", fg_color="#F3F4F6", text_color="#6B7280")

        self.fields[key] = entry
        self.error_labels[key] = error
        self.row_counter[parent] += 2

        # In-line input formatters
        if key in ["first_name", "middle_name", "last_name"]:
            entry.bind("<KeyRelease>", lambda e, k=key: self.format_name(k))
        elif key == "phone":
            entry.bind("<KeyRelease>", lambda e: self.format_phone())
        elif key == "pin_code":
            entry.bind("<KeyRelease>", lambda e: self.format_pincode())
        elif key == "dob":
            entry.bind("<KeyRelease>", lambda e: self.format_dob())

    def add_combobox(self, parent, label_text, values, key, command=None):
        row = self.row_counter[parent]

        lbl = ctk.CTkLabel(
            parent,
            text=label_text,
            width=160,
            anchor="w",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT
        )
        lbl.grid(row=row, column=0, sticky="w", padx=(25, 20), pady=(5, 0))

        combo = ctk.CTkComboBox(
            parent,
            values=values,
            width=430,
            height=38,
            state="readonly",
            command=command
        )

        defaults = {
            "gender": "Select Gender",
            "government_id_type": "Select Government ID",
            "state": "Select State",
            "city": "Select City"
        }
        combo.set(defaults.get(key, "Select"))

        combo.grid(row=row, column=1, sticky="w", padx=(0, 25), pady=(5, 0))

        error = ctk.CTkLabel(
            parent,
            text="",
            font=("Montserrat", 11),
            text_color="#EF4444"
        )
        error.grid(row=row + 1, column=1, sticky="w", padx=(0, 25), pady=(2, 6))

        self.fields[key] = combo
        self.error_labels[key] = error
        self.row_counter[parent] += 2

    # ==================================================
    # Section Constructors
    # ==================================================

    def build_personal_information(self):
        card = self.create_section_card("PERSONAL INFORMATION")

        # 1. Add Customer ID Field
        self.add_entry(card, "Customer ID", "Auto-generating...", "customer_id")

        # 2. Fetch Auto ID and lock the field
        auto_id = CustomerService.get_next_customer_id()
        cust_id_entry = self.fields["customer_id"]
        
        cust_id_entry.configure(state="normal")
        cust_id_entry.delete(0, "end")
        cust_id_entry.insert(0, auto_id)
        cust_id_entry.configure(
            state="disabled",
            fg_color="#F3F4F6",      # Muted grey background
            text_color="#374151"     # Dark grey text for readability
        )
        self.add_entry(card, "First Name", "Enter first name", "first_name")
        self.add_entry(card, "Middle Name", "Enter middle name (optional)", "middle_name")
        self.add_entry(card, "Last Name", "Enter last name", "last_name")
        self.add_entry(card, "Date of Birth", "DD / MM / YYYY", "dob")
        self.add_combobox(card, "Gender", ["Male", "Female", "Other", "Prefer not to say"], "gender")
        self.add_entry(card, "Nationality", "Indian", "nationality", disabled=True)

    def build_identity_information(self):
        card = self.create_section_card("IDENTITY INFORMATION")
        id_options = ["Aadhaar Card", "PAN Card", "Passport", "Driving Licence", "Voter ID"]
        self.add_combobox(card, "Government ID Type", id_options, "government_id_type", command=self.on_government_id_change)
        self.add_entry(card, "Government ID Number", "Select ID Type First", "government_id_number")

        # Bind live restriction/formatting on ID entry key release
        id_entry = self.fields["government_id_number"]
        id_entry.bind("<KeyRelease>", lambda e: self.format_government_id_number())

    def on_government_id_change(self, value):
        entry = self.fields["government_id_number"]
        entry.configure(state="normal")
        entry.delete(0, "end")

        placeholders = {
            "Aadhaar Card": "12-digit number",
            "PAN Card": "10-character alphanumeric (e.g. ABCDE1234F)",
            "Passport": "8-character alphanumeric",
            "Driving Licence": "Up to 16 alphanumeric characters",
            "Voter ID": "10-character alphanumeric (e.g. ABC1234567)"
        }
        entry.configure(placeholder_text=placeholders.get(value, "Enter ID Number"))

    def format_government_id_number(self):
        """Enforces live input filtering and character limits based on selected ID type."""
        id_type = self.fields["government_id_type"].get()
        entry = self.fields["government_id_number"]
        raw_val = entry.get()

        if id_type == "Aadhaar Card":
            # Numbers only, max 12 digits
            filtered = "".join(ch for ch in raw_val if ch.isdigit())[:12]
        elif id_type == "PAN Card":
            # Alphanumeric only, uppercase, max 10 chars
            filtered = "".join(ch for ch in raw_val if ch.isalnum()).upper()[:10]
        elif id_type == "Passport":
            # Alphanumeric only, uppercase, max 8 chars
            filtered = "".join(ch for ch in raw_val if ch.isalnum()).upper()[:8]
        elif id_type == "Voter ID":
            # Alphanumeric only, uppercase, max 10 chars
            filtered = "".join(ch for ch in raw_val if ch.isalnum()).upper()[:10]
        elif id_type == "Driving Licence":
            # Alphanumeric only, uppercase, max 16 chars
            filtered = "".join(ch for ch in raw_val if ch.isalnum()).upper()[:16]
        else:
            filtered = raw_val

        if raw_val != filtered:
            entry.delete(0, "end")
            entry.insert(0, filtered)

    def build_contact_information(self):
        card = self.create_section_card("CONTACT INFORMATION")
        self.add_entry(card, "Phone Number", "10-digit mobile number", "phone")
        self.add_entry(card, "Email Address", "example@domain.com", "email")

    def build_address_information(self):
        card = self.create_section_card("ADDRESS INFORMATION")
        self.add_entry(card, "Address Line", "Flat/House No, Street, Landmark", "address")
        self.add_combobox(card, "State", list(INDIA_LOCATIONS.keys()), "state", command=self.on_state_change)
        self.add_combobox(card, "City", [], "city")
        self.add_entry(card, "PIN Code", "6-digit PIN code", "pin_code")

    # ==================================================
    # Event Handlers & Input Formatters
    # ==================================================

    def on_government_id_change(self, value):
        entry = self.fields["government_id_number"]
        entry.configure(state="normal")
        entry.delete(0, "end")

        placeholders = {
            "Aadhaar Card": "Enter 12-digit Aadhaar Number",
            "PAN Card": "e.g. ABCDE1234F",
            "Passport": "Enter Passport Number",
            "Driving Licence": "Enter Driving Licence Number",
            "Voter ID": "Enter Voter ID Number"
        }
        entry.configure(placeholder_text=placeholders.get(value, "Enter ID Number"))

    def on_state_change(self, state):
        city_combo = self.fields["city"]
        cities = INDIA_LOCATIONS.get(state, [])
        city_combo.configure(values=cities)
        city_combo.set("Select City")

    def format_name(self, key):
        entry = self.fields[key]
        val = "".join(ch for ch in entry.get() if ch.isalpha() or ch.isspace())
        if entry.get() != val:
            entry.delete(0, "end")
            entry.insert(0, val.title())

    def format_phone(self):
        entry = self.fields["phone"]
        digits = "".join(ch for ch in entry.get() if ch.isdigit())[:10]
        if entry.get() != digits:
            entry.delete(0, "end")
            entry.insert(0, digits)

    def format_pincode(self):
        entry = self.fields["pin_code"]
        digits = "".join(ch for ch in entry.get() if ch.isdigit())[:6]
        if entry.get() != digits:
            entry.delete(0, "end")
            entry.insert(0, digits)

    def format_dob(self):
        entry = self.fields["dob"]
        digits = "".join(ch for ch in entry.get() if ch.isdigit())[:8]
        formatted = digits
        if len(digits) > 4:
            formatted = f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
        elif len(digits) > 2:
            formatted = f"{digits[:2]}/{digits[2:]}"
        
        if entry.get() != formatted:
            entry.delete(0, "end")
            entry.insert(0, formatted)

    # ==================================================
    # Buttons Layout
    # ==================================================

    def build_buttons(self):
        """Creates and attaches action buttons at the bottom of the form."""
        button_container = ctk.CTkFrame(self.content, fg_color="transparent")
        button_container.pack(fill="x", pady=(10, 30))

        # Back Button (Left Aligned)
        back_btn = ctk.CTkButton(
            button_container,
            text="← Back",
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            height=42,
            width=110,
            command=self.back
        )
        back_btn.pack(side="left")

        # Save Button (Right Aligned - Primary Action)
        save_btn = ctk.CTkButton(
            button_container,
            text="Save Customer",
            font=fonts.BUTTON,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            height=42,
            width=160,
            command=self.save_customer
        )
        save_btn.pack(side="right", padx=(12, 0))

        # Clear Form Button (Right Aligned Next to Save)
        clear_btn = ctk.CTkButton(
            button_container,
            text="Clear Form",
            font=fonts.BUTTON,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            hover_color="#E5E7EB",
            height=42,
            width=120,
            command=self.clear_form
        )
        clear_btn.pack(side="right")

    def is_form_dirty(self) -> bool:
        """Checks if the user typed or selected anything in the form."""
        if not hasattr(self, "fields"):
            return False

        for key, widget in self.fields.items():
            # Skip read-only metadata fields
            if key in ["customer_id", "nationality"]:
                continue

            if isinstance(widget, ctk.CTkEntry):
                if widget.get().strip():
                    return True
            elif isinstance(widget, ctk.CTkComboBox):
                val = widget.get().strip()
                if val and not val.startswith("Select"):
                    return True
        return False

    def back(self):
        """Triggers the confirmation dialog if changes were made, else leaves immediately."""
        if self.is_form_dirty():
            ConfirmDialog(
                parent=self.winfo_toplevel(),  # Uses main window so popup displays on top
                title="Discard Changes?",
                message="You have unsaved changes on this form. Are you sure you want to leave?",
                on_confirm=self._force_leave
            )
        else:
            self._force_leave()

    def _force_leave(self):
        """Clears form state and executes the navigation back callback."""
        self.clear_form()
        if callable(self.on_back):
            self.on_back()   

    # ==================================================
    # Actions
    # ==================================================

    def save_customer(self):
        # 1. Clear previous errors
        for label in self.error_labels.values():
            label.configure(text="")

        # 2. Gather form data
        data = {key: widget.get().strip() for key, widget in self.fields.items()}

        # 3. Call service layer validation & save
        success, errors = CustomerService.save_customer(data)

        if not success:
            for key, message in errors.items():
                if key in self.error_labels:
                    self.error_labels[key].configure(text=message)
        else:
            # 4. Show Workflow Dialog passing newly created customer object
            SuccessDialog(
                parent=self.winfo_toplevel(),
                customer_data=data,
                on_create_account=self._navigate_to_account_form,
                on_customer_management=self._force_leave
            )

    def _navigate_to_account_form(self, customer_data):
        if callable(self.on_create_account):
            self.on_create_account(customer_data)

    def _on_save_success_complete(self):
        self.clear_form()
        if callable(self.on_back):
            self.on_back()

    def clear_form(self):
        """Resets input fields while preserving read-only structural data."""
        # 1. Clear error labels
        for label in self.error_labels.values():
            label.configure(text="")

        # 2. Reset fields
        for key, widget in self.fields.items():
            # Do NOT clear auto-generated Customer ID or Nationality
            if key in ["customer_id", "nationality"]:
                continue

            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state="normal")
                widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkComboBox):
                defaults = {
                    "gender": "Select Gender",
                    "government_id_type": "Select Government ID",
                    "state": "Select State",
                    "city": "Select City"
                }
                widget.set(defaults.get(key, "Select"))


    # ==================================================
    # Footer
    # ==================================================

    def build_footer(self):
        footer = ctk.CTkLabel(
            self,
            text="Version 1.0     © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY
        )
        footer.grid(row=2, column=0, pady=(0, 12))