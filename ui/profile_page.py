import logging
import customtkinter as ctk
import tkinter.messagebox as tkmb
from core import theme, fonts

logger = logging.getLogger(__name__)

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, auth_service, current_user, on_navigate_dashboard, on_open_password_reset, on_logout):
        super().__init__(parent, fg_color=theme.BACKGROUND)
        self.pack(fill="both", expand=True)

        self.auth_service = auth_service
        self.current_user = current_user or {}
        self.on_navigate_dashboard = on_navigate_dashboard
        self.on_open_password_reset = on_open_password_reset
        self.on_logout = on_logout

        self.setup_ui()

    def setup_ui(self):
        # 1. NAVBAR
        navbar = ctk.CTkFrame(self, height=60, fg_color=theme.PRIMARY, corner_radius=0)
        navbar.pack(fill="x", side="top")
        navbar.pack_propagate(False)

        ctk.CTkButton(
            navbar, text="Back to Dashboard", width=150, height=36,
            fg_color="transparent", text_color="white", hover_color="#183153",
            font=("Montserrat", 12, "bold"), command=self.on_navigate_dashboard
        ).pack(side="left", padx=20, pady=12)

        ctk.CTkLabel(navbar, text="User Profile", font=fonts.NAVBAR, text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # 2. FOOTER
        footer = ctk.CTkFrame(self, height=35, fg_color="white", corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(
            footer, text="Version 1.0     © 2026 Divera Bank",
            font=("Montserrat", 10), text_color=theme.TEXT_SECONDARY
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 3. CONTENT AREA
        content_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(content_area, fg_color="white", corner_radius=16, border_width=1, border_color="#E5E7EB", width=500)
        card.pack(anchor="center", pady=20, padx=20)

        ctk.CTkLabel(card, text="👤", font=("Montserrat", 48)).pack(pady=(25, 5))
        self.user_heading = ctk.CTkLabel(card, text=self.current_user.get("full_name", "Admin User"), font=("Montserrat", 18, "bold"), text_color=theme.PRIMARY)
        self.user_heading.pack(pady=(0, 2))

        ctk.CTkLabel(card, text=f"Role: {self.current_user.get('role', 'Bank Operator')}", font=fonts.BODY_TEXT, text_color=theme.TEXT_SECONDARY).pack(pady=(0, 20))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=40)

        # Username / ID (Read-Only)
        self._add_label(form, "Username / Employee ID (Read-Only)")
        self.username_entry = ctk.CTkEntry(form, width=400, height=38, corner_radius=8)
        self.username_entry.pack(pady=(0, 10))
        self.username_entry.insert(0, self.current_user.get("username", "admin"))
        self.username_entry.configure(state="disabled")

        # Full Name (Editable)
        self._add_label(form, "Full Name")
        self.fullname_entry = ctk.CTkEntry(form, width=400, height=38, corner_radius=8)
        self.fullname_entry.pack(pady=(0, 10))
        self.fullname_entry.insert(0, self.current_user.get("full_name", ""))

        # Email Address (Read-Only per Bank Administration Policy)
        self._add_label(form, "Email Address (Read-Only - Contact Higher Admin)")
        self.email_entry = ctk.CTkEntry(form, width=400, height=38, corner_radius=8)
        self.email_entry.pack(pady=(0, 10))
        self.email_entry.insert(0, self.current_user.get("email", "admin@diverabank.com"))
        self.email_entry.configure(state="disabled")

        # Department (Read-Only)
        self._add_label(form, "Department (Read-Only)")
        self.dept_entry = ctk.CTkEntry(form, width=400, height=38, corner_radius=8)
        self.dept_entry.pack(pady=(0, 20))
        self.dept_entry.insert(0, self.current_user.get("department", "Accounts & Transactions"))
        self.dept_entry.configure(state="disabled")

        # Save Button
        ctk.CTkButton(
            card, text="Save Name Changes", width=400, height=40, corner_radius=10,
            font=("Montserrat", 12, "bold"), fg_color=theme.PRIMARY, hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.handle_save
        ).pack(pady=6)

        # Password Reset Button
        ctk.CTkButton(
            card, text="🔑 Reset / Change Password", width=400, height=40, corner_radius=10,
            font=("Montserrat", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB",
            command=self.on_open_password_reset
        ).pack(pady=6)

        ctk.CTkFrame(card, height=1, fg_color="#E5E7EB", width=400).pack(pady=12)

        # Logout Session Button
        ctk.CTkButton(
            card, text="Logout Session", width=400, height=40, corner_radius=10,
            font=("Montserrat", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626",
            command=self.handle_logout
        ).pack(pady=(0, 25))

    def _add_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Montserrat", 11, "bold"), text_color=theme.TEXT_SECONDARY, anchor="w").pack(fill="x", pady=(2, 2))

    def handle_save(self):
        new_name = self.fullname_entry.get().strip()
        if not new_name:
            tkmb.showwarning("Validation Error", "Full Name cannot be empty.")
            return

        username = self.current_user.get("username", "admin")
        
        try:
            success = self.auth_service.update_admin_profile(username, new_name)
            if success:
                self.current_user["full_name"] = new_name
                self.user_heading.configure(text=new_name)
                tkmb.showinfo("Success", "Profile name updated successfully in database.")
            else:
                tkmb.showwarning("Warning", "No changes were saved.")
        except Exception as e:
            tkmb.showerror("Database Error", f"Failed to update profile: {e}")

    def handle_logout(self):
        if tkmb.askyesno("Logout", "Are you sure you want to log out?"):
            self.on_logout()