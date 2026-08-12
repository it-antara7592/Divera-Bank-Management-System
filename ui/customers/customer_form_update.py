import logging
from pathlib import Path
from PIL import Image
import customtkinter as ctk

from core import theme, fonts
from services.customer_service import CustomerService
from ui.components.dialogs import ManagerAuthorizationDialog

logger = logging.getLogger(__name__)


class CustomerUpdateFormPage(ctk.CTkFrame):

    def __init__(self, parent, customer_data, on_back, on_success):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.customer_data = customer_data
        self.on_back = on_back
        self.on_success = on_success

        self._create_layout()
        self._populate_existing_data()
        self.pack(fill="both", expand=True)

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

        self._build_form()

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
            text="Back to Customer List",
            width=160,
            height=36,
            corner_radius=8,
            fg_color=theme.BUTTON_PRIMARY_HOVER,
            hover_color="#0F172A",
            text_color="white",
            font=fonts.BUTTON,
            command=self.on_back,
        )
        back_btn.pack(side="right")

    def _build_form(self):
        page_title = ctk.CTkLabel(
            self.content,
            text=f"Update Customer Profile — {self.customer_data.get('customer_id', self.customer_data.get('id', ''))}",
            font=("Montserrat", 24, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        )
        page_title.pack(fill="x", pady=(10, 2))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Modify personal details, address, or contact information for this customer record.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle.pack(fill="x", pady=(0, 20))

        form_card = ctk.CTkFrame(
            self.content,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        form_card.pack(fill="x", pady=(0, 20))

        card_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        card_inner.pack(fill="x", padx=30, pady=25)

        # Row 1: Name Fields
        r1 = ctk.CTkFrame(card_inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 15))
        r1.columnconfigure((0, 1, 2), weight=1, uniform="r1")

        self.entry_fn = self._create_field(r1, "First Name*", 0)
        self.entry_mn = self._create_field(r1, "Middle Name", 1)
        self.entry_ln = self._create_field(r1, "Last Name*", 2)

        # Row 2: Phone & Email
        r2 = ctk.CTkFrame(card_inner, fg_color="transparent")
        r2.pack(fill="x", pady=(0, 15))
        r2.columnconfigure((0, 1), weight=1, uniform="r2")

        self.entry_phone = self._create_field(r2, "Phone Number*", 0)
        self.entry_email = self._create_field(r2, "Email Address*", 1)

        # Row 3: Government ID Details
        r3 = ctk.CTkFrame(card_inner, fg_color="transparent")
        r3.pack(fill="x", pady=(0, 15))
        r3.columnconfigure((0, 1), weight=1, uniform="r3")

        f3_1 = ctk.CTkFrame(r3, fg_color="transparent")
        f3_1.grid(row=0, column=0, sticky="ew", padx=6)
        ctk.CTkLabel(f3_1, text="Govt ID Type*", font=fonts.BODY_TEXT, text_color=theme.PRIMARY).pack(anchor="w", pady=(0, 4))
        self.entry_id_type = ctk.CTkOptionMenu(
            f3_1,
            values=["PAN Card", "Passport", "Voter ID", "Driving License"],
            height=38,
            fg_color=theme.PRIMARY,
        )
        self.entry_id_type.pack(fill="x")

        self.entry_id_num = self._create_field(r3, "Govt ID Number*", 1)

        # Row 4: Address
        r4 = ctk.CTkFrame(card_inner, fg_color="transparent")
        r4.pack(fill="x", pady=(0, 15))
        r4.columnconfigure(0, weight=1)
        self.entry_address = self._create_field(r4, "Residential Address*", 0)

        # Row 5: City, State, Pin Code
        r5 = ctk.CTkFrame(card_inner, fg_color="transparent")
        r5.pack(fill="x", pady=(0, 20))
        r5.columnconfigure((0, 1, 2), weight=1, uniform="r5")

        self.entry_city = self._create_field(r5, "City*", 0)
        self.entry_state = self._create_field(r5, "State*", 1)
        self.entry_pincode = self._create_field(r5, "Pin Code*", 2)

        self.err_label = ctk.CTkLabel(card_inner, text="", font=fonts.BODY_TEXT, text_color="red")
        self.err_label.pack(pady=(0, 10))

        submit_btn = ctk.CTkButton(
            card_inner,
            text="Verify & Save Changes",
            height=44,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            font=fonts.PRIMARY_BUTTON,
            command=self._open_authorization_dialog,
        )
        submit_btn.pack(fill="x")

    def _create_field(self, parent, label_text, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="ew", padx=6)

        lbl = ctk.CTkLabel(frame, text=label_text, font=fonts.BODY_TEXT, text_color=theme.PRIMARY)
        lbl.pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(frame, height=38, font=fonts.BODY_TEXT, border_color=theme.BORDER)
        entry.pack(fill="x")
        return entry

    def _populate_existing_data(self):
        c = self.customer_data
        self.entry_fn.insert(0, c.get("first_name", ""))
        self.entry_mn.insert(0, c.get("middle_name", ""))
        self.entry_ln.insert(0, c.get("last_name", ""))
        self.entry_phone.insert(0, c.get("phone", ""))
        self.entry_email.insert(0, c.get("email", ""))
        if c.get("government_id_type") or c.get("identity_type"):
            self.entry_id_type.set(c.get("government_id_type") or c.get("identity_type"))
        self.entry_id_num.insert(0, c.get("government_id_number") or c.get("identity_number", ""))
        self.entry_address.insert(0, c.get("address", ""))
        self.entry_city.insert(0, c.get("city", ""))
        self.entry_state.insert(0, c.get("state", ""))
        self.entry_pincode.insert(0, c.get("pin_code", ""))

    def _open_authorization_dialog(self):
        """Triggers the centralized ManagerAuthorizationDialog from ui.components.dialogs"""
        ManagerAuthorizationDialog(self, on_authorized=self._save_changes)

    def _save_changes(self):
        updated_payload = {
            "first_name": self.entry_fn.get().strip(),
            "middle_name": self.entry_mn.get().strip(),
            "last_name": self.entry_ln.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "email": self.entry_email.get().strip(),
            "government_id_type": self.entry_id_type.get(),
            "government_id_number": self.entry_id_num.get().strip(),
            "address": self.entry_address.get().strip(),
            "city": self.entry_city.get().strip(),
            "state": self.entry_state.get().strip(),
            "pin_code": self.entry_pincode.get().strip(),
        }

        cust_id = self.customer_data.get("customer_id") or self.customer_data.get("id")
        success, errors = CustomerService.update_customer_profile(cust_id, updated_payload)

        if success:
            if callable(self.on_success):
                self.on_success()
        else:
            msg = errors.get("general", "Error updating customer profile. Check inputs.")
            self.err_label.configure(text=msg)