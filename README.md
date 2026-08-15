# DIVERA BANK 🏦

A desktop-based **Bank Management System** built using **Python, CustomTkinter, and MongoDB Community Server**.

Divera Bank is an academic banking management application designed to simulate the internal administrative operations of a bank. The project combines practical business rules, database management, authentication, customer and account management, transaction processing, security features, and an experimental **AI-assisted insights feature**.

The application follows a **traditional desktop banking management approach**. Rather than attempting to reproduce the navigation patterns of modern web-based banking platforms, Divera Bank is organized around dedicated administrative pages, forms, database records, operational workflows, and rule-based processing.

At the same time, the system introduces selected modern capabilities, particularly **AI-assisted operational analysis and insights**, on top of this traditional foundation.

This creates the core concept of the project:

```text
Traditional Desktop Banking Management
                +
       Modern AI Experimentation
                ↓
          Divera Bank
```

The project therefore explores how a conventional, database-driven banking application can be enhanced with modern software capabilities such as intelligent analysis, automation, improved security, and data-driven insights.


> **Note:** Divera Bank is an academic banking simulation. It does not connect to real banking networks, payment gateways, financial institutions, or real-world banking infrastructure.

---

# 📌 Overview

Divera Bank is an **admin-only banking management system**.

The administrator can:

* Log into the application
* Manage customer records
* Automatically generate Customer IDs
* Create and manage bank accounts
* Automatically generate Account Numbers
* Check account balances
* Perform deposits
* Perform withdrawals
* Perform account-to-account transfers
* Manage Current Account overdrafts
* View transaction history
* Close accounts
* View dashboard statistics
* Manage administrator profile information
* Use an AI-assisted insights and summary feature

The project combines standard banking management functionality with an attempt to introduce a modern AI component into a traditional desktop application.

---

# ✨ Features

## 🔐 Admin Authentication

Divera Bank provides an administrator authentication system.

Features include:

* Admin login
* Password hashing using `bcrypt`
* Predefined administrator credentials for the academic/demo setup
* Password reset functionality
* Authorization/manager verification for sensitive operations
* Input validation
* Logout functionality

Passwords are not stored as plain text in the database. Passwords are protected using hashing.

---

# 👥 Customer Management

Administrators can:

* Create customers
* View customer records
* Search customers
* Update customer information
* Check customer details
* Validate customer information

Customer information includes fields such as:

* Customer ID
* Name
* Email
* Phone number
* Address
* Nationality

## Automatic Customer ID Generation

Customer IDs are generated automatically by the system.

The administrator does not manually assign a Customer ID when creating a customer.

The system uses its database counter mechanism to generate identifiers.

---

# 🏦 Account Management

Divera Bank supports two account types:

* **Savings Account**
* **Current Account**

Administrators can:

* Create accounts
* View account details
* Search/list accounts
* Check account balances
* Manage account information
* Close accounts

## Automatic Account Number Generation

Account numbers are generated automatically by the system.

Administrators do not manually assign account numbers.

---

## Account Ownership Rules

Each customer can have a maximum of:

* **1 Savings Account**
* **1 Current Account**

Therefore, one customer can have:

```text
Customer
   │
   ├── 1 Savings Account
   │
   └── 1 Current Account
```

A customer cannot create multiple Savings Accounts or multiple Current Accounts.

The system validates this rule before allowing a new account to be created.

---

# 🔒 Account Closing

Accounts cannot be permanently deleted from the database.

Instead, an account can be **closed**.

The lifecycle is:

```text
Account Created
      │
      ▼
    ACTIVE
      │
      │ Close Account
      ▼
    CLOSED
      │
      ▼
No further banking operations
```

Once an account is closed:

* The account remains stored in MongoDB
* The account record is preserved
* Its status becomes `CLOSED`
* Deposits are not allowed
* Withdrawals are not allowed
* Transfers are not allowed
* Other banking operations are not allowed

This preserves the account's historical record instead of deleting it.

---

# 💰 Transaction Management

Divera Bank supports the following core banking operations:

## Deposit

Money can be deposited into an eligible account.

The system validates:

* Account existence
* Account status
* Transaction amount
* Applicable banking rules

The account balance is then updated and the transaction is recorded.

---

## Withdrawal

Money can be withdrawn from an eligible account.

