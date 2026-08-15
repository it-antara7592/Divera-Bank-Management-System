import logging
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from core import theme, fonts
from services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class CustomerListPage(ctk.CTkFrame):

    def __init__(self, parent, on_back, on_open_update=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_back = on_back
        self.on_open_update = on_open_update  # Callback to navigate to update page
        self.selected_customer_id = None
        self.selected_customer_data = None

        self.customers_db = self._fetch_customers_from_db()
        self.filtered_customers = list(self.customers_db)
        self.row_frames = {}

        self._create_layout()
        self.pack(fill="both", expand=True)

    def _fetch_customers_from_db(self):
        """Fetch records using CustomerService / CustomerRepository."""
        try:
            records = CustomerService.get_all_customers()
            formatted_list = []
            for doc in records:
                # Map repository document fields to UI schema
                first_name = doc.get("first_name", "")
                middle_name = doc.get("middle_name", "")
                last_name = doc.get("last_name", "")
                
                full_name = " ".join(filter(None, [first_name, middle_name, last_name])) or doc.get("name", "N/A")

                formatted_list.append({
                    "id": doc.get("customer_id", "N/A"),
                    "name": full_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "phone": doc.get("phone", "N/A"),
                    "email": doc.get("email", "N/A"),
                    "identity_type": doc.get("government_id_type", doc.get("identity_type", "Government ID")),
                    "identity_number": doc.get("government_id_number", ""),
                    "address": doc.get("address", ""),
                    "city": doc.get("city", ""),
                    "state": doc.get("state", ""),
                    "pin_code": doc.get("pin_code", ""),
                    "status": doc.get("status", "Active"),
                    "raw_doc": doc
                })
            return formatted_list
        except Exception as e:
            logger.error(f"Failed to fetch customer data: {e}")
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
            text="Return to Management",
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
            text="Customer Directory & Records",
            font=("Montserrat", 26, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        )
        page_title.pack(fill="x", pady=(10, 2))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Search, inspect, and update customer identification profiles across the central banking database.",
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
            text="🔍 Find Record:",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        )
        search_label.pack(side="left", padx=(0, 15))

        self.search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Search by Customer ID, Phone, or Email...",
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

        self.update_btn = ctk.CTkButton(
            toolbar,
            text="Update Customer Data",
            height=38,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            state="disabled",
            command=self._navigate_to_update_page,
        )
        self.update_btn.pack(side="left")

        info_lbl = ctk.CTkLabel(
            toolbar,
            text="* Select a row to enable profile editing.",
            font=fonts.SMALL_TEXT,
            text_color=theme.TEXT_SECONDARY,
        )
        info_lbl.pack(side="right", pady=5)

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
            ("Customer ID", 160),
            ("Full Name", 180),
            ("Phone Number", 140),
            ("Email Address", 220),
            ("Gov ID Type", 120),
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

        if not self.filtered_customers:
            no_data = ctk.CTkLabel(
                self.rows_container,
                text="No customer records found in database.",
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY,
                pady=30,
            )
            no_data.pack(fill="x")
            return

        for idx, customer in enumerate(self.filtered_customers):
            c_id = customer["id"]
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

            row.bind("<Button-1>", lambda e, cust=customer: self._select_customer(cust))

            cells = [
                (customer["id"], 160, "bold"),
                (customer["name"], 180, "normal"),
                (customer["phone"], 140, "normal"),
                (customer["email"], 220, "normal"),
                (customer["identity_type"], 120, "normal"),
                (customer["status"], 100, "bold"),
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
                cell_lbl.bind("<Button-1>", lambda e, cust=customer: self._select_customer(cust))

            self.row_frames[c_id] = row

    def _select_customer(self, customer):
        self.selected_customer_id = customer["id"]
        self.selected_customer_data = customer
        self.update_btn.configure(state="normal")

        for cid, row in self.row_frames.items():
            if cid == customer["id"]:
                row.configure(fg_color="#E0F2FE")
            else:
                row.configure(fg_color=theme.CARD)

    def _perform_search(self):
        query = self.search_entry.get().strip().lower()

        if not query:
            self.filtered_customers = list(self.customers_db)
        else:
            self.filtered_customers = [
                c for c in self.customers_db
                if query in c["id"].lower()
                or query in c["phone"].lower()
                or query in c["email"].lower()
                or query in c["name"].lower()
            ]

        self.selected_customer_id = None
        self.selected_customer_data = None
        self.update_btn.configure(state="disabled")
        self._render_table_rows()

    def _navigate_to_update_page(self):
        """Navigates to the full update form page."""
        if self.on_open_update and self.selected_customer_data:
            self.on_open_update(self.selected_customer_data)