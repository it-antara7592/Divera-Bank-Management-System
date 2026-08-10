from pathlib import Path
import customtkinter as ctk
from PIL import Image

from core import fonts, theme
from services.auth_service import (
    AuthService,
    AuthenticationError,
    DatabaseConnectionError,
)


class LabeledEntry(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        label_text: str,
        show: str = None,
        is_password: bool = False,
        **kwargs,
    ):
        super().__init__(parent, fg_color="transparent")

        self.label = ctk.CTkLabel(
            self, text=label_text, font=fonts.BODY_TEXT, text_color=theme.TEXT
        )
        self.label.pack(anchor="w")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", pady=(4, 2))

        self.entry = ctk.CTkEntry(
            self.input_frame,
            height=42,
            show=show or "",
            corner_radius=10,
            border_color=theme.BORDER,
            fg_color="#FFFFFF",
            text_color=theme.TEXT,
            **kwargs,
        )
        self.entry.pack(side="left", expand=True, fill="x")

        if is_password:
            self.password_visible = False
            self.eye_button = ctk.CTkButton(
                self.input_frame,
                text="👁",
                width=42,
                height=42,
                fg_color="transparent",
                hover_color="#F3F4F6",
                text_color=theme.TEXT,
                font=("Segoe UI Emoji", 16),
                command=self.toggle_password,
            )
            self.eye_button.pack(side="left", padx=(6, 0))

        self.error_label = ctk.CTkLabel(
            self, text="", font=("Montserrat", 11), text_color=theme.ERROR
        )
        self.error_label.pack(anchor="w", pady=(2, 4))

    def get(self) -> str:
        return self.entry.get().strip()

    def set_error(self, message: str):
        if not self.winfo_exists():
            return
        self.error_label.configure(text=message)
        self.entry.configure(
            border_color=theme.ERROR if message else theme.BORDER
        )

    def clear_error(self):
        self.set_error("")

    def set_state(self, state: str):
        if not self.winfo_exists():
            return
        self.entry.configure(state=state)
        if hasattr(self, "eye_button") and self.eye_button.winfo_exists():
            self.eye_button.configure(state=state)

    def toggle_password(self):
        self.password_visible = not self.password_visible
        self.entry.configure(show="" if self.password_visible else "•")
        self.eye_button.configure(text="🙈" if self.password_visible else "👁")