The system validates:

* Account existence
* Account status
* Withdrawal amount
* Available balance
* Overdraft rules where applicable

---

## Transfer

The system supports account-to-account transfers.

The system validates:

* Source account
* Destination account
* Source account status
* Destination account status
* Transfer amount
* Same-account transfers
* Available balance
* Overdraft rules where applicable

The source account is debited and the destination account is credited when the transfer is valid.

---

# 💳 Overdraft Facility

Current Accounts support a controlled overdraft facility.

The system checks:

* Current account balance
* Required overdraft amount
* Overdraft limit
* Whether the overdraft facility has already been used

The system prevents a transaction from exceeding the permitted overdraft limit.

The overdraft functionality provides domain-specific banking logic beyond basic CRUD operations.

---

# 📜 Transaction History

The application provides transaction history functionality.

Administrators can view transaction information recorded by the system.

Transaction records can contain information such as:

* Transaction ID
* Account number
* Transaction type
* Amount
* Date/time
* Transaction status
* Related account information where applicable

### Current Limitation

Transaction history **cannot currently be downloaded or exported** into a file format.

CSV/PDF export is considered a possible future enhancement.

---

# 📊 Dashboard

The dashboard provides an overview of the banking system.

It can display information such as:

* Total customers
* Total accounts
* Total transactions
* Account statistics
* Overall system insights

Administrators can also check account/customer balance information through the application.

---

# 🤖 AI-Assisted Insights

One of the experimental aspects of Divera Bank is the integration of **Google GenAI**.

The AI feature provides **overall administrative insights and summaries** based on information available in the banking system.

The AI component is intended to explore how modern AI capabilities can be incorporated into a traditional desktop banking management application.

## What AI Does Not Do

The AI system does not:

* Approve transactions
* Reject transactions
* Move money
* Calculate account balances
* Perform deposits
* Perform withdrawals
* Perform transfers
* Replace banking business logic

Core banking operations remain controlled by deterministic application logic.

The AI component acts as an additional insight layer rather than the core decision-making system.

---

# 🛡️ Security

Security-related functionality implemented in the application includes:

* Admin authentication
* Password hashing using `bcrypt`
* Predefined administrator credentials for the academic/demo setup
* Password reset functionality
* Manager/authorization verification for sensitive operations
* Input validation
* Database uniqueness constraints/indexes
* Account status validation
* Controlled overdraft rules
* Failed transaction logging

---

# 🔑 Demo Credentials

Divera Bank uses predefined administrator credentials for the academic/demo environment.

These credentials are intentionally provided so that the application can be tested without requiring an administrator account to be manually created.

| Credential | Value |
|---|---|
| **Admin ID / Username** | `admin` |
| **Password** | `1234` |
| **Security Reset Code** | `DBMS-RESET-2026` |
| **Transaction Passcode** | `7777` |

> ⚠️ **Important:** These are demonstration credentials for this academic project only. They must not be used for any real banking or production system.

---

# 🔑 Gemini API Configuration

The Gemini API key is **not included with the project**.

Anyone who wants to use the AI-assisted insights feature must create their own `.env` file in the project root and provide their own Gemini API key.

### Example

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace your_gemini_api_key_here with your own Gemini API key.

### ⚠️ Important: The .env file should not be committed to GitHub.

The separation is:

README.md
    │
    └── Predefined demo credentials
        for application login

.env
    │
    └── User's own Gemini API key
        for AI functionality

No Gemini API key is distributed with the project.

---

# 🏗️ System Architecture

Divera Bank follows a modular architecture that separates the graphical interface, business logic, database access, validation, and shared application functionality.

```text
                         ┌──────────────────────┐
                         │      CustomTkinter   │
                         │          UI          │
                         │                      │
                         │ Login                │
                         │ Dashboard            │
                         │ Customers            │
                         │ Accounts             │
                         │ Transactions         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       Services       │
                         │                      │
                         │ Auth                 │
                         │ Customer             │
                         │ Account              │
                         │ Transaction          │
                         │ AI                   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Repositories     │
                         │                      │
                         │ Customer Repository  │
                         │ Account Repository   │
                         │ Transaction Repo     │
                         │ Statistics Repo      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       MongoDB        │
                         │                      │
                         │ customers            │
                         │ accounts             │
                         │ admins               │
                         │ transactions         │
                         │ counters             │
                         └──────────────────────┘

             ┌──────────────────┐
             │    Validations   │
             │                  │
             │ Customer         │
             │ Account          │
             │ Transaction      │
             └──────────────────┘

             ┌──────────────────┐
             │       Core       │
             │                  │
             │ Security         │
             │ Fonts            │
             │ Theme            │
             └──────────────────┘
```

