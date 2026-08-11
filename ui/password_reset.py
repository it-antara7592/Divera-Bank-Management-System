import logging
import customtkinter as ctk
import tkinter.messagebox as tkmb
from core import theme, fonts

logger = logging.getLogger(__name__)

class PasswordResetPage(ctk.CTkFrame):
    def __init__(self, parent, auth_service, on_return_callback, current_user=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)
        self.pack(fill="both", expand=True)

        self.auth_service = auth_service
        self.on_return_callback = on_return_callback
        self.current_user = current_user

        self.setup_ui()

    def setup_ui(self):
        self.card = ctk.CTkFrame(
            self, fg_color="#FFFFFF", corner_radius=18,
            border_width=2, border_color=theme.PRIMARY, width=440
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.card, text="🔒 Admin Password Reset",
            font=fonts.SECTION_TITLE, text_color=theme.PRIMARY
        ).pack(pady=(25, 5), padx=25)

        ctk.CTkLabel(
            self.card, text="Enter username, special reset code, and your new password.",
            font=fonts.BODY_TEXT, text_color=theme.TEXT_SECONDARY, wraplength=360
        ).pack(pady=(0, 20), padx=25)

        form = ctk.CTkFrame(self.card, fg_color="transparent")
        form.pack(fill="x", padx=30, pady=5)

        # Username
        self.username_entry = ctk.CTkEntry(
            form, placeholder_text="Employee ID", width=360, height=42, corner_radius=10,
            fg_color="#FFFFFF", border_color=theme.PRIMARY, text_color=theme.TEXT
        )
        self.username_entry.pack(pady=6)
        if self.current_user:
            self.username_entry.insert(0, self.current_user.get("username", ""))

        # Reset Code
        self.reset_code_entry = ctk.CTkEntry(
            form, placeholder_text="Special Reset Code", show="•", width=360, height=42, corner_radius=10,
            fg_color="#FFFFFF", border_color=theme.PRIMARY, text_color=theme.TEXT
        )
        self.reset_code_entry.pack(pady=6)

        # New Password & Confirm Password
        self.new_pass_entry = ctk.CTkEntry(
            form, placeholder_text="New Password (e.g., Divera@2026)", show="•", width=360, height=42, corner_radius=10,
            fg_color="#FFFFFF", border_color=theme.PRIMARY, text_color=theme.TEXT
        )
        self.new_pass_entry.pack(pady=6)

        self.confirm_pass_entry = ctk.CTkEntry(
            form, placeholder_text="Confirm New Password", show="•", width=360, height=42, corner_radius=10,
            fg_color="#FFFFFF", border_color=theme.PRIMARY, text_color=theme.TEXT
        )
        self.confirm_pass_entry.pack(pady=6)

        # Submit
        ctk.CTkButton(
            self.card, 
            text="Reset Password", 
            width=360, 
            height=45, 
            corner_radius=12,
            font=fonts.BUTTON, 
            fg_color=theme.PRIMARY, 
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            text_color="white", 
            command=self.handle_reset
        ).pack(pady=(15, 8))

        back_text = "Back to Profile" if self.current_user else "Back to Login"
        
        ctk.CTkButton(
            self.card, text=back_text, width=360, height=35, corner_radius=10,
            fg_color="transparent", text_color=theme.TEXT_SECONDARY, hover_color="#F3F4F6",
            font=fonts.BODY_TEXT, command=self.on_return_callback
        ).pack(pady=(0, 20))

    def handle_reset(self):
        username = self.username_entry.get().strip()
        reset_code = self.reset_code_entry.get().strip()
        new_pass = self.new_pass_entry.get().strip()
        confirm_pass = self.confirm_pass_entry.get().strip()

        if not username or not reset_code or not new_pass or not confirm_pass:
            tkmb.showwarning("Missing Information", "All fields are required.")
            return

        try:
            self.auth_service.reset_admin_password(username, reset_code, new_pass, confirm_pass)
            tkmb.showinfo("Success", "Password Reset Successful!\n\nPlease login using your new password.")
            self.on_return_callback()
        except Exception as err:
            tkmb.showerror("Reset Error", str(err))