class LoginPage(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        auth_service: AuthService,
        on_login_success,
        on_forgot_password,
    ):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.auth_service = auth_service
        self.on_login_success = on_login_success
        self.on_forgot_password = on_forgot_password

        self.pack(fill="both", expand=True)
        self.create_layout()

    def create_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(
            self, height=60, fg_color=theme.PRIMARY, corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")

        title = ctk.CTkLabel(
            self.header_frame,
            text="Divera Banking Management System",
            font=fonts.NAVBAR,
            text_color="#FFFFFF",
        )
        title.pack(anchor="w", padx=30, pady=16)

        self.content_frame = ctk.CTkFrame(
            self, fg_color=theme.BACKGROUND, corner_radius=0
        )
        self.content_frame.grid(
            row=1, column=0, sticky="nsew", padx=30, pady=20
        )
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(
            self.content_frame,
            width=420,
            fg_color=theme.CARD,
            corner_radius=16,
            border_width=1,
            border_color=theme.BORDER,
        )
        self.left_frame.grid(row=0, column=0, sticky="e", padx=(0, 20), pady=10)
        self.left_frame.grid_propagate(False)

        self.right_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.build_left_panel()
        self.build_right_panel()

        footer = ctk.CTkLabel(
            self,
            text="Version 1.0     © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY,
        )
        footer.place(relx=0.5, rely=0.98, anchor="s")

    def build_left_panel(self):
        content = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=30, pady=20)

        ctk.CTkLabel(
            content,
            text="Welcome Back",
            font=fonts.APP_TITLE,
            text_color=theme.PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text="Sign in to continue to Divera Banking Management System",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
            justify="left",
            wraplength=320,
        ).pack(anchor="w", pady=(6, 16))

        self.employee_field = LabeledEntry(content, label_text="Employee ID")
        self.employee_field.pack(fill="x")

        self.password_field = LabeledEntry(
            content, label_text="Password", show="•", is_password=True
        )
        self.password_field.pack(fill="x")

        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(4, 12))

        self.remember_var = ctk.BooleanVar(value=False)
        self.remember_me = ctk.CTkCheckBox(
            bottom_row,
            text="Remember Me",
            variable=self.remember_var,
            text_color=theme.TEXT,
            hover_color=theme.SECONDARY,
        )
        self.remember_me.pack(side="left")

        forgot_lbl = ctk.CTkLabel(
            bottom_row,
            text="Forgot Password?",
            text_color=theme.SECONDARY,
            cursor="hand2",
            font=fonts.BODY_TEXT,
        )
        forgot_lbl.pack(side="right")
        forgot_lbl.bind("<Button-1>", lambda e: self.on_forgot_password())

        self.auth_error = ctk.CTkLabel(
            content, text=" ", font=("Inter", 12), text_color=theme.ERROR
        )
        self.auth_error.pack(anchor="center", pady=(0, 8))

        self.login_button = ctk.CTkButton(
            content,
            text="Login",
            height=45,
            corner_radius=10,
            fg_color=theme.BUTTON_PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            text_color=theme.BUTTON_TEXT,
            font=fonts.BUTTON,
            command=self.on_login_clicked,
        )
        self.login_button.pack(fill="x")

        self.employee_field.entry.focus()
        self.employee_field.entry.bind(
            "<Return>", lambda e: self.on_login_clicked()
        )
        self.password_field.entry.bind(
            "<Return>", lambda e: self.on_login_clicked()
        )

    def build_right_panel(self):
        image_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        image_container.pack(expand=True, fill="both")

        image_path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "images"
            / "LoginPage_Image.png"
        )

        try:
            image = Image.open(image_path)
            self.login_image = ctk.CTkImage(
                light_image=image, dark_image=image, size=(500, 500)
            )
            ctk.CTkLabel(image_container, image=self.login_image, text="").pack(
                expand=True
            )
        except FileNotFoundError:
            placeholder = ctk.CTkFrame(
                image_container,
                width=500,
                height=500,
                fg_color=theme.CARD,
                border_width=1,
                border_color=theme.BORDER,
                corner_radius=16,
            )
            placeholder.pack(expand=True)
            placeholder.pack_propagate(False)

            ctk.CTkLabel(
                placeholder,
                text="Login Illustration Placeholder",
                font=fonts.SECTION_TITLE,
                text_color=theme.TEXT_SECONDARY,
            ).place(relx=0.5, rely=0.5, anchor="center")

    def validate_fields(self) -> bool:
        self.employee_field.clear_error()
        self.password_field.clear_error()
        valid = True

        if not self.employee_field.get():
            self.employee_field.set_error("Employee ID is required.")
            valid = False

        if not self.password_field.get():
            self.password_field.set_error("Password is required.")
            valid = False

        return valid

    def set_form_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.employee_field.set_state(state)
        self.password_field.set_state(state)
        self.remember_me.configure(state=state)
        self.login_button.configure(
            state=state, text="Login" if enabled else "Logging in..."
        )

    def on_login_clicked(self):
        if not self.validate_fields():
            return

        self.auth_error.configure(text=" ")
        self.set_form_state(enabled=False)
        self.after(200, self.authenticate)

    def authenticate(self):
        if not self.winfo_exists():
            return

        employee_id = self.employee_field.get()
        password = self.password_field.get()

        try:
            user_record = self.auth_service.login(employee_id, password)
            if user_record:
                self.employee_field.entry.unbind("<Return>")
                self.password_field.entry.unbind("<Return>")
                self.on_login_success(user_record)

        except AuthenticationError as err:
            if self.winfo_exists():
                self.auth_error.configure(text=str(err))

        except DatabaseConnectionError:
            if self.winfo_exists():
                self.auth_error.configure(
                    text="Database offline. Check MongoDB connection."
                )

        except Exception:
            if self.winfo_exists():
                self.auth_error.configure(
                    text="An unexpected system error occurred."
                )

        finally:
            if self.winfo_exists():
                self.set_form_state(enabled=True)