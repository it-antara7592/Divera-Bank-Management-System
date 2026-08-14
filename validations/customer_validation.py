import re
from datetime import datetime


class CustomerValidator:

    @staticmethod
    def validate_first_name(name):
        name_str = name.strip()
        if not name_str:
            return "First Name is required."
        if len(name_str) < 2:
            return "Minimum 2 characters required."
        if len(name_str) > 30:
            return "Maximum 30 characters allowed."
        if not re.fullmatch(r"[A-Za-z ]+", name_str):
            return "Only alphabets are allowed."
        return None

    @staticmethod
    def validate_middle_name(name):
        name_str = name.strip()
        if not name_str:
            return None
        if len(name_str) > 30:
            return "Maximum 30 characters allowed."
        if not re.fullmatch(r"[A-Za-z ]+", name_str):
            return "Only alphabets are allowed."
        return None

    @staticmethod
    def validate_last_name(name):
        name_str = name.strip()
        if not name_str:
            return "Last Name is required."
        if len(name_str) < 2:
            return "Minimum 2 characters required."
        if len(name_str) > 30:
            return "Maximum 30 characters allowed."
        if not re.fullmatch(r"[A-Za-z ]+", name_str):
            return "Only alphabets are allowed."
        return None

    @staticmethod
    def validate_dob(dob):
        if not dob.strip():
            return "Date of Birth is required."
        try:
            birth = datetime.strptime(dob.strip(), "%d/%m/%Y")
        except ValueError:
            return "Format must be DD/MM/YYYY."

        today = datetime.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

        if age < 18:
            return "Customer must be at least 18 years old."
        if age > 120:
            return "Please enter a valid birth date."
        return None

    @staticmethod
    def validate_gender(gender):
        if not gender or gender in ["Select", "Select Gender"]:
            return "Please select a gender."
        return None

    @staticmethod
    def validate_government_id_type(id_type):
        if not id_type or id_type in ["Select", "Select Government ID"]:
            return "Please select a Government ID type."
        return None

    @staticmethod
    def validate_government_id_number(id_type, number):
        num_str = number.strip()
        if not num_str:
            return "Government ID Number is required."

        if id_type == "Aadhaar Card":
            if not re.fullmatch(r"\d{12}", num_str):
                return "Aadhaar must contain exactly 12 digits."
        elif id_type == "PAN Card":
            if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", num_str):
                return "Invalid PAN format (e.g. ABCDE1234F)."
        elif id_type == "Passport":
            if not re.fullmatch(r"[A-Z][0-9]{7}", num_str):
                return "Invalid Passport format."
        elif id_type == "Driving Licence":
            if len(num_str) < 10:
                return "Invalid Driving Licence number."
        elif id_type == "Voter ID":
            if not re.fullmatch(r"[A-Z]{3}[0-9]{7}", num_str):
                return "Invalid Voter ID format."

        return None

    @staticmethod
    def validate_phone(phone):
        if not re.fullmatch(r"[6-9]\d{9}", phone.strip()):
            return "Enter a valid 10-digit phone number."
        return None

    @staticmethod
    def validate_email(email):
        if not email.strip():
            return "Email is required."
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.fullmatch(pattern, email.strip()):
            return "Invalid email address."
        return None

    @staticmethod
    def validate_pincode(pin):
        if not re.fullmatch(r"\d{6}", pin.strip()):
            return "PIN Code must contain 6 digits."
        return None

    @staticmethod
    def validate_address(address):
        if not address.strip():
            return "Address is required."
        if len(address.strip()) > 100:
            return "Maximum 100 characters allowed."
        return None

    @staticmethod
    def validate_state(state):
        if not state or state in ["Select", "Select State"]:
            return "Please select a State."
        return None

    @staticmethod
    def validate_city(city):
        if not city or city in ["Select", "Select City"]:
            return "Please select a City."
        return None