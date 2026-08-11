"""
=========================================================
Divera Banking Management System
Main Application Entry Point
=========================================================
"""
import customtkinter as ctk
from core import theme

# Force Light Mode
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

from services.auth_service import AuthService
from ui.landing_page import LandingPage
from ui.login_page import LoginPage
from ui.dashboard import DashboardPage
from ui.profile_page import ProfilePage
from ui.customers.customer_management import CustomerManagementPage
from ui.customers.customer_form_page import CustomerFormPage
from ui.accounts.account_form_page import AccountFormPage
from ui.password_reset import PasswordResetPage
from ui.accounts.account_management import AccountManagementPage
from ui.accounts.account_list_page import AccountListPage
from ui.customers.customer_list_page import CustomerListPage
from ui.customers.customer_form_update import CustomerUpdateFormPage
from ui.transactions.transaction_management import TransactionManagementPage
from ui.accounts.account_details_page import AccountDetailsPage

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Divera Bank Operations Core")
        self.geometry("1400x800")
        self.minsize(1280, 720)
        self.configure(fg_color=theme.BACKGROUND)

        # Services & State
        self.auth_service = AuthService()
        self.current_user = None

        # Root view container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_dashboard()

    def clear_page(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_landing(self):
        self.clear_page()
        LandingPage(
            parent=self.container,
            on_get_started=self.show_login
        )

    def show_login(self):
        self.clear_page()
        LoginPage(
            parent=self.container,
            auth_service=self.auth_service,
            on_login_success=self.handle_login_success,
            on_forgot_password=self.show_password_reset
        )

    def handle_login_success(self, user_record: dict):
        self.current_user = user_record
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_page()
        DashboardPage(
            parent=self.container,
            current_user=self.current_user,
            on_logout=self.show_landing,
            open_customer_management=self.show_customer_management,
            open_account_management=self.show_account_management,
            open_transaction_management=self.show_transaction_management,
            open_profile=self.show_profile
        )


    def show_profile(self):
        self.clear_page()
        ProfilePage(
            parent=self.container,
            auth_service=self.auth_service,
            current_user=self.current_user,
            on_navigate_dashboard=self.show_dashboard,
            on_open_password_reset=self.show_password_reset,
            on_logout=self.show_landing
        )

    def show_password_reset(self):
        self.clear_page()
        return_callback = self.show_profile if self.current_user else self.show_login
        PasswordResetPage(
            parent=self.container,
            auth_service=self.auth_service,
            current_user=self.current_user,
            on_return_callback=return_callback
        )

    def show_customer_management(self):
        self.clear_page()
        CustomerManagementPage(
            parent=self.container,
            on_back=self.show_dashboard,
            on_create=self.show_customer_form,
            on_view=self.show_customer_list_page
        )
        
        
    def show_customer_form(self):
        self.clear_page()
        CustomerFormPage(
            parent=self.container,
            on_back=self.show_customer_management,
            on_create_account=self.show_account_form
        )

    def show_account_form(self, customer_data=None):
        self.clear_page()
        self.account_page = AccountFormPage(
            parent=self.container,
            on_back=self.show_dashboard,
            prefill_customer=customer_data
        )

    def show_account_management(self):
        self.clear_page()
        AccountManagementPage(
            parent=self.container,
            on_back=self.show_dashboard,
            on_create=self.show_account_form,
            on_view=self.show_account_list_page
        )

        
    def show_customer_update(self,customer_data):
        self.clear_page()
        CustomerUpdateFormPage(
            parent=self.container,
            customer_data=customer_data,
            on_back=self.show_customer_list_page,
            on_success=self.show_customer_list_page  # Navigates back to customer list upon successful save
        )

    def show_customer_list_page(self):
            self.clear_page()
            CustomerListPage(
                parent=self.container,
                on_back=self.show_customer_management,
                on_open_update=self.show_customer_update
            )

    def show_account_list_page(self):
                self.clear_page()
                AccountListPage(
                    parent=self.container,
                    on_back=self.show_account_management,
                    on_open_details=self.show_account_details_page
                )

    def show_account_details_page(self, account_data):
        self.clear_page()
        AccountDetailsPage(
            parent=self.container,
            account_data=account_data,
            on_back=self.show_account_list_page,
            on_refresh_parent=self.show_account_list_page
        )

    def show_transaction_management(self):
            self.clear_page()
            page = TransactionManagementPage(
                parent=self.container,
                on_back=self.show_dashboard,
                on_deposit=None,
                on_withdraw=None,
                on_transfer=None,
                on_history=None,
            )


        

if __name__ == "__main__":
    app = Application()
    app.mainloop()