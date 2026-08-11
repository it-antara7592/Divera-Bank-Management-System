from pathlib import Path
import customtkinter as ctk
from PIL import Image
from core import fonts, theme


class LandingPage(ctk.CTkFrame):

    def __init__(self, parent, on_get_started):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.on_get_started = on_get_started
        self.pack(fill="both", expand=True)

        self.create_layout()

    # ======================================================
    # Main Layout
    # ======================================================

    def create_layout(self):
        # Window Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -------------------------------
        # Header
        # -------------------------------
        self.header_frame = ctk.CTkFrame(
            self, height=65, fg_color=theme.PRIMARY, corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.header_frame,
            text="Divera Banking Management System",
            font=("Montserrat", 20, "bold"),
            text_color="white",
        )
        title.grid(row=0, column=0, padx=30, pady=18, sticky="w")

        # -------------------------------
        # Main Content
        # -------------------------------
        self.content_frame = ctk.CTkFrame(
            self, fg_color=theme.BACKGROUND, corner_radius=0
        )
        self.content_frame.grid(
            row=1, column=0, sticky="nsew", padx=40, pady=(25, 70)
        )

        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Left Section
        self.left_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Right Section
        self.right_frame = ctk.CTkFrame(
            self.content_frame,
            width=455,
            height=650,
            fg_color=theme.CARD,
            corner_radius=20,
            border_width=1,
            border_color=theme.BORDER,
        )
        self.right_frame.grid(row=0, column=1, sticky="w", padx=(15, 0), pady=15)
        self.right_frame.grid_propagate(False)

        # Build Sections
        self.build_left_panel()
        self.build_right_panel()

        # -------------------------------
        # Footer
        # -------------------------------
        footer = ctk.CTkLabel(
            self,
            text="Version 1.0     © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY,
        )
        footer.place(relx=0.5, rely=0.985, anchor="s")

    # ======================================================
    # Left Panel
    # ======================================================

    def build_left_panel(self):
        image_container = ctk.CTkFrame(
            self.left_frame, fg_color="transparent"
        )
        image_container.pack(expand=True, fill="both")

        BASE_DIR = Path(__file__).resolve().parent.parent
        image_path = (
            BASE_DIR / "assets" / "images" / "DiveraBank_LandingImage.png"
        )

        try:
            image = Image.open(image_path)
            self.bank_image = ctk.CTkImage(
                light_image=image, dark_image=image, size=(600, 470)
            )

            image_label = ctk.CTkLabel(
                image_container, image=self.bank_image, text=""
            )
            image_label.pack(expand=True)

        except FileNotFoundError:
            placeholder = ctk.CTkFrame(
                image_container,
                width=620,
                height=500,
                fg_color=theme.CARD,
                border_width=1,
                border_color=theme.BORDER,
                corner_radius=theme.LARGE_RADIUS,
            )
            placeholder.pack(expand=True)
            placeholder.pack_propagate(False)

            text = ctk.CTkLabel(
                placeholder,
                text="Bank Image",
                font=fonts.SECTION_TITLE,
                text_color=theme.TEXT_SECONDARY,
            )
            text.place(relx=0.5, rely=0.5, anchor="center")

    # ======================================================
    # Right Panel
    # ======================================================

    def build_right_panel(self):
        content = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=32, pady=30)

        # Bank Name & Subtitle
        bank_name = ctk.CTkLabel(
            content, text="DIVERA BANK", font=fonts.APP_TITLE, text_color=theme.PRIMARY
        )
        bank_name.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            content,
            text="Banking Management System",
            font=fonts.APP_SUBTITLE,
            text_color=theme.SECONDARY,
        )
        subtitle.pack(anchor="w", pady=(4, 18))

        # Heading & Description
        heading = ctk.CTkLabel(
            content,
            text="Modern Banking\nSecure Operations\nIntelligent Insights",
            justify="left",
            font=fonts.SECTION_TITLE,
            text_color=theme.TEXT,
        )
        heading.pack(anchor="w", pady=(0, 14))

        description_text = (
            "Manage customers, accounts and banking operations "
            "through one modern desktop application built for "
            "speed, security and reliability."
        )
        description = ctk.CTkLabel(
            content,
            text=description_text,
            wraplength=320,
            justify="left",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
        )
        description.pack(anchor="w", pady=(0, 18))

        # Features List
        features = [
            "Customer Management",
            "Account Management",
            "Secure Transactions",
            "AI Insights",
        ]

        for feature in features:
            item = ctk.CTkLabel(
                content,
                text=f"✓   {feature}",
                font=fonts.BODY_TEXT,
                text_color=theme.PRIMARY,
            )
            item.pack(anchor="w", pady=(0, 6))

        # Divider
        ctk.CTkFrame(content, height=1, fg_color=theme.DIVIDER).pack(
            fill="x", pady=(10, 10)
        )

        # Get Started Button
        button = ctk.CTkButton(
            content,
            text="Get Started",
            width=300,
            height=45,
            corner_radius=10,
            fg_color=theme.BUTTON_PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            text_color=theme.BUTTON_TEXT,
            font=fonts.BUTTON,
            command=self.on_get_started,
        )
        button.pack(anchor="w", pady=(1, 0))