### Architecture Layers

| Layer           | Responsibility                                  |
| --------------- | ----------------------------------------------- |
| `ui/`           | Graphical user interface and user interaction   |
| `services/`     | Application business logic and operations       |
| `repositories/` | Database access and persistence                 |
| `validations/`  | Validation rules for application data           |
| `core/`         | Shared security, fonts, and theme functionality |
| `data/`         | Static/reference data                           |
| `assets/`       | Images and icons                                |

---

# 🗄️ Database

Divera Bank uses **MongoDB Community Server**.

### Database

```text
divera_bank_db
```

### Collections

```text
customers
accounts
admins
transactions
counters
```

### Database Features

The application uses MongoDB for:

* Customer storage
* Account storage
* Administrator information
* Transaction records
* Identifier generation
* Account status management
* Banking statistics

Indexes are used where appropriate, including customer ID and email-related indexes.

The `counters` collection supports automatic identifier generation.

---

# 🛠️ Technology Stack

| Technology                   | Purpose                                 |
| ---------------------------- | --------------------------------------- |
| **Python**                   | Core programming language               |
| **CustomTkinter**            | Desktop graphical user interface        |
| **MongoDB Community Server** | Database                                |
| **PyMongo**                  | Python-MongoDB connectivity             |
| **Pillow (PIL)**             | Image and UI asset handling             |
| **bcrypt**                   | Password hashing                        |
| **python-dotenv**            | Environment variable/API key management |
| **Google GenAI**             | AI-assisted insights                    |
| **Pydantic**                 | Supporting data validation              |
| **Git / GitHub**             | Version control                         |

---

# 📦 Python Dependencies

The project includes a requirements.txt file containing the primary Python dependencies.

Install them using:

pip install -r requirements.txt

The direct dependencies are:

customtkinter==6.0.0
pymongo==4.17.0
pillow==12.3.0
bcrypt==5.0.0
python-dotenv==1.2.2
google-genai==2.18.0

Supporting dependencies are automatically installed by pip when required.

Note: MongoDB Community Server is not a Python package and must be installed separately.

---

# 💻 Requirements

Before running Divera Bank, the following are required:

### Python

Python 3.13 or a compatible Python 3.x installation.

Check your Python version:

```bash
python --version
```

### MongoDB Community Server

MongoDB Community Server must be installed and running locally.

The application connects to MongoDB through **PyMongo**.

### Gemini API Key

A Gemini API key is required only if the AI-assisted insights functionality is being used.

Users must provide their own API key.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd divera-bank
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

## 3. Install Dependencies

The project includes a `requirements.txt` file containing the required Python dependencies.

Install all required packages by running:

```bash
pip install -r requirements.txt
```

This will automatically install the required Python packages and their supporting dependencies.

Supporting dependencies will be installed automatically by pip where required.

## 4. Configure Gemini API

The Gemini API key is not included in the project.

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own Gemini API key.

The `.env` file should not be committed to GitHub.

## 5. Start MongoDB

Make sure **MongoDB Community Server** is installed and running.

## 6. Run the Application

```bash
python main.py
```

---

# 📁 Project Structure

