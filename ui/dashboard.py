import datetime
import json
import logging
import threading
import os
import customtkinter as ctk
from pathlib import Path
from PIL import Image
from core import fonts, theme
from repositories.stats_repository import StatsRepository
from services.ai_service import AIService

# Setup module-level logger
logger = logging.getLogger(__name__)


class DashboardPage(ctk.CTkFrame):

    def __init__(self, parent, current_user=None, on_logout=None, open_customer_management=None,open_account_management=None, open_transaction_management=None,open_profile=None):
        super().__init__(parent, fg_color=theme.BACKGROUND)

        self.pack(fill="both", expand=True)
        self.current_user = current_user
        self.on_logout_callback = on_logout
        self.open_customer_management_callback = open_customer_management
        self.open_account_management_callback=open_account_management
        self.open_transaction_management_callback=open_transaction_management
        self.open_profile_callback = open_profile


        # Dynamic Stats Data — Defaulted to 0/Placeholder state
        self.stats_data = {
            "Customers": "0",
            "Active Accounts": "0",
            "Closed Accounts": "0",
            "Transactions": "0",
            "Bank Balance": "₹0",
            "Failed Transactions": "0",
        }

        # References to value labels for safe real-time updates
        self.stat_labels = {}

        try:
            self.create_layout()
            logger.info("Dashboard layout successfully built.")
        except Exception as e:
            logger.error(f"Error initializing Dashboard layout: {e}")

        self.refresh_stats()

    def refresh_stats(self):
        #Fetches live aggregated metrics from MongoDB and updates the dashboard cards instantly.
        try:
            live_data = StatsRepository.get_dashboard_stats()
            for key, val_lbl in self.stat_labels.items():
                if key in live_data:
                    val_lbl.configure(text=live_data[key])
        except Exception as e:
            logger.error(f"Failed to refresh dashboard stats: {e}")

    def create_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_header()

        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BACKGROUND,
            corner_radius=0,
            scrollbar_button_color=theme.PRIMARY,
            scrollbar_button_hover_color=theme.BUTTON_PRIMARY_HOVER,
        )

        self.content.grid(
            row=1, column=0, sticky="nsew", padx=40, pady=25
        )

        self.build_dashboard()

    def build_header(self):
        self.header = ctk.CTkFrame(
            self, height=70, fg_color=theme.PRIMARY, corner_radius=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        left = ctk.CTkFrame(self.header, fg_color="transparent")
        left.pack(side="left", padx=25, pady=10)

        # Safe Logo Image Loader
        BASE_DIR = Path(__file__).resolve().parent.parent
        logo_path = BASE_DIR / "assets" / "icons" / "divera-bank-logo.png"

        try:
            if logo_path.exists():
                image = Image.open(logo_path)
                self.logo = ctk.CTkImage(
                    light_image=image, dark_image=image, size=(36, 36)
                )
                logo = ctk.CTkLabel(left, image=self.logo, text="")
                logo.pack(side="left", padx=(0, 12))
            else:
                logger.warning(f"Logo asset not found at path: {logo_path}")
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

        # Dynamic Logout / Profile Actions container on the right
        right_container = ctk.CTkFrame(self.header, fg_color="transparent")
        right_container.pack(side="right", padx=20, pady=14)

        # Dynamic Profile Page Navigation Button
        profile_btn = ctk.CTkButton(
            right_container,
            text="👤  Admin Profile",
            width=140,
            height=42,
            corner_radius=20,
            fg_color="#1E3A8A",
            hover_color="#2563EB",
            text_color="white",
            font=("Montserrat", 13, "bold"),
            command=self.safe_open_profile,
        )
        profile_btn.pack(side="right")

    def build_dashboard(self):
        title = ctk.CTkLabel(
            self.content,
            text="Dashboard",
            font=fonts.APP_TITLE,
            text_color=theme.PRIMARY,
        )
        title.pack(anchor="w", pady=(0, 5))

        subtitle = ctk.CTkLabel(
            self.content,
            text="Here's today's banking overview.",
            font=fonts.BODY_TEXT,
            text_color=theme.TEXT_SECONDARY,
        )
        subtitle.pack(anchor="w", pady=(0, 25))


        # Dynamic Stat Cards Section
        stats_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(10, 30))

        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)

        card_keys = list(self.stats_data.keys())
        coords = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2)
        ]

        for (row, col), key in zip(coords, card_keys):
            try:
                self.create_stat_card(
                    stats_frame, row, col, key, self.stats_data[key]
                )
            except Exception as e:
                logger.error(f"Failed to render stat card '{key}': {e}")


        # Quick Actions (Centered Layout)
        actions_heading = ctk.CTkLabel(
            self.content,
            text="Quick Actions",
            font=fonts.SECTION_TITLE,
            text_color=theme.PRIMARY,
        )
        actions_heading.pack(anchor="w", pady=(5, 15))

        actions = ctk.CTkFrame(self.content, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 30))

        for col in range(3):
            actions.grid_columnconfigure(col, weight=1)

        customer_btn = ctk.CTkButton(
            actions,
            text="CUSTOMERS",
            width=210,
            height=52,
            corner_radius=14,
            font=("Montserrat", 16, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.safe_open_customer_management,
        )
        customer_btn.grid(row=0, column=0, padx=10, pady=5)

        account_btn = ctk.CTkButton(
            actions,
            text="ACCOUNTS",
            width=210,
            height=52,
            corner_radius=14,
            font=("Montserrat", 16, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.safe_open_account_management,
        )
        account_btn.grid(row=0, column=1, padx=10, pady=5)

        transaction_btn = ctk.CTkButton(
            actions,
            text="TRANSACTIONS",
            width=210,
            height=52,
            corner_radius=14,
            font=("Montserrat", 16, "bold"),
            fg_color=theme.PRIMARY,
            hover_color=theme.BUTTON_PRIMARY_HOVER,
            command=self.safe_open_transaction_management,
        )
        transaction_btn.grid(row=0, column=2, padx=10, pady=5)


        # AI Insights Section
        self.build_ai_insights()

        footer = ctk.CTkLabel(
            self.content,
            text="Version 1.0    © 2026 Divera Bank",
            font=fonts.FOOTER,
            text_color=theme.TEXT_SECONDARY,
        )
        footer.pack(pady=(30, 15))

    def create_stat_card(self, parent, row, column, title, value):
        #Builds card with registered label reference for real-time DB updates.
        try:
            card = ctk.CTkFrame(
                parent,
                width=280,
                height=120,
                fg_color="#FFFFFF",
                corner_radius=16,
                border_width=2,
                border_color=theme.PRIMARY,
            )

            card.grid(
                row=row, column=column, padx=10, pady=10, sticky="nsew"
            )
            card.grid_propagate(False)

            content = ctk.CTkFrame(card, fg_color="transparent")
            content.place(relx=0.5, rely=0.5, anchor="center")

            # Title label rendered first at the top
            title_label = ctk.CTkLabel(
                content,
                text=title,
                font=fonts.BODY_TEXT,
                text_color=theme.TEXT_SECONDARY,
            )
            title_label.pack(pady=(0, 4))

            # Value label rendered underneath with large font
            value_label = ctk.CTkLabel(
                content,
                text=value,
                font=("Montserrat", 30, "bold"),
                text_color=theme.PRIMARY,
            )
            value_label.pack()

            # Reference stored safely for real-time live DB updates
            self.stat_labels[title] = value_label

        except Exception as e:
            logger.error(f"Error creating card '{title}': {e}")

    def update_stat_cards(self, new_data: dict):
        #Updates stat card values safely when DB connects.
        try:
            for title, val in new_data.items():
                if title in self.stat_labels:
                    self.stat_labels[title].configure(text=str(val))
            logger.info("Stat cards updated with fresh database values.")
        except Exception as e:
            logger.error(f"Error updating stat card values: {e}")

    def build_ai_insights(self):
        #AI Insights panel with cached load and on-demand execution.
        try:
            ai_card = ctk.CTkFrame(
                self.content,
                fg_color="white",
                corner_radius=18,
                border_width=2,
                border_color=theme.PRIMARY,
            )
            ai_card.pack(fill="x", pady=(0, 20))

            header = ctk.CTkFrame(
                ai_card,
                fg_color=theme.PRIMARY,
                corner_radius=15,
                height=45,
            )
            header.pack(fill="x", padx=2, pady=2)
            header.pack_propagate(False)

            heading = ctk.CTkLabel(
                header,
                text="🤖 AI Insights & Operational Summary",
                font=fonts.SECTION_TITLE,
                text_color="white",
            )
            heading.pack(side="left", padx=18, pady=10)

            body = ctk.CTkFrame(ai_card, fg_color="transparent")
            body.pack(fill="both", expand=True, padx=20, pady=18)

            summary_title = ctk.CTkLabel(
                body,
                text="Daily Banking Overview",
                font=("Montserrat", 16, "bold"),
                text_color=theme.PRIMARY,
            )
            summary_title.pack(anchor="w", pady=(0, 12))

            # Initial view loads cached text or setup prompt
            self.ai_summary_label = ctk.CTkLabel(
                body,
                text=(
                    "✓ Database offline — initial setup mode active.\n\n"
                    "• MongoDB will aggregate raw transaction metrics into JSON.\n\n"
                    "💡 Add GEMINI_API_KEY to your .env file and click 'Generate Fresh Insights' below to run live analysis."
                ),
                justify="left",
                anchor="w",
                font=fonts.BODY_TEXT,
                wraplength=900,
            )
            self.ai_summary_label.pack(anchor="w")

            btn_frame = ctk.CTkFrame(body, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(20, 5))

            generate_btn = ctk.CTkButton(
                btn_frame,
                text="✨ Generate Fresh Insights",
                width=210,
                height=40,
                corner_radius=10,
                fg_color=theme.PRIMARY,
                hover_color=theme.BUTTON_PRIMARY_HOVER,
                font=fonts.BUTTON,
                command=self.safe_generate_ai_insight,
            )
            generate_btn.pack(side="right", padx=(10, 0))

            view_report_btn = ctk.CTkButton(
                btn_frame,
                text="📄 View Full Report",
                width=160,
                height=40,
                corner_radius=10,
                fg_color="#1E3A8A",
                hover_color="#2563EB",
                font=fonts.BUTTON,
                command=self.safe_open_full_report_modal,
            )
            view_report_btn.pack(side="right")

        except Exception as e:
            logger.error(f"Failed building AI Insights panel: {e}")


    # Event Handlers & Modal
    def safe_generate_ai_insight(self):
        """Triggered on-demand when user clicks 'Generate Fresh Insights'."""
        try:
            logger.info("Initiating on-demand AI insight pipeline...")
            self.ai_summary_label.configure(
                text="⏳ Gathering database counts and querying Gemini AI..."
            )
            # Run in background thread to keep UI completely responsive
            threading.Thread(target=self._fetch_ai_insights_background, daemon=True).start()
        except Exception as e:
            logger.error(f"Error initiating AI generation: {e}")

    def _fetch_ai_insights_background(self):
        try:
            # 1. Grab raw statistics from your dashboard stat cards
            raw_metrics = "Current Dashboard Database Metrics:\n"
            for title, label_widget in self.stat_labels.items():
                raw_metrics += f"- {title}: {label_widget.cget('text')}\n"

            # 2. Sanitize data through security filter
            safe_metrics = AIService.anonymize_data(raw_metrics)

            # 3. Fetch from Gemini
            result = AIService.generate_banking_insights(safe_metrics)
            
            # 4. Update local memory cache
            self.cached_short_summary = result.get("short", "No summary.")
            self.cached_full_report = result.get("full", "No report.")

            # 5. Update UI label safely on main thread
            self.after(0, lambda: self.ai_summary_label.configure(text=self.cached_short_summary))
            logger.info("Fresh AI insights successfully fetched and cached.")
            
        except Exception as e:
            error_msg = f"❌ Failed to fetch insights: {str(e)}"
            self.cached_short_summary = error_msg
            self.after(0, lambda: self.ai_summary_label.configure(text=error_msg))
            logger.error(error_msg)

    def safe_open_full_report_modal(self):
        #Opens popup displaying the detailed analytical report from cache.
        try:
            FullReportModal(self, report_text=self.cached_full_report)
            logger.info("Opened Full Report modal window.")
        except Exception as e:
            logger.error(f"Failed opening Full Report modal: {e}")

    def safe_open_customer_management(self):
        try:
            if callable(self.open_customer_management_callback):
                self.open_customer_management_callback()
            else:
                logger.warning("Customer management callback unassigned.")
        except Exception as e:
            logger.error(f"Navigation error to Customer Management: {e}")

    def safe_open_account_management(self):
            try:
                if callable(self.open_account_management_callback):
                    self.open_account_management_callback()
                else:
                    logger.warning("Account management callback unassigned.")
            except Exception as e:
                logger.error(f"Navigation error to Account Management: {e}")

    def safe_open_transaction_management(self):
        try:
            if callable(self.open_account_management_callback):
                self.open_transaction_management_callback()
            else:
                logger.warning("Transaction management callback unassigned.")
        except Exception as e:
            logger.error(f"Navigation error to Transaction Management: {e}")
            
    def safe_open_profile(self):
        try:
            if callable(self.open_profile_callback):
                self.open_profile_callback()
            else:
                logger.warning("Profile page callback unassigned.")
        except Exception as e:
            logger.error(f"Navigation error to Profile Page: {e}")


# Pop-up Window for Full AI Operational Report
class FullReportModal(ctk.CTkToplevel):

    def __init__(self, parent, report_text):
        super().__init__(parent)

        self.title("Divera Bank — Full AI Operational Intelligence Report")
        self.geometry("750x550")
        self.resizable(False, False)

        # Focus modal window on top
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        heading = ctk.CTkLabel(
            self,
            text="📊 Comprehensive AI Analytical Report",
            font=("Montserrat", 18, "bold"),
            text_color=theme.PRIMARY,
        )
        heading.pack(anchor="w", padx=25, pady=(20, 10))

        self.textbox = ctk.CTkTextbox(
            self,
            font=("Montserrat", 13),
            wrap="word",
            border_width=2,
            border_color=theme.PRIMARY,
            corner_radius=12,
        )
        self.textbox.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        self.textbox.insert("1.0", report_text)
        self.textbox.configure(state="disabled")

        close_btn = ctk.CTkButton(
            self,
            text="Close Report",
            width=140,
            height=38,
            corner_radius=8,
            fg_color=theme.PRIMARY,
            command=self.destroy,
        )
        close_btn.pack(anchor="e", padx=25, pady=(0, 20))