```text
divera-bank/
│
├── assets/
│   ├── icons/
│   └── images/
│
├── core/
│   ├── fonts.py
│   ├── security.py
│   └── theme.py
│
├── data/
│   └── india_location.py
│
├── repositories/
│   ├── account_repository.py
│   ├── customer_repository.py
│   ├── stats_repository.py
│   └── transaction_repository.py
│
├── services/
│   ├── account_service.py
│   ├── ai_service.py
│   ├── auth_service.py
│   ├── customer_service.py
│   └── transaction_service.py
│
├── ui/
│   ├── accounts/
│   │   ├── account_details_page.py
│   │   ├── account_form_page.py
│   │   ├── account_list_page.py
│   │   └── account_management.py
│   │
│   ├── components/
│   │   └── dialogs.py
│   │
│   ├── customers/
│   │   ├── customer_form_page.py
│   │   ├── customer_form_update.py
│   │   ├── customer_list_page.py
│   │   └── customer_management.py
│   │
│   ├── transactions/
│   │   ├── deposit_funds.py
│   │   ├── funds_transfer.py
│   │   ├── transaction_history.py
│   │   ├── transaction_management.py
│   │   └── withdraw_funds.py
│   │
│   ├── dashboard.py
│   ├── landing_page.py
│   ├── login_page.py
│   ├── password_reset.py
│   └── profile_page.py
│
├── validations/
│   ├── account_validation.py
│   ├── customer_validation.py
│   └── transaction_validation.py
│
├── .gitignore
├── .env
├── requirements.txt
├── db.py
├── main.py
└── README.md
```

## Directory Responsibilities

| Directory       | Purpose                                         |
| --------------- | ----------------------------------------------- |
| `assets/`       | Application icons and images                    |
| `core/`         | Shared security, fonts, and theme functionality |
| `data/`         | Static/reference data used by the application   |
| `repositories/` | Database access and data persistence            |
| `services/`     | Business logic and application services         |
| `ui/`           | CustomTkinter graphical interface               |
| `validations/`  | Customer, account, and transaction validation   |

### Important Files

**`main.py`**
The main entry point used to launch the application.

**`db.py`**
Handles the MongoDB connection and database-related initialization.

**`services/ai_service.py`**
Handles AI-related functionality.

**`core/security.py`**
Contains shared security-related functionality.

**`.env`**
Contains the user's own Gemini API key when AI functionality is used.

---

# 🔄 Core Banking Operations

## Deposit

```text
Validate account
      ↓
Validate account status
      ↓
Validate amount
      ↓
Update account balance
      ↓
Record transaction
```

## Withdrawal

```text
Validate account
      ↓
Validate account status
      ↓
Validate amount
      ↓
Check available balance
      ↓
Check overdraft rules
      ↓
Update account balance
      ↓
Record transaction
```

## Transfer

```text
Validate source account
        ↓
Validate destination account
        ↓
Validate account status
        ↓
Prevent same-account transfer
        ↓
Check balance / overdraft
        ↓
Debit source account
        ↓
Credit destination account
        ↓
Record transaction
```

---

# 💳 Overdraft Logic

For a Current Account, the system determines whether a transaction can use the available overdraft facility.

Conceptually:

```text
Amount <= Balance
       │
       ▼
Normal transaction


Amount > Balance
       │
       ▼
Calculate required overdraft
       │
       ▼
Check overdraft limit
       │
       ▼
Check whether overdraft was already used
       │
       ├── Valid → Allow transaction
       │
       └── Invalid → Reject transaction
```

The overdraft facility is controlled by application business rules.

---

# 🔒 Account Lifecycle

Accounts are not deleted.

Instead, an account can transition from active to closed:

```text
              ┌─────────────┐
              │   CREATED   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   ACTIVE    │
              └──────┬──────┘
                     │
                Close Account
                     │
                     ▼
              ┌─────────────┐
              │   CLOSED    │
              └─────────────┘
                     │
                     ▼
             No further operations
```

The closed account remains in the database to preserve its record.

---

## 🎨 User Interface

Divera Bank uses **CustomTkinter** for its desktop graphical interface.

The interface includes:

- Landing page
- Login page
- Dashboard
- Customer management
- Account management
- Transaction management
- Profile page
- Password reset
- Dialogs and confirmation prompts

The visual design uses the Divera Bank branding, typography, icons, and image assets.

--- 

## ⌨️ Keyboard Shortcuts

Divera Bank provides keyboard shortcuts for quickly navigating between the main management sections of the application.

| Shortcut | Action |
|---|---|
| `Ctrl + Q` | Open Dashboard |
| `Ctrl + W` | Open Customer Management |
| `Ctrl + E` | Open Transaction Management |
| `Ctrl + A` | Open Account Management |

These shortcuts provide a faster way to move between the major sections without requiring the administrator to navigate through multiple pages manually.

The keyboard shortcuts also complement the application's traditional desktop-oriented workflow by providing direct keyboard-based access to frequently used management modules.

--- 

### Design Approach

The interface combines a **traditional desktop application workflow** with a clean and consistent visual design.

The application does not attempt to replicate a modern web-based banking platform with persistent navigation, highly interconnected pages, or enterprise-style interaction patterns. Instead, each major banking operation is organized into dedicated functional pages and workflows.

The visual design is intentionally polished through consistent branding, typography, spacing, colors, buttons, cards, and structured layouts.

This creates the following concept:

```text
Traditional Desktop Workflow
            +
     Modern Visual Design
            +
      AI-Assisted Analysis
            │
            ▼
       Divera Bank
```

---

# 🧠 Project Philosophy

Divera Bank is a **creative academic experiment** that explores the evolution of traditional database-driven software toward more intelligent and user-centered applications.

Rather than attempting to build a production-grade or enterprise-level banking platform, the project starts from a traditional banking-management approach consisting of:

- Forms
- Database records
- Rule-based processing
- Administrative workflows
- CRUD operations
- Business logic

The system follows a **traditional desktop application workflow**, where different banking operations are organized into dedicated functional pages rather than a highly interconnected modern web-style interface.

A clean visual design and consistent branding are used to improve the presentation and usability of this traditional workflow.

An AI-assisted insights feature is then added as a modern layer on top of this traditional foundation.

The purpose is to explore the question:

> **What would happen if a traditional banking management system were extended with modern AI capabilities?**

This approach also provides an opportunity to understand how software can evolve beyond purely functional, database-driven systems.

Through the project, it becomes possible to observe the value of capabilities commonly associated with modern software, such as:

- Improved user experience
- Automation
- Intelligent assistance
- Advanced analytics
- Data-driven decision support
- Stronger security
- More efficient workflows
- Greater system integration

Therefore, Divera Bank is not intended to claim that its interface or architecture represents modern enterprise banking software. Instead, it is a **creative attempt to explore software evolution by deliberately combining a traditional desktop banking-management application with modern visual design and AI-assisted analysis**.

---

# ⚠️ Project Limitations

Divera Bank is an academic banking simulation and is not intended for production banking environments.

The current system does not provide:

* Real banking transactions
* Online banking
* Payment gateway integration
* ATM integration
* Real customer login
* Inter-bank transfers
* Real financial institution connectivity
* Enterprise-grade deployment
* Production banking infrastructure
* Transaction history download/export
* CSV transaction reports
* PDF transaction reports
* Permanent account deletion

Accounts are closed rather than deleted so that their records remain available in the database.

---

# 🔮 Future Enhancements

Possible future improvements include:

* Transaction history export to CSV
* Transaction history export to PDF
* Advanced audit logging
* Role-based access control
* Multi-factor authentication
* Advanced transaction monitoring
* Fraud detection
* AI-powered anomaly detection
* More advanced financial analytics
* Automated reporting
* Stronger multi-document transaction consistency
* Database backup and recovery
* Comprehensive automated testing
* Production-grade deployment

---

# 👨‍💻 Development

Divera Bank was developed with emphasis on:

* Python programming
* Object-oriented programming
* Modular software architecture
* MongoDB database design
* CustomTkinter GUI development
* CRUD operations combined with business logic
* Authentication and password security
* Banking transaction processing
* Account lifecycle management
* Overdraft handling
* Automatic identifier generation
* Input validation
* AI experimentation

---

# 📚 Academic Purpose

Divera Bank demonstrates how a banking management workflow can be implemented as a desktop application while combining:

**GUI + Business Logic + Database + Security + Banking Rules + AI**

Although the system contains CRUD functionality, it also implements domain-specific banking rules and application logic, including:

* Automatic Customer ID generation
* Automatic Account Number generation
* One Savings Account per customer
* One Current Account per customer
* Account status management
* Closed account preservation
* Balance checking
* Deposit processing
* Withdrawal processing
* Account transfers
* Overdraft handling
* Transaction validation
* Failed transaction tracking
* Password hashing
* Administrative authorization

The AI-assisted insights feature represents an attempt to introduce a modern technology element into a conventional desktop banking management application.

---

# 📄 License

This project was developed for academic and educational purposes.

---

# 👤 Author

**Divera Bank Management System** by **Antara**

Academic Project — 